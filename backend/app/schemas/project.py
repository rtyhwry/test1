"""
Project schemas
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class ProjectBase(BaseModel):
    """Project base schema"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50, pattern="^[A-Za-z0-9_-]+$")
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project create schema"""
    owner_id: Optional[UUID] = None
    team_members: List[UUID] = Field(default_factory=list)
    settings: dict = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    owner_id: Optional[UUID] = None
    team_members: Optional[List[UUID]] = None
    settings: Optional[dict] = None
    status: Optional[str] = Field(None, pattern="^(active|archived)$")


class ProjectResponse(ProjectBase, TimestampSchema):
    """Project response schema"""
    id: UUID
    owner_id: Optional[UUID] = None
    team_members: List[UUID] = []
    settings: dict = {}
    status: str
    created_by: Optional[UUID] = None
    
    # Statistics
    environment_count: int = 0
    task_count: int = 0
    
    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Project list item response"""
    id: UUID
    name: str
    code: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    
    model_config = {"from_attributes": True}
