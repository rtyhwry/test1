"""
TestSuite and TestCase schemas
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


# TestSuite schemas
class TestSuiteBase(BaseModel):
    """TestSuite base schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    source: str = Field(default="manual", pattern="^(manual|alm|gitlab)$")


class TestSuiteCreate(TestSuiteBase):
    """TestSuite create schema"""
    project_id: Optional[UUID] = None
    alm_suite_id: Optional[str] = None
    git_repo: Optional[str] = None
    git_branch: str = Field(default="main")
    git_path: Optional[str] = None
    framework: Optional[str] = None
    setup_commands: Optional[str] = None
    teardown_commands: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class TestSuiteUpdate(BaseModel):
    """TestSuite update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    git_repo: Optional[str] = None
    git_branch: Optional[str] = None
    git_path: Optional[str] = None
    framework: Optional[str] = None
    setup_commands: Optional[str] = None
    teardown_commands: Optional[str] = None
    tags: Optional[List[str]] = None


class TestSuiteResponse(TestSuiteBase, TimestampSchema):
    """TestSuite response schema"""
    id: UUID
    project_id: Optional[UUID] = None
    alm_suite_id: Optional[str] = None
    git_repo: Optional[str] = None
    git_branch: str
    git_path: Optional[str] = None
    framework: Optional[str] = None
    setup_commands: Optional[str] = None
    teardown_commands: Optional[str] = None
    tags: List[str] = []
    case_count: int = 0
    
    model_config = {"from_attributes": True}


# TestCase schemas
class TestCaseBase(BaseModel):
    """TestCase base schema"""
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(critical|high|medium|low)$")
    case_type: Optional[str] = None


class TestCaseCreate(TestCaseBase):
    """TestCase create schema"""
    suite_id: UUID
    alm_case_id: Optional[str] = None
    script_path: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None
    parameters: dict = Field(default_factory=dict)
    timeout: int = Field(default=300, ge=1)
    retry_count: int = Field(default=0, ge=0)
    preconditions: Optional[str] = None
    steps: Optional[str] = None
    expected_results: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    capabilities_required: List[str] = Field(default_factory=list)
    is_automated: bool = True


class TestCaseUpdate(BaseModel):
    """TestCase update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(critical|high|medium|low)$")
    case_type: Optional[str] = None
    script_path: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None
    parameters: Optional[dict] = None
    timeout: Optional[int] = Field(None, ge=1)
    retry_count: Optional[int] = Field(None, ge=0)
    preconditions: Optional[str] = None
    steps: Optional[str] = None
    expected_results: Optional[str] = None
    tags: Optional[List[str]] = None
    capabilities_required: Optional[List[str]] = None
    is_automated: Optional[bool] = None
    status: Optional[str] = Field(None, pattern="^(active|deprecated)$")


class TestCaseResponse(TestCaseBase, TimestampSchema):
    """TestCase response schema"""
    id: UUID
    suite_id: UUID
    alm_case_id: Optional[str] = None
    script_path: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None
    parameters: dict = {}
    timeout: int
    retry_count: int
    preconditions: Optional[str] = None
    steps: Optional[str] = None
    expected_results: Optional[str] = None
    tags: List[str] = []
    capabilities_required: List[str] = []
    is_automated: bool
    status: str
    
    model_config = {"from_attributes": True}


class TestCaseListResponse(BaseModel):
    """TestCase list item response"""
    id: UUID
    name: str
    priority: str
    case_type: Optional[str] = None
    is_automated: bool
    status: str
    tags: List[str] = []
    
    model_config = {"from_attributes": True}
