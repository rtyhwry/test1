"""
Common schemas used across the application
"""
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    items: List[T]
    total: int
    page: int
    page_size: int
    
    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size
    
    model_config = {"from_attributes": True}


class ErrorDetail(BaseModel):
    """Error detail"""
    field: Optional[str] = None
    message: str


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None
    errors: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {"from_attributes": True}


class IDModel(BaseModel):
    """Model with just ID"""
    id: UUID


class NamedModel(IDModel):
    """Model with ID and name"""
    name: str


class BaseSchema(BaseModel):
    """Base schema with common config"""
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_schema_extra": {"examples": []}
    }


class TimestampSchema(BaseModel):
    """Schema with timestamps"""
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
