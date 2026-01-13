"""
Project model
"""
from typing import Optional, List

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel


class Project(BaseModel):
    """Project model"""
    
    __tablename__ = "projects"
    
    name: Mapped[str] = Column(String(100), nullable=False)
    code: Mapped[str] = Column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = Column(Text)
    
    owner_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    team_members: Mapped[list] = Column(JSONB, default=list)  # List of user IDs
    
    settings: Mapped[dict] = Column(JSONB, default=dict)
    status: Mapped[str] = Column(String(20), default="active", index=True)  # active, archived
    
    created_by: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    environments: Mapped[List["Environment"]] = relationship(
        "Environment",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    test_suites: Mapped[List["TestSuite"]] = relationship(
        "TestSuite",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    test_tasks: Mapped[List["TestTask"]] = relationship(
        "TestTask",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Project {self.code}: {self.name}>"


# Import at bottom to avoid circular imports
from app.models.environment import Environment
from app.models.test_suite import TestSuite
from app.models.task import TestTask
