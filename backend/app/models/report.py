"""
TestReport model
"""
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.task import TaskExecution, TestTask


class TestReport(BaseModel):
    """Test report model"""
    
    __tablename__ = "test_reports"
    
    execution_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("task_executions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    task_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("test_tasks.id"))
    
    report_name: Mapped[Optional[str]] = Column(String(200))
    report_type: Mapped[str] = Column(String(50), default="execution")
    # execution, daily, weekly, custom
    
    # Statistics
    total_cases: Mapped[int] = Column(Integer, default=0)
    passed: Mapped[int] = Column(Integer, default=0)
    failed: Mapped[int] = Column(Integer, default=0)
    skipped: Mapped[int] = Column(Integer, default=0)
    error: Mapped[int] = Column(Integer, default=0)
    
    pass_rate: Mapped[Optional[float]] = Column(Numeric(5, 2))
    duration: Mapped[Optional[int]] = Column(Integer)  # seconds
    
    # Environment info
    environment_info: Mapped[dict] = Column(JSONB, default=dict)
    
    # Report files
    html_report_path: Mapped[Optional[str]] = Column(String(500))
    pdf_report_path: Mapped[Optional[str]] = Column(String(500))
    json_report_path: Mapped[Optional[str]] = Column(String(500))
    
    # Summary
    summary: Mapped[Optional[str]] = Column(Text)
    highlights: Mapped[list] = Column(JSONB, default=list)  # Key issues
    
    # Relationships
    execution: Mapped["TaskExecution"] = relationship(
        "TaskExecution",
        back_populates="report"
    )
    task: Mapped[Optional["TestTask"]] = relationship("TestTask")
    
    def __repr__(self):
        return f"<TestReport {self.report_name}>"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_cases == 0:
            return 0.0
        return round((self.passed / self.total_cases) * 100, 2)
