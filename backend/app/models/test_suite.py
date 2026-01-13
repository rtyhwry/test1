"""
TestSuite and TestCase models
"""
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task import TestTask, TestCaseResult


class TestSuite(BaseModel):
    """Test suite model"""
    
    __tablename__ = "test_suites"
    
    name: Mapped[str] = Column(String(200), nullable=False)
    description: Mapped[Optional[str]] = Column(Text)
    
    project_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    
    source: Mapped[str] = Column(String(20), default="manual")  # manual, alm, gitlab
    alm_suite_id: Mapped[Optional[str]] = Column(String(100), index=True)
    
    git_repo: Mapped[Optional[str]] = Column(String(500))
    git_branch: Mapped[str] = Column(String(100), default="main")
    git_path: Mapped[Optional[str]] = Column(String(500))
    
    framework: Mapped[Optional[str]] = Column(String(50))  # pytest, robot, custom
    setup_commands: Mapped[Optional[str]] = Column(Text)
    teardown_commands: Mapped[Optional[str]] = Column(Text)
    
    tags: Mapped[list] = Column(JSONB, default=list)
    
    created_by: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="test_suites")
    test_cases: Mapped[List["TestCase"]] = relationship(
        "TestCase",
        back_populates="suite",
        cascade="all, delete-orphan"
    )
    tasks: Mapped[List["TestTask"]] = relationship("TestTask", back_populates="suite")
    
    def __repr__(self):
        return f"<TestSuite {self.name}>"
    
    @property
    def case_count(self) -> int:
        """Get number of test cases"""
        return len(self.test_cases) if self.test_cases else 0


class TestCase(BaseModel):
    """Test case model"""
    
    __tablename__ = "test_cases"
    
    suite_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("test_suites.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    name: Mapped[str] = Column(String(500), nullable=False)
    description: Mapped[Optional[str]] = Column(Text)
    
    alm_case_id: Mapped[Optional[str]] = Column(String(100), index=True)
    
    priority: Mapped[str] = Column(String(20), default="medium", index=True)
    # critical, high, medium, low
    case_type: Mapped[Optional[str]] = Column(String(50))
    # smoke, regression, functional, performance
    
    script_path: Mapped[Optional[str]] = Column(String(500))
    class_name: Mapped[Optional[str]] = Column(String(200))
    method_name: Mapped[Optional[str]] = Column(String(200))
    
    parameters: Mapped[dict] = Column(JSONB, default=dict)
    
    timeout: Mapped[int] = Column(Integer, default=300)  # seconds
    retry_count: Mapped[int] = Column(Integer, default=0)
    
    preconditions: Mapped[Optional[str]] = Column(Text)
    steps: Mapped[Optional[str]] = Column(Text)
    expected_results: Mapped[Optional[str]] = Column(Text)
    
    tags: Mapped[list] = Column(JSONB, default=list)
    capabilities_required: Mapped[list] = Column(JSONB, default=list)
    
    is_automated: Mapped[bool] = Column(Boolean, default=True)
    status: Mapped[str] = Column(String(20), default="active")  # active, deprecated
    
    created_by: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    suite: Mapped["TestSuite"] = relationship("TestSuite", back_populates="test_cases")
    results: Mapped[List["TestCaseResult"]] = relationship(
        "TestCaseResult",
        back_populates="test_case"
    )
    
    def __repr__(self):
        return f"<TestCase {self.name}>"
    
    @property
    def full_path(self) -> str:
        """Get full test path"""
        parts = []
        if self.script_path:
            parts.append(self.script_path)
        if self.class_name:
            parts.append(self.class_name)
        if self.method_name:
            parts.append(self.method_name)
        return "::".join(parts) if parts else self.name
