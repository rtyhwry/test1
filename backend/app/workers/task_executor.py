"""
Task executor worker - handles test execution
"""
import asyncio
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

from app.workers.celery_app import celery_app
from app.core.config import settings


@celery_app.task(bind=True, max_retries=3)
def execute_test_task(self, task_id: str, execution_id: str) -> Dict:
    """
    Execute a test task
    
    Steps:
    1. Get task configuration
    2. Prepare environment (upgrade if needed)
    3. Pull test code from GitLab
    4. Execute test cases
    5. Collect results
    6. Generate report
    """
    try:
        result = asyncio.run(_execute_task_async(task_id, execution_id))
        return result
    except Exception as e:
        # Retry on failure
        raise self.retry(exc=e, countdown=60)


async def _execute_task_async(task_id: str, execution_id: str) -> Dict:
    """Async task execution logic"""
    from app.core.database import async_session_factory
    from app.models.task import TestTask, TaskExecution, TestCaseResult
    from app.models.environment import Environment, TestHost
    from app.models.test_suite import TestSuite, TestCase
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    async with async_session_factory() as db:
        # Get task and execution
        task_result = await db.execute(
            select(TestTask)
            .where(TestTask.id == UUID(task_id))
            .options(selectinload(TestTask.suite))
        )
        task = task_result.scalar_one_or_none()
        
        exec_result = await db.execute(
            select(TaskExecution)
            .where(TaskExecution.id == UUID(execution_id))
            .options(
                selectinload(TaskExecution.environment),
            )
        )
        execution = exec_result.scalar_one_or_none()
        
        if not task or not execution:
            return {"success": False, "error": "Task or execution not found"}
        
        # Update status
        execution.status = "preparing"
        await db.commit()
        
        # Get test host info
        host = None
        if execution.host_id:
            host_result = await db.execute(
                select(TestHost).where(TestHost.id == execution.host_id)
            )
            host = host_result.scalar_one_or_none()
        
        if not host:
            execution.status = "failed"
            execution.error_message = "Test host not found"
            await db.commit()
            return {"success": False, "error": "Test host not found"}
        
        try:
            # Step 1: Upgrade if needed
            if task.need_upgrade:
                execution.status = "upgrading"
                await db.commit()
                
                upgrade_result = await _upgrade_device(
                    task, execution, host, db
                )
                if not upgrade_result["success"]:
                    raise Exception(upgrade_result["error"])
                
                execution.software_version = task.target_version
                execution.upgraded_from = upgrade_result.get("old_version")
            
            # Step 2: Pull test code
            execution.status = "pulling"
            await db.commit()
            
            if task.suite and task.suite.git_repo:
                pull_result = await _pull_test_code(
                    task.suite, host, db
                )
                if not pull_result["success"]:
                    raise Exception(pull_result["error"])
                
                execution.git_repo = task.suite.git_repo
                execution.git_branch = task.suite.git_branch
                execution.git_commit = pull_result.get("commit")
            
            # Step 3: Get test cases
            cases_to_run = await _get_test_cases(task, db)
            execution.total_cases = len(cases_to_run)
            
            # Step 4: Execute tests
            execution.status = "running"
            await db.commit()
            
            results = await _run_tests(
                cases_to_run, task.suite, host, task, execution, db
            )
            
            # Step 5: Calculate statistics
            passed = sum(1 for r in results if r["status"] == "passed")
            failed = sum(1 for r in results if r["status"] == "failed")
            skipped = sum(1 for r in results if r["status"] == "skipped")
            error = sum(1 for r in results if r["status"] == "error")
            
            execution.passed_cases = passed
            execution.failed_cases = failed
            execution.skipped_cases = skipped
            execution.error_cases = error
            
            # Step 6: Save case results
            for r in results:
                case_result = TestCaseResult(
                    execution_id=execution.id,
                    case_id=r.get("case_id"),
                    case_name=r.get("case_name"),
                    status=r.get("status"),
                    started_at=r.get("started_at"),
                    finished_at=r.get("finished_at"),
                    duration=r.get("duration"),
                    error_message=r.get("error_message"),
                    error_stack=r.get("error_stack"),
                    logs=r.get("logs")
                )
                db.add(case_result)
            
            # Update final status
            execution.status = "success" if failed == 0 and error == 0 else "failed"
            execution.finished_at = datetime.now(timezone.utc)
            execution.duration = int(
                (execution.finished_at - execution.started_at).total_seconds()
            )
            
            # Update task status
            task.status = execution.status
            task.finished_at = execution.finished_at
            
            # Release environment
            if execution.environment:
                execution.environment.status = "idle"
                execution.environment.current_task_id = None
            
            await db.commit()
            
            # Trigger report generation
            generate_report.delay(str(execution.id))
            
            return {
                "success": True,
                "execution_id": str(execution.id),
                "total": len(results),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "error": error
            }
            
        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.finished_at = datetime.now(timezone.utc)
            
            task.status = "failed"
            task.finished_at = execution.finished_at
            
            # Release environment
            if execution.environment:
                execution.environment.status = "idle"
                execution.environment.current_task_id = None
            
            await db.commit()
            
            return {"success": False, "error": str(e)}


async def _upgrade_device(task, execution, host, db) -> Dict:
    """Upgrade device firmware/software"""
    # TODO: Implement actual upgrade logic
    # 1. Download artifact from repository
    # 2. Connect to device via SSH/CAN/UDS
    # 3. Flash firmware
    # 4. Verify version
    
    return {"success": True, "old_version": "1.0.0"}


async def _pull_test_code(suite, host, db) -> Dict:
    """Pull test code from GitLab to test host"""
    # TODO: Implement actual git pull via SSH
    # 1. SSH to host
    # 2. Clone/pull repository
    # 3. Checkout branch
    
    return {"success": True, "commit": "abc123def"}


async def _get_test_cases(task, db) -> List:
    """Get test cases to execute"""
    from app.models.test_suite import TestCase
    from sqlalchemy import select
    
    query = select(TestCase).where(TestCase.suite_id == task.suite_id)
    
    # Filter by case_ids if specified
    if task.case_ids:
        query = query.where(TestCase.id.in_([UUID(c) for c in task.case_ids]))
    
    # Apply case filter
    if task.case_filter:
        if task.case_filter.get("priority"):
            query = query.where(
                TestCase.priority.in_(task.case_filter["priority"])
            )
        if task.case_filter.get("tags"):
            # JSONB contains check for tags
            pass
    
    query = query.where(TestCase.status == "active")
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def _run_tests(cases, suite, host, task, execution, db) -> List[Dict]:
    """Execute test cases on test host"""
    results = []
    
    for case in cases:
        case_result = {
            "case_id": str(case.id),
            "case_name": case.name,
            "started_at": datetime.now(timezone.utc),
        }
        
        try:
            # TODO: Execute actual test via SSH
            # 1. SSH to host
            # 2. Run pytest/robot command
            # 3. Collect output
            
            # Simulated execution
            case_result["status"] = "passed"
            case_result["duration"] = 1000  # ms
            
        except Exception as e:
            case_result["status"] = "error"
            case_result["error_message"] = str(e)
        
        case_result["finished_at"] = datetime.now(timezone.utc)
        results.append(case_result)
    
    return results


@celery_app.task
def generate_report(execution_id: str) -> Dict:
    """Generate test report for an execution"""
    return asyncio.run(_generate_report_async(execution_id))


async def _generate_report_async(execution_id: str) -> Dict:
    """Async report generation"""
    from app.core.database import async_session_factory
    from app.models.task import TaskExecution
    from app.models.report import TestReport
    from sqlalchemy import select
    
    async with async_session_factory() as db:
        result = await db.execute(
            select(TaskExecution).where(TaskExecution.id == UUID(execution_id))
        )
        execution = result.scalar_one_or_none()
        
        if not execution:
            return {"success": False, "error": "Execution not found"}
        
        # Create report
        total_executed = (
            execution.passed_cases + 
            execution.failed_cases + 
            execution.error_cases
        )
        pass_rate = 0.0
        if total_executed > 0:
            pass_rate = round(execution.passed_cases / total_executed * 100, 2)
        
        report = TestReport(
            execution_id=execution.id,
            task_id=execution.task_id,
            report_name=f"Test Report - Execution #{execution.execution_number}",
            report_type="execution",
            total_cases=execution.total_cases,
            passed=execution.passed_cases,
            failed=execution.failed_cases,
            skipped=execution.skipped_cases,
            error=execution.error_cases,
            pass_rate=pass_rate,
            duration=execution.duration,
            environment_info={
                "host_id": str(execution.host_id) if execution.host_id else None,
                "environment_id": str(execution.environment_id) if execution.environment_id else None,
                "software_version": execution.software_version
            }
        )
        
        db.add(report)
        await db.commit()
        
        return {"success": True, "report_id": str(report.id)}


@celery_app.task
def check_scheduled_tasks():
    """Check and trigger scheduled tasks"""
    return asyncio.run(_check_scheduled_tasks_async())


async def _check_scheduled_tasks_async():
    """Check for due tasks and trigger them"""
    from app.core.database import async_session_factory
    from app.services.scheduler_service import SchedulerService
    
    async with async_session_factory() as db:
        scheduler = SchedulerService(db)
        due_tasks = await scheduler.get_due_tasks()
        
        for task in due_tasks:
            # Submit task for execution
            execute_test_task.delay(str(task.id), None)
        
        return {"triggered": len(due_tasks)}


@celery_app.task
def cleanup_old_logs():
    """Cleanup old logs and reports"""
    # TODO: Implement log cleanup logic
    return {"cleaned": 0}
