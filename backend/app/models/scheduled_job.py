"""
ScheduledJob model
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from app.models.base import BaseModel


class ScheduledJob(BaseModel):
    """Scheduled job model for cron tasks"""
    
    __tablename__ = "scheduled_jobs"
    
    task_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("test_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    job_type: Mapped[str] = Column(String(20), nullable=False)
    # once, cron
    
    schedule_time: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    cron_expression: Mapped[Optional[str]] = Column(String(100))
    timezone: Mapped[str] = Column(String(50), default="Asia/Shanghai")
    
    next_run_time: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), index=True)
    last_run_time: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    
    is_enabled: Mapped[bool] = Column(Boolean, default=True, index=True)
    
    def __repr__(self):
        return f"<ScheduledJob {self.task_id} ({self.job_type})>"
