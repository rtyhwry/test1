"""
Task Service - Business logic for test task management
"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.task import TestTask, TaskExecution, TestCaseResult
from app.models.environment import Environment
from app.models.test_suite import TestSuite, TestCase
from app.schemas.task import TestTaskCreate, TaskStatistics


class TaskService:
    """Service for managing test tasks"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_task_by_id(self, task_id: UUID) -> Optional[TestTask]:
        """Get task by ID with related data"""
        result = await self.db.execute(
            select(TestTask)
            .where(TestTask.id == task_id)
            .options(
                selectinload(TestTask.executions),
                selectinload(TestTask.suite),
                selectinload(TestTask.environment)
            )
        )
        return result.scalar_one_or_none()
    
    async def create_task(
        self,
        task_data: TestTaskCreate,
        created_by: UUID
    ) -> TestTask:
        """Create a new test task"""
        task = TestTask(
            name=task_data.name,
            description=task_data.description,
            project_id=task_data.project_id,
            source="manual",
            trigger_type=task_data.trigger_type,
            schedule_time=task_data.schedule_time,
            cron_expression=task_data.cron_expression,
            priority=task_data.priority,
            need_upgrade=task_data.need_upgrade,
            suite_id=task_data.test_config.suite_id,
            created_by=created_by
        )
        
        # Handle version config
        if task_data.version_config:
            task.version_strategy = task_data.version_config.strategy
            task.target_version = task_data.version_config.version
        
        # Handle env config
        if task_data.env_config:
            task.env_strategy = task_data.env_config.strategy
            task.environment_id = task_data.env_config.environment_id
            task.env_requirements = task_data.env_config.requirements
        
        # Handle test config
        if task_data.test_config.case_ids:
            task.case_ids = [str(c) for c in task_data.test_config.case_ids]
        task.case_filter = task_data.test_config.case_filter
        
        # Handle execution config
        if task_data.execution_config:
            task.timeout = task_data.execution_config.timeout
            task.retry_on_failure = task_data.execution_config.retry_on_failure
            task.max_retries = task_data.execution_config.max_retries
            task.parallel_count = task_data.execution_config.parallel_count
        
        # Handle notify config
        if task_data.notify_config:
            task.notify_config = task_data.notify_config.model_dump()
        
        # Set initial status
        if task.trigger_type == "immediate":
            task.status = "queued"
            task.queued_at = datetime.now(timezone.utc)
        else:
            task.status = "pending"
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def start_task(self, task_id: UUID) -> TaskExecution:
        """Start task execution"""
        task = await self.get_task_by_id(task_id)
        if not task:
            raise ValueError("Task not found")
        
        if task.status not in ["pending", "queued"]:
            raise ValueError(f"Cannot start task in '{task.status}' status")
        
        # Find available environment
        environment = await self._find_available_environment(task)
        if not environment:
            raise ValueError("No available environment")
        
        # Create execution record
        execution_number = len(task.executions) + 1
        execution = TaskExecution(
            task_id=task.id,
            execution_number=execution_number,
            environment_id=environment.id,
            host_id=environment.host_id,
            status="preparing",
            started_at=datetime.now(timezone.utc)
        )
        
        # Update task and environment status
        task.status = "running"
        task.started_at = datetime.now(timezone.utc)
        environment.status = "busy"
        environment.current_task_id = task.id
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        return execution
    
    async def complete_task(
        self,
        execution_id: UUID,
        success: bool,
        results: List[dict]
    ) -> TaskExecution:
        """Complete task execution"""
        result = await self.db.execute(
            select(TaskExecution)
            .where(TaskExecution.id == execution_id)
            .options(selectinload(TaskExecution.task))
        )
        execution = result.scalar_one_or_none()
        
        if not execution:
            raise ValueError("Execution not found")
        
        # Update execution statistics
        execution.finished_at = datetime.now(timezone.utc)
        execution.duration = int(
            (execution.finished_at - execution.started_at).total_seconds()
        )
        execution.status = "success" if success else "failed"
        
        # Calculate statistics
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        error = sum(1 for r in results if r.get("status") == "error")
        
        execution.total_cases = len(results)
        execution.passed_cases = passed
        execution.failed_cases = failed
        execution.skipped_cases = skipped
        execution.error_cases = error
        
        # Save case results
        for r in results:
            case_result = TestCaseResult(
                execution_id=execution.id,
                case_id=r.get("case_id"),
                case_name=r.get("case_name"),
                status=r.get("status"),
                duration=r.get("duration"),
                error_message=r.get("error_message"),
                error_stack=r.get("error_stack"),
                logs=r.get("logs")
            )
            self.db.add(case_result)
        
        # Update task status
        task = execution.task
        task.status = "success" if success else "failed"
        task.finished_at = datetime.now(timezone.utc)
        
        # Release environment
        if execution.environment_id:
            env_result = await self.db.execute(
                select(Environment).where(Environment.id == execution.environment_id)
            )
            environment = env_result.scalar_one_or_none()
            if environment:
                environment.status = "idle"
                environment.current_task_id = None
        
        await self.db.commit()
        await self.db.refresh(execution)
        
        return execution
    
    async def _find_available_environment(
        self,
        task: TestTask
    ) -> Optional[Environment]:
        """Find an available environment for the task"""
        if task.env_strategy == "specific" and task.environment_id:
            # Use specified environment
            result = await self.db.execute(
                select(Environment)
                .where(
                    and_(
                        Environment.id == task.environment_id,
                        Environment.status == "idle"
                    )
                )
            )
            return result.scalar_one_or_none()
        
        # Auto-select environment
        query = select(Environment).where(
            and_(
                Environment.status == "idle",
                Environment.project_id == task.project_id
            )
        )
        
        # Apply requirements filter if specified
        requirements = task.env_requirements or {}
        
        if requirements.get("device_type"):
            # Filter by device type capability
            pass  # TODO: Implement capability matching
        
        query = query.order_by(Environment.updated_at).limit(1)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_task_statistics(self, task_id: UUID) -> TaskStatistics:
        """Get task execution statistics"""
        task = await self.get_task_by_id(task_id)
        
        if not task or not task.executions:
            return TaskStatistics()
        
        latest = task.executions[0]
        
        return TaskStatistics(
            total_cases=latest.total_cases,
            passed=latest.passed_cases,
            failed=latest.failed_cases,
            skipped=latest.skipped_cases,
            error=latest.error_cases,
            pass_rate=latest.pass_rate
        )
