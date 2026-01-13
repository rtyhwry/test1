"""
Test Task API endpoints
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user, get_pagination, require_permission
from app.core.security import Permission
from app.models.user import User
from app.models.task import TestTask, TaskExecution, TestCaseResult
from app.schemas.task import (
    TestTaskCreate,
    TestTaskUpdate,
    TestTaskResponse,
    TestTaskListResponse,
    TaskExecutionResponse,
    TestCaseResultResponse,
    TaskAction,
    TaskStatistics,
)
from app.schemas.common import APIResponse, PaginatedResponse, PaginationParams


router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedResponse[TestTaskListResponse]])
async def list_tasks(
    pagination: PaginationParams = Depends(get_pagination),
    project_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    trigger_type: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    created_by: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_READ))
):
    """
    List all test tasks with pagination and filters
    """
    query = select(TestTask).options(selectinload(TestTask.executions))
    count_query = select(func.count(TestTask.id))
    
    # Apply filters
    if project_id:
        query = query.where(TestTask.project_id == project_id)
        count_query = count_query.where(TestTask.project_id == project_id)
    
    if status:
        query = query.where(TestTask.status == status)
        count_query = count_query.where(TestTask.status == status)
    
    if trigger_type:
        query = query.where(TestTask.trigger_type == trigger_type)
        count_query = count_query.where(TestTask.trigger_type == trigger_type)
    
    if source:
        query = query.where(TestTask.source == source)
        count_query = count_query.where(TestTask.source == source)
    
    if created_by:
        query = query.where(TestTask.created_by == created_by)
        count_query = count_query.where(TestTask.created_by == created_by)
    
    if start_date:
        query = query.where(TestTask.created_at >= start_date)
        count_query = count_query.where(TestTask.created_at >= start_date)
    
    if end_date:
        query = query.where(TestTask.created_at <= end_date)
        count_query = count_query.where(TestTask.created_at <= end_date)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(TestTask.created_at.desc())
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    items = []
    for task in tasks:
        response = TestTaskListResponse.model_validate(task)
        # Calculate statistics from latest execution
        if task.executions:
            latest = task.executions[0]
            response.statistics = TaskStatistics(
                total_cases=latest.total_cases,
                passed=latest.passed_cases,
                failed=latest.failed_cases,
                skipped=latest.skipped_cases,
                error=latest.error_cases,
                pass_rate=latest.pass_rate
            )
        items.append(response)
    
    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
    )


@router.post("", response_model=APIResponse[TestTaskResponse], status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TestTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TASK_CREATE))
):
    """
    Create a new test task
    """
    task = TestTask(
        name=task_in.name,
        description=task_in.description,
        project_id=task_in.project_id,
        source="manual",
        trigger_type=task_in.trigger_type,
        schedule_time=task_in.schedule_time,
        cron_expression=task_in.cron_expression,
        priority=task_in.priority,
        need_upgrade=task_in.need_upgrade,
        version_strategy=task_in.version_config.strategy if task_in.version_config else None,
        target_version=task_in.version_config.version if task_in.version_config else None,
        env_strategy=task_in.env_config.strategy if task_in.env_config else "auto",
        environment_id=task_in.env_config.environment_id if task_in.env_config else None,
        env_requirements=task_in.env_config.requirements if task_in.env_config else {},
        suite_id=task_in.test_config.suite_id,
        case_ids=[str(c) for c in task_in.test_config.case_ids] if task_in.test_config.case_ids else None,
        case_filter=task_in.test_config.case_filter,
        parallel_count=task_in.execution_config.parallel_count if task_in.execution_config else 1,
        timeout=task_in.execution_config.timeout if task_in.execution_config else 3600,
        retry_on_failure=task_in.execution_config.retry_on_failure if task_in.execution_config else False,
        max_retries=task_in.execution_config.max_retries if task_in.execution_config else 1,
        notify_config=task_in.notify_config.model_dump() if task_in.notify_config else {},
        created_by=current_user.id
    )
    
    # Set status based on trigger type
    if task.trigger_type == "immediate":
        task.status = "queued"
        task.queued_at = datetime.now(timezone.utc)
    else:
        task.status = "pending"
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    # TODO: If immediate, submit to task queue for execution
    
    return APIResponse(data=TestTaskResponse.model_validate(task))


@router.get("/{task_id}", response_model=APIResponse[TestTaskResponse])
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_READ))
):
    """
    Get test task by ID
    """
    result = await db.execute(
        select(TestTask)
        .where(TestTask.id == task_id)
        .options(
            selectinload(TestTask.executions),
            selectinload(TestTask.suite),
            selectinload(TestTask.environment)
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    response = TestTaskResponse.model_validate(task)
    
    # Add statistics from latest execution
    if task.executions:
        latest = task.executions[0]
        response.statistics = TaskStatistics(
            total_cases=latest.total_cases,
            passed=latest.passed_cases,
            failed=latest.failed_cases,
            skipped=latest.skipped_cases,
            error=latest.error_cases,
            pass_rate=latest.pass_rate
        )
    
    return APIResponse(data=response)


@router.put("/{task_id}", response_model=APIResponse[TestTaskResponse])
async def update_task(
    task_id: UUID,
    task_in: TestTaskUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_UPDATE))
):
    """
    Update test task (only pending tasks can be updated)
    """
    result = await db.execute(select(TestTask).where(TestTask.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.status not in ["pending", "queued"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending or queued tasks can be updated"
        )
    
    update_data = task_in.model_dump(exclude_unset=True)
    
    # Handle nested configs
    if "version_config" in update_data and update_data["version_config"]:
        vc = update_data.pop("version_config")
        task.version_strategy = vc.get("strategy")
        task.target_version = vc.get("version")
    
    if "env_config" in update_data and update_data["env_config"]:
        ec = update_data.pop("env_config")
        task.env_strategy = ec.get("strategy", "auto")
        task.environment_id = ec.get("environment_id")
        task.env_requirements = ec.get("requirements", {})
    
    if "execution_config" in update_data and update_data["execution_config"]:
        exc = update_data.pop("execution_config")
        task.timeout = exc.get("timeout", 3600)
        task.retry_on_failure = exc.get("retry_on_failure", False)
        task.max_retries = exc.get("max_retries", 1)
        task.parallel_count = exc.get("parallel_count", 1)
    
    if "notify_config" in update_data and update_data["notify_config"]:
        task.notify_config = update_data.pop("notify_config")
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    return APIResponse(data=TestTaskResponse.model_validate(task))


@router.delete("/{task_id}", response_model=APIResponse)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_DELETE))
):
    """
    Delete test task
    """
    result = await db.execute(select(TestTask).where(TestTask.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete running task"
        )
    
    await db.delete(task)
    await db.commit()
    
    return APIResponse(message="Task deleted successfully")


@router.post("/{task_id}/actions", response_model=APIResponse)
async def task_action(
    task_id: UUID,
    action_in: TaskAction,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TASK_EXECUTE))
):
    """
    Perform action on task (start, stop, cancel, retry)
    """
    result = await db.execute(select(TestTask).where(TestTask.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    action = action_in.action
    
    if action == "start":
        if task.status not in ["pending", "queued"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start task in '{task.status}' status"
            )
        task.status = "queued"
        task.queued_at = datetime.now(timezone.utc)
        # TODO: Submit to task queue
        
    elif action == "stop":
        if task.status != "running":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is not running"
            )
        task.status = "cancelled"
        task.finished_at = datetime.now(timezone.utc)
        # TODO: Send stop signal to executor
        
    elif action == "cancel":
        if task.status in ["success", "failed", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task already completed"
            )
        task.status = "cancelled"
        task.finished_at = datetime.now(timezone.utc)
        
    elif action == "retry":
        if task.status not in ["failed", "cancelled", "timeout"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only failed/cancelled tasks can be retried"
            )
        task.status = "queued"
        task.queued_at = datetime.now(timezone.utc)
        task.started_at = None
        task.finished_at = None
        # TODO: Submit to task queue
    
    await db.commit()
    
    return APIResponse(message=f"Action '{action}' executed successfully")


@router.get("/{task_id}/executions", response_model=APIResponse[list[TaskExecutionResponse]])
async def list_task_executions(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_READ))
):
    """
    List all executions for a task
    """
    result = await db.execute(
        select(TaskExecution)
        .where(TaskExecution.task_id == task_id)
        .order_by(TaskExecution.execution_number.desc())
    )
    executions = result.scalars().all()
    
    return APIResponse(
        data=[TaskExecutionResponse.model_validate(e) for e in executions]
    )


@router.get("/{task_id}/executions/{execution_id}/results", response_model=APIResponse[list[TestCaseResultResponse]])
async def list_execution_results(
    task_id: UUID,
    execution_id: UUID,
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_READ))
):
    """
    List case results for an execution
    """
    query = select(TestCaseResult).where(TestCaseResult.execution_id == execution_id)
    
    if status:
        query = query.where(TestCaseResult.status == status)
    
    query = query.order_by(TestCaseResult.started_at)
    
    result = await db.execute(query)
    results = result.scalars().all()
    
    return APIResponse(
        data=[TestCaseResultResponse.model_validate(r) for r in results]
    )


@router.get("/{task_id}/logs")
async def get_task_logs(
    task_id: UUID,
    execution_id: Optional[UUID] = Query(None),
    level: Optional[str] = Query(None),
    limit: int = Query(default=100, le=1000),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_READ))
):
    """
    Get task execution logs
    """
    # TODO: Implement log retrieval from storage
    return APIResponse(
        data={
            "logs": [],
            "message": "Log retrieval not implemented"
        }
    )
