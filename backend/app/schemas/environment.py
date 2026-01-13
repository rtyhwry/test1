"""
Environment, TestHost, and TestDevice schemas
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


# TestHost schemas
class TestHostBase(BaseModel):
    """TestHost base schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    ip_address: str = Field(..., description="IP address")
    ssh_port: int = Field(default=22, ge=1, le=65535)
    username: Optional[str] = Field(None, max_length=50)
    auth_type: str = Field(default="password", pattern="^(password|key)$")
    work_directory: str = Field(default="/opt/test")


class TestHostCreate(TestHostBase):
    """TestHost create schema"""
    password: Optional[str] = None
    ssh_key: Optional[str] = None
    project_id: Optional[UUID] = None
    capabilities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    max_concurrent_tasks: int = Field(default=1, ge=1)


class TestHostUpdate(BaseModel):
    """TestHost update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    ip_address: Optional[str] = None
    ssh_port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = Field(None, max_length=50)
    auth_type: Optional[str] = Field(None, pattern="^(password|key)$")
    password: Optional[str] = None
    ssh_key: Optional[str] = None
    work_directory: Optional[str] = None
    capabilities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    max_concurrent_tasks: Optional[int] = Field(None, ge=1)
    status: Optional[str] = None


class TestHostResponse(TestHostBase, TimestampSchema):
    """TestHost response schema"""
    id: UUID
    status: str
    last_heartbeat: Optional[datetime] = None
    system_info: dict = {}
    capabilities: List[str] = []
    tags: List[str] = []
    max_concurrent_tasks: int
    current_task_count: int
    project_id: Optional[UUID] = None
    
    model_config = {"from_attributes": True}


# TestDevice schemas
class TestDeviceBase(BaseModel):
    """TestDevice base schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    device_type: str = Field(..., min_length=1, max_length=50)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)


class TestDeviceCreate(TestDeviceBase):
    """TestDevice create schema"""
    host_id: Optional[UUID] = None
    connection_type: Optional[str] = None
    connection_config: dict = Field(default_factory=dict)
    project_id: Optional[UUID] = None
    capabilities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class TestDeviceUpdate(BaseModel):
    """TestDevice update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    device_type: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    host_id: Optional[UUID] = None
    connection_type: Optional[str] = None
    connection_config: Optional[dict] = None
    capabilities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class TestDeviceResponse(TestDeviceBase, TimestampSchema):
    """TestDevice response schema"""
    id: UUID
    host_id: Optional[UUID] = None
    connection_type: Optional[str] = None
    connection_config: dict = {}
    current_version: Optional[str] = None
    hardware_version: Optional[str] = None
    status: str
    last_heartbeat: Optional[datetime] = None
    capabilities: List[str] = []
    tags: List[str] = []
    project_id: Optional[UUID] = None
    
    model_config = {"from_attributes": True}


# Environment schemas
class EnvironmentBase(BaseModel):
    """Environment base schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    env_type: Optional[str] = Field(None, max_length=50)


class EnvironmentCreate(EnvironmentBase):
    """Environment create schema"""
    host_id: Optional[UUID] = None
    device_ids: List[UUID] = Field(default_factory=list)
    project_id: Optional[UUID] = None
    capabilities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class EnvironmentUpdate(BaseModel):
    """Environment update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    env_type: Optional[str] = Field(None, max_length=50)
    host_id: Optional[UUID] = None
    device_ids: Optional[List[UUID]] = None
    capabilities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class EnvironmentResponse(EnvironmentBase, TimestampSchema):
    """Environment response schema"""
    id: UUID
    host_id: Optional[UUID] = None
    host: Optional[TestHostResponse] = None
    device_ids: List[UUID] = []
    devices: List[TestDeviceResponse] = []
    status: str
    current_task_id: Optional[UUID] = None
    capabilities: List[str] = []
    tags: List[str] = []
    reserved_by: Optional[UUID] = None
    reserved_until: Optional[datetime] = None
    project_id: Optional[UUID] = None
    
    model_config = {"from_attributes": True}


class EnvironmentReserveRequest(BaseModel):
    """Environment reserve request"""
    start_time: datetime
    end_time: datetime
    reason: Optional[str] = None


class EnvironmentActionRequest(BaseModel):
    """Environment action request"""
    action: str = Field(..., pattern="^(maintenance|release|reserve)$")
