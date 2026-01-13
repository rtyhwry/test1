"""
OperationLog model for audit trail
"""
from typing import Optional

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import Mapped

from app.models.base import BaseModel


class OperationLog(BaseModel):
    """Operation log model for audit"""
    
    __tablename__ = "operation_logs"
    
    user_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    username: Mapped[Optional[str]] = Column(String(50))
    
    action: Mapped[str] = Column(String(50), nullable=False, index=True)
    # create, update, delete, execute, login, logout
    
    resource_type: Mapped[str] = Column(String(50), nullable=False, index=True)
    # task, environment, report, user, project
    resource_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True))
    resource_name: Mapped[Optional[str]] = Column(String(200))
    
    details: Mapped[dict] = Column(JSONB, default=dict)
    
    ip_address: Mapped[Optional[str]] = Column(INET)
    user_agent: Mapped[Optional[str]] = Column(Text)
    
    def __repr__(self):
        return f"<OperationLog {self.action} {self.resource_type}>"
