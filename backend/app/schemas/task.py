"""
TestTask, TaskExecution, and TestCaseResult schemas
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


# Version configuration
class VersionConfig(BaseModel):
    """Version configuration for upgrade"""
    strategy: str = Field(..., pattern="^(latest|specific)$")
    version: Optional[str] = None
    artifact_name: Optional[str] = None


# Environment configuration
class EnvConfig(BaseModel):
    """Environment configuration"""
    strategy: str = Field(default="auto", pattern="^(auto|specific)$")
    environment_id: Optional[UUID] = None
    requirements: Dict[str, Any] = Field(default_factory=dict)


# Test configuration
class TestConfig(BaseModel):
    """Test configuration"""
    suite_id: UUID
    case_ids: Optional[List[UUID]] = None
    case_filter: Dict[str, Any] = Field(default_factory=dict)


# Execution configuration
class ExecutionConfig(BaseModel):
    """Execution configuration"""
    timeout: int = Field(default=3600, ge=60)
    retry_on_failure: bool = False
    max_retries: int = Field(default=1, ge=0, le=5)
    parallel_count: int = Field(default=1, ge=1)


# Notification configuration
class NotifyConfig(BaseModel):
    """Notification configuration"""
    on_success: bool = True
    on_failure: bool = True
    channels: List[str] = Field(default_factory=list)
    recipients: List[str] = Field(default_factory=list)
    webhook_url: Optional[str] = None


# TestTask schemas
class TestTaskBase(BaseModel):
    """TestTask base schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class TestTaskCreate(TestTaskBase):
    """TestTask create schema"""
    project_id: Optional[UUID] = None
    
    # Trigger configuration
    trigger_type: str = Field(default="immediate", pattern="^(immediate|scheduled|cron)$")
    schedule_time: Optional[datetime] = None
    cron_expression: Optional[str] = None
    
    # Priority
    priority: int = Field(default=5, ge=1, le=10)
    
    # Upgrade configuration
    need_upgrade: bool = False
    version_config: Optional[VersionConfig] = None
    
    # Environment configuration
    env_config: Optional[EnvConfig] = None
    
    # Test configuration
    test_config: TestConfig
    
    # Execution configuration
    execution_config: Optional[ExecutionConfig] = None
    
    # Notification configuration
    notify_config: Optional[NotifyConfig] = None


class TestTaskUpdate(BaseModel):
    """TestTask update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    trigger_type: Optional[str] = Field(None, pattern="^(immediate|scheduled|cron)$")
    schedule_time: Optional[datetime] = None
    cron_expression: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    need_upgrade: Optional[bool] = None
    version_config: Optional[VersionConfig] = None
    env_config: Optional[EnvConfig] = None
    execution_config: Optional[ExecutionConfig] = None
    notify_config: Optional[NotifyConfig] = None


class TaskStatistics(BaseModel):
    """Task execution statistics"""
    total_cases: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    error: int = 0
    running: int = 0
    pending: int = 0
    pass_rate: float = 0.0


class TestTaskResponse(TestTaskBase, TimestampSchema):
    """TestTask response schema"""
    id: UUID
    project_id: Optional[UUID] = None
    source: str
    trigger_type: str
    schedule_time: Optional[datetime] = None
    cron_expression: Optional[str] = None
    priority: int
    need_upgrade: bool
    version_config: Optional[Dict] = None
    env_config: Optional[Dict] = None
    environment_id: Optional[UUID] = None
    suite_id: Optional[UUID] = None
    status: str
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    
    # Related data
    statistics: Optional[TaskStatistics] = None
    
    model_config = {"from_attributes": True}


class TestTaskListResponse(BaseModel):
    """TestTask list item response"""
    id: UUID
    name: str
    project_id: Optional[UUID] = None
    source: str
    trigger_type: str
    priority: int
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    statistics: Optional[TaskStatistics] = None
    
    model_config = {"from_attributes": True}


# TaskExecution schemas
class TaskExecutionResponse(TimestampSchema):
    """TaskExecution response schema"""
    id: UUID
    task_id: UUID
    execution_number: int
    environment_id: Optional[UUID] = None
    host_id: Optional[UUID] = None
    software_version: Optional[str] = None
    upgraded_from: Optional[str] = None
    git_repo: Optional[str] = None
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration: Optional[int] = None
    total_cases: int
    passed_cases: int
    failed_cases: int
    skipped_cases: int
    error_cases: int
    pass_rate: float = 0.0
    log_path: Optional[str] = None
    error_message: Optional[str] = None
    
    model_config = {"from_attributes": True}


# TestCaseResult schemas
class TestCaseResultResponse(TimestampSchema):
    """TestCaseResult response schema"""
    id: UUID
    execution_id: UUID
    case_id: Optional[UUID] = None
    case_name: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration: Optional[int] = None
    retry_count: int
    error_message: Optional[str] = None
    error_stack: Optional[str] = None
    logs: Optional[str] = None
    screenshots: List[str] = []
    attachments: List[str] = []
    metrics: Dict = {}
    
    model_config = {"from_attributes": True}


# Task action
class TaskAction(BaseModel):
    """Task action request"""
    action: str = Field(..., pattern="^(start|stop|cancel|retry)$")


# Task filter
class TaskFilter(BaseModel):
    """Task filter parameters"""
    project_id: Optional[UUID] = None
    status: Optional[str] = None
    trigger_type: Optional[str] = None
    source: Optional[str] = None
    created_by: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
