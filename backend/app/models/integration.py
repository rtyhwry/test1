"""
IntegrationConfig model
"""
from typing import Optional

from sqlalchemy import Column, String, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped

from app.models.base import BaseModel


class IntegrationConfig(BaseModel):
    """Integration configuration model"""
    
    __tablename__ = "integration_configs"
    
    __table_args__ = (
        UniqueConstraint(
            "integration_type", "name", "project_id",
            name="uq_integration_type_name_project"
        ),
    )
    
    integration_type: Mapped[str] = Column(String(50), nullable=False, index=True)
    # gitlab, alm, artifact, notification
    name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[Optional[str]] = Column(Text)
    
    # Configuration (sensitive fields should be encrypted)
    config: Mapped[dict] = Column(JSONB, nullable=False)
    
    is_default: Mapped[bool] = Column(Boolean, default=False)
    is_enabled: Mapped[bool] = Column(Boolean, default=True)
    
    project_id: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    # null means global config
    
    created_by: Mapped[Optional[UUID]] = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    def __repr__(self):
        return f"<IntegrationConfig {self.integration_type}: {self.name}>"


# Example config structures:
#
# GitLab:
# {
#     "url": "https://gitlab.example.com",
#     "token": "encrypted_token",
#     "default_branch": "main"
# }
#
# ALM:
# {
#     "url": "https://alm.example.com",
#     "username": "user",
#     "password": "encrypted_password",
#     "project_id": "123"
# }
#
# Artifact Repository (Nexus/Artifactory):
# {
#     "type": "nexus",
#     "url": "https://nexus.example.com",
#     "repository": "releases",
#     "username": "user",
#     "password": "encrypted_password"
# }
#
# Email Notification:
# {
#     "smtp_host": "smtp.example.com",
#     "smtp_port": 587,
#     "username": "user",
#     "password": "encrypted_password",
#     "from_email": "noreply@example.com"
# }
#
# Webhook:
# {
#     "url": "https://webhook.example.com/notify",
#     "headers": {"Authorization": "Bearer token"},
#     "timeout": 30
# }
