"""
User and Role schemas
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr

from app.schemas.common import BaseSchema, TimestampSchema


# Role schemas
class RoleBase(BaseModel):
    """Role base schema"""
    name: str = Field(..., min_length=1, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)


class RoleCreate(RoleBase):
    """Role create schema"""
    pass


class RoleUpdate(BaseModel):
    """Role update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleResponse(RoleBase, TimestampSchema):
    """Role response schema"""
    id: UUID
    is_system: bool
    
    model_config = {"from_attributes": True}


# User schemas
class UserBase(BaseModel):
    """User base schema"""
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    display_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    """User create schema"""
    password: str = Field(..., min_length=6)
    role_id: Optional[UUID] = None
    auth_type: str = Field(default="local", pattern="^(local|ldap|oauth2)$")


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    display_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role_id: Optional[UUID] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|locked)$")


class PasswordUpdate(BaseModel):
    """Password update schema"""
    old_password: str
    new_password: str = Field(..., min_length=6)


class UserResponse(UserBase, TimestampSchema):
    """User response schema"""
    id: UUID
    role_id: Optional[UUID] = None
    role: Optional[RoleResponse] = None
    auth_type: str
    status: str
    last_login_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """User list item response"""
    id: UUID
    username: str
    email: str
    display_name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    status: str
    last_login_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}
