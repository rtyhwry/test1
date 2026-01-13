"""
Report API endpoints
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.api.deps import get_db, get_current_user, get_pagination, require_permission
from app.core.security import Permission
from app.models.user import User
from app.models.task import TestTask, TaskExecution
from app.models.report import TestReport
from app.schemas.report import (
    TestReportResponse,
    ReportStatistics,
)
from app.schemas.common import APIResponse, PaginatedResponse, PaginationParams


router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedResponse[TestReportResponse]])
async def list_reports(
    pagination: PaginationParams = Depends(get_pagination),
    project_id: Optional[UUID] = Query(None),
    task_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.REPORT_READ))
):
    """
    List all test reports with pagination
    """
    query = select(TestReport)
    count_query = select(func.count(TestReport.id))
    
    if task_id:
        query = query.where(TestReport.task_id == task_id)
        count_query = count_query.where(TestReport.task_id == task_id)
    
    if project_id:
        query = query.join(TestTask).where(TestTask.project_id == project_id)
        count_query = count_query.join(TestTask).where(TestTask.project_id == project_id)
    
    if start_date:
        query = query.where(TestReport.created_at >= start_date)
        count_query = count_query.where(TestReport.created_at >= start_date)
    
    if end_date:
        query = query.where(TestReport.created_at <= end_date)
        count_query = count_query.where(TestReport.created_at <= end_date)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(TestReport.created_at.desc())
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    items = [TestReportResponse.model_validate(r) for r in reports]
    
    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
    )


@router.get("/statistics", response_model=APIResponse[ReportStatistics])
async def get_statistics(
    project_id: Optional[UUID] = Query(None),
    period: str = Query(default="week", pattern="^(day|week|month)$"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.REPORT_READ))
):
    """
    Get aggregated statistics for reports
    """
    now = datetime.now(timezone.utc)
    
    # Set default date range based on period
    if not end_date:
        end_date = now
    if not start_date:
        if period == "day":
            start_date = end_date - timedelta(days=1)
        elif period == "week":
            start_date = end_date - timedelta(weeks=1)
        else:
            start_date = end_date - timedelta(days=30)
    
    # Build base query
    base_filter = and_(
        TaskExecution.started_at >= start_date,
        TaskExecution.started_at <= end_date,
        TaskExecution.status.in_(["success", "failed"])
    )
    
    if project_id:
        base_filter = and_(
            base_filter,
            TestTask.project_id == project_id
        )
    
    # Get overview statistics
    overview_query = select(
        func.count(TaskExecution.id).label("total_executions"),
        func.sum(TaskExecution.total_cases).label("total_cases"),
        func.sum(TaskExecution.passed_cases).label("passed"),
        func.sum(TaskExecution.failed_cases).label("failed")
    ).select_from(TaskExecution).join(TestTask).where(base_filter)
    
    overview_result = await db.execute(overview_query)
    overview_row = overview_result.one()
    
    total_executed = (overview_row.passed or 0) + (overview_row.failed or 0)
    avg_pass_rate = 0.0
    if total_executed > 0:
        avg_pass_rate = round((overview_row.passed or 0) / total_executed * 100, 2)
    
    overview = {
        "total_tasks": overview_row.total_executions or 0,
        "total_executions": overview_row.total_executions or 0,
        "total_cases": overview_row.total_cases or 0,
        "avg_pass_rate": avg_pass_rate
    }
    
    # TODO: Calculate trend data (daily/weekly breakdown)
    trend = []
    
    # TODO: Get statistics by project
    by_project = []
    
    # TODO: Get top failed cases
    top_failed_cases = []
    
    return APIResponse(
        data=ReportStatistics(
            overview=overview,
            trend=trend,
            by_project=by_project,
            top_failed_cases=top_failed_cases
        )
    )


@router.get("/{report_id}", response_model=APIResponse[TestReportResponse])
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.REPORT_READ))
):
    """
    Get report by ID
    """
    result = await db.execute(
        select(TestReport).where(TestReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return APIResponse(data=TestReportResponse.model_validate(report))


@router.get("/{report_id}/export")
async def export_report(
    report_id: UUID,
    format: str = Query(default="pdf", pattern="^(pdf|excel|html)$"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.REPORT_EXPORT))
):
    """
    Export report in specified format
    """
    result = await db.execute(
        select(TestReport).where(TestReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # TODO: Implement actual export logic
    # For now, return the stored file if available
    
    if format == "pdf" and report.pdf_report_path:
        # Return PDF file
        pass
    elif format == "html" and report.html_report_path:
        # Return HTML file
        pass
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Export to {format} not implemented"
    )
