"""
TestTask, TaskExecution, and TestCaseResult models
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Boolean, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.environment import Environment, TestHost
    from app.models.test_suite import TestSuite, TestCase
    from app.models.report import TestReport


class TestTask(BaseModel):
    """Test task model"""
    
    __tablename__ = "test_tasks"
    
    name: Mapped[str] = Column(String(200), nullable=False)
    description: Mapped[Optional[str]] = Column(Text)
    
    project_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    
    # Source
    source: Mapped[str] = Column(String(20), default="manual", index=True)
    # manual, alm, ci, api
    external_id: Mapped[Optional[str]] = Column(String(100))
    
    # Trigger configuration
    trigger_type: Mapped[str] = Column(String(20), default="immediate", index=True)
    # immediate, scheduled, cron
    schedule_time: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), index=True)
    cron_expression: Mapped[Optional[str]] = Column(String(100))
    
    # Priority
    priority: Mapped[int] = Column(Integer, default=5, index=True)  # 1-10, 1 is highest
    
    # Upgrade configuration
    need_upgrade: Mapped[bool] = Column(Boolean, default=False)
    version_strategy: Mapped[Optional[str]] = Column(String(20))  # latest, specific
    target_version: Mapped[Optional[str]] = Column(String(50))
    artifact_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True))
    
    # Environment configuration
    env_strategy: Mapped[str] = Column(String(20), default="auto")  # auto, specific
    environment_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("environments.id"))
    env_requirements: Mapped[dict] = Column(JSONB, default=dict)
    
    # Test configuration
    suite_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("test_suites.id"))
    case_ids: Mapped[Optional[list]] = Column(JSONB)  # null means all cases
    case_filter: Mapped[dict] = Column(JSONB, default=dict)
    
    # Execution configuration
    parallel_count: Mapped[int] = Column(Integer, default=1)
    timeout: Mapped[int] = Column(Integer, default=3600)  # seconds
    retry_on_failure: Mapped[bool] = Column(Boolean, default=False)
    max_retries: Mapped[int] = Column(Integer, default=1)
    
    # Notification configuration
    notify_config: Mapped[dict] = Column(JSONB, default=dict)
    
    # Status
    status: Mapped[str] = Column(String(20), default="pending", index=True)
    # pending, queued, preparing, running, success, failed, cancelled, timeout
    
    # Timestamps
    queued_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    started_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    
    created_by: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="test_tasks")
    environment: Mapped[Optional["Environment"]] = relationship("Environment")
    suite: Mapped[Optional["TestSuite"]] = relationship("TestSuite", back_populates="tasks")
    executions: Mapped[List["TaskExecution"]] = relationship(
        "TaskExecution",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskExecution.execution_number.desc()"
    )
    
    def __repr__(self):
        return f"<TestTask {self.name} ({self.status})>"
    
    @property
    def latest_execution(self) -> Optional["TaskExecution"]:
        """Get the latest execution"""
        return self.executions[0] if self.executions else None
    
    @property
    def duration(self) -> Optional[int]:
        """Get task duration in seconds"""
        if self.started_at and self.finished_at:
            return int((self.finished_at - self.started_at).total_seconds())
        return None


class TaskExecution(BaseModel):
    """Task execution record"""
    
    __tablename__ = "task_executions"
    
    task_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("test_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    execution_number: Mapped[int] = Column(Integer, nullable=False)
    
    environment_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("environments.id"))
    host_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("test_hosts.id"))
    
    # Version info
    software_version: Mapped[Optional[str]] = Column(String(50))
    upgraded_from: Mapped[Optional[str]] = Column(String(50))
    
    # Git info
    git_repo: Mapped[Optional[str]] = Column(String(500))
    git_branch: Mapped[Optional[str]] = Column(String(100))
    git_commit: Mapped[Optional[str]] = Column(String(100))
    
    # Status
    status: Mapped[str] = Column(String(20), default="pending", index=True)
    # pending, preparing, upgrading, pulling, running, success, failed, cancelled
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), index=True)
    finished_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    duration: Mapped[Optional[int]] = Column(Integer)  # seconds
    
    # Results
    total_cases: Mapped[int] = Column(Integer, default=0)
    passed_cases: Mapped[int] = Column(Integer, default=0)
    failed_cases: Mapped[int] = Column(Integer, default=0)
    skipped_cases: Mapped[int] = Column(Integer, default=0)
    error_cases: Mapped[int] = Column(Integer, default=0)
    
    # Logs
    log_path: Mapped[Optional[str]] = Column(String(500))
    error_message: Mapped[Optional[str]] = Column(Text)
    
    # Context
    context: Mapped[dict] = Column(JSONB, default=dict)
    
    # Relationships
    task: Mapped["TestTask"] = relationship("TestTask", back_populates="executions")
    environment: Mapped[Optional["Environment"]] = relationship("Environment", back_populates="executions")
    host: Mapped[Optional["TestHost"]] = relationship("TestHost")
    case_results: Mapped[List["TestCaseResult"]] = relationship(
        "TestCaseResult",
        back_populates="execution",
        cascade="all, delete-orphan"
    )
    report: Mapped[Optional["TestReport"]] = relationship(
        "TestReport",
        back_populates="execution",
        uselist=False
    )
    
    def __repr__(self):
        return f"<TaskExecution {self.task_id}#{self.execution_number}>"
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate"""
        executed = self.passed_cases + self.failed_cases + self.error_cases
        if executed == 0:
            return 0.0
        return round((self.passed_cases / executed) * 100, 2)


class TestCaseResult(BaseModel):
    """Test case execution result"""
    
    __tablename__ = "test_case_results"
    
    execution_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("task_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    case_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("test_cases.id"))
    
    case_name: Mapped[str] = Column(String(500))  # Denormalized for performance
    
    status: Mapped[str] = Column(String(20), nullable=False, index=True)
    # passed, failed, skipped, error, timeout
    
    started_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    duration: Mapped[Optional[int]] = Column(Integer)  # milliseconds
    
    retry_count: Mapped[int] = Column(Integer, default=0)
    
    error_message: Mapped[Optional[str]] = Column(Text)
    error_stack: Mapped[Optional[str]] = Column(Text)
    
    logs: Mapped[Optional[str]] = Column(Text)
    screenshots: Mapped[list] = Column(JSONB, default=list)
    attachments: Mapped[list] = Column(JSONB, default=list)
    
    metrics: Mapped[dict] = Column(JSONB, default=dict)
    
    # Relationships
    execution: Mapped["TaskExecution"] = relationship("TaskExecution", back_populates="case_results")
    test_case: Mapped[Optional["TestCase"]] = relationship("TestCase", back_populates="results")
    
    def __repr__(self):
        return f"<TestCaseResult {self.case_name}: {self.status}>"
