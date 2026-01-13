"""
Environment, TestHost, and TestDevice models
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task import TaskExecution


class TestHost(BaseModel):
    """Test host (machine that runs tests)"""
    
    __tablename__ = "test_hosts"
    
    name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[Optional[str]] = Column(Text)
    
    ip_address: Mapped[str] = Column(INET, nullable=False)
    ssh_port: Mapped[int] = Column(Integer, default=22)
    username: Mapped[Optional[str]] = Column(String(50))
    auth_type: Mapped[str] = Column(String(20), default="password")  # password, key
    password_encrypted: Mapped[Optional[str]] = Column(String(500))
    ssh_key_encrypted: Mapped[Optional[str]] = Column(Text)
    
    work_directory: Mapped[str] = Column(String(500), default="/opt/test")
    
    status: Mapped[str] = Column(String(20), default="offline", index=True)
    # online, offline, busy, maintenance
    last_heartbeat: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    
    system_info: Mapped[dict] = Column(JSONB, default=dict)
    tags: Mapped[list] = Column(JSONB, default=list)
    capabilities: Mapped[list] = Column(JSONB, default=list)
    
    max_concurrent_tasks: Mapped[int] = Column(Integer, default=1)
    current_task_count: Mapped[int] = Column(Integer, default=0)
    
    project_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    created_by: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    devices: Mapped[List["TestDevice"]] = relationship(
        "TestDevice",
        back_populates="host",
        cascade="all, delete-orphan"
    )
    environments: Mapped[List["Environment"]] = relationship(
        "Environment",
        back_populates="host"
    )
    
    def __repr__(self):
        return f"<TestHost {self.name} ({self.ip_address})>"
    
    @property
    def is_available(self) -> bool:
        """Check if host is available for new tasks"""
        return (
            self.status == "online" and
            self.current_task_count < self.max_concurrent_tasks
        )


class TestDevice(BaseModel):
    """Test device (ECU, VCU, etc.)"""
    
    __tablename__ = "test_devices"
    
    name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[Optional[str]] = Column(Text)
    
    device_type: Mapped[str] = Column(String(50), nullable=False, index=True)
    # ECU, VCU, BMS, MCU, Tbox, IVI, etc.
    model: Mapped[Optional[str]] = Column(String(100))
    serial_number: Mapped[Optional[str]] = Column(String(100))
    
    host_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("test_hosts.id"))
    
    connection_type: Mapped[Optional[str]] = Column(String(50))
    # ssh, serial, can, doip, uds
    connection_config: Mapped[dict] = Column(JSONB, default=dict)
    
    current_version: Mapped[Optional[str]] = Column(String(50))
    hardware_version: Mapped[Optional[str]] = Column(String(50))
    
    status: Mapped[str] = Column(String(20), default="offline", index=True)
    # online, offline, busy, upgrading, error
    last_heartbeat: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    
    capabilities: Mapped[list] = Column(JSONB, default=list)
    tags: Mapped[list] = Column(JSONB, default=list)
    
    project_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    created_by: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    host: Mapped[Optional["TestHost"]] = relationship("TestHost", back_populates="devices")
    
    def __repr__(self):
        return f"<TestDevice {self.name} ({self.device_type})>"


class Environment(BaseModel):
    """Test environment (combination of host and devices)"""
    
    __tablename__ = "environments"
    
    name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[Optional[str]] = Column(Text)
    
    env_type: Mapped[Optional[str]] = Column(String(50))  # HIL, SIL, 实车
    
    host_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("test_hosts.id"))
    device_ids: Mapped[list] = Column(JSONB, default=list)  # List of device UUIDs
    
    status: Mapped[str] = Column(String(20), default="idle", index=True)
    # idle, busy, offline, maintenance, reserved, upgrading
    current_task_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True))
    
    capabilities: Mapped[list] = Column(JSONB, default=list)
    tags: Mapped[list] = Column(JSONB, default=list)
    
    reserved_by: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reserved_until: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    
    project_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    created_by: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    host: Mapped[Optional["TestHost"]] = relationship("TestHost", back_populates="environments")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="environments")
    executions: Mapped[List["TaskExecution"]] = relationship(
        "TaskExecution",
        back_populates="environment"
    )
    
    def __repr__(self):
        return f"<Environment {self.name}>"
    
    @property
    def is_available(self) -> bool:
        """Check if environment is available for tasks"""
        return self.status == "idle"
    
    @property
    def is_reserved(self) -> bool:
        """Check if environment is reserved"""
        if not self.reserved_until:
            return False
        from datetime import timezone
        return datetime.now(timezone.utc) < self.reserved_until
