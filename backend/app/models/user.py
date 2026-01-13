"""
User and Role models
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel


class Role(BaseModel):
    """Role model for RBAC"""
    
    __tablename__ = "roles"
    
    name: Mapped[str] = Column(String(50), unique=True, nullable=False, index=True)
    display_name: Mapped[Optional[str]] = Column(String(100))
    description: Mapped[Optional[str]] = Column(Text)
    permissions: Mapped[list] = Column(JSONB, default=list, nullable=False)
    is_system: Mapped[bool] = Column(Boolean, default=False)
    
    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="role")
    
    def __repr__(self):
        return f"<Role {self.name}>"


class User(BaseModel):
    """User model"""
    
    __tablename__ = "users"
    
    username: Mapped[str] = Column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = Column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = Column(String(255))
    
    role_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    
    display_name: Mapped[Optional[str]] = Column(String(100))
    department: Mapped[Optional[str]] = Column(String(100))
    phone: Mapped[Optional[str]] = Column(String(20))
    avatar_url: Mapped[Optional[str]] = Column(String(500))
    
    ldap_dn: Mapped[Optional[str]] = Column(String(255))
    auth_type: Mapped[str] = Column(String(20), default="local")  # local, ldap, oauth2
    
    status: Mapped[str] = Column(String(20), default="active", index=True)  # active, inactive, locked
    last_login_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    
    # Relationships
    role: Mapped[Optional["Role"]] = relationship("Role", back_populates="users")
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    @property
    def permissions(self) -> list:
        """Get user permissions from role"""
        if self.role:
            return self.role.permissions
        return []
    
    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == "active"
