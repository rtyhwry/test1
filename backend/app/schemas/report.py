"""
Report schemas
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel

from app.schemas.common import TimestampSchema


class ReportSummary(BaseModel):
    """Report summary"""
    total_cases: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    error: int = 0
    pass_rate: float = 0.0
    duration: int = 0


class EnvironmentInfo(BaseModel):
    """Environment info in report"""
    host: Optional[str] = None
    device: Optional[str] = None
    software_version: Optional[str] = None


class FailedCaseInfo(BaseModel):
    """Failed case info"""
    id: UUID
    name: str
    error_message: Optional[str] = None
    duration: Optional[int] = None


class TestReportResponse(TimestampSchema):
    """TestReport response schema"""
    id: UUID
    execution_id: UUID
    task_id: Optional[UUID] = None
    report_name: Optional[str] = None
    report_type: str
    
    # Statistics
    total_cases: int
    passed: int
    failed: int
    skipped: int
    error: int
    pass_rate: float
    duration: Optional[int] = None
    
    # Environment
    environment_info: Dict = {}
    
    # Report files
    html_report_path: Optional[str] = None
    pdf_report_path: Optional[str] = None
    json_report_path: Optional[str] = None
    
    # Summary
    summary: Optional[str] = None
    highlights: List[Dict] = []
    
    model_config = {"from_attributes": True}


class ReportStatistics(BaseModel):
    """Report statistics for dashboard"""
    overview: Dict = {}
    trend: List[Dict] = []
    by_project: List[Dict] = []
    top_failed_cases: List[Dict] = []


class ReportExportRequest(BaseModel):
    """Report export request"""
    format: str = "pdf"  # pdf, excel, html


class DailyStatistics(BaseModel):
    """Daily statistics"""
    date: str
    executions: int
    pass_rate: float
    total_cases: int
    passed: int
    failed: int


class ProjectStatistics(BaseModel):
    """Project statistics"""
    project_id: UUID
    project_name: str
    executions: int
    pass_rate: float


class TopFailedCase(BaseModel):
    """Top failed case"""
    case_id: UUID
    case_name: str
    failure_count: int
    last_failure: Optional[datetime] = None
