"""
ArtifactVersion model
"""
from typing import Optional

from sqlalchemy import Column, String, BigInteger, Text, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped

from app.models.base import BaseModel


class ArtifactVersion(BaseModel):
    """Artifact version model"""
    
    __tablename__ = "artifact_versions"
    
    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_artifact_name_version"),
    )
    
    name: Mapped[str] = Column(String(200), nullable=False, index=True)
    version: Mapped[str] = Column(String(50), nullable=False)
    
    artifact_type: Mapped[Optional[str]] = Column(String(50))
    # firmware, software, config
    device_type: Mapped[Optional[str]] = Column(String(50), index=True)
    
    download_url: Mapped[Optional[str]] = Column(String(1000))
    file_size: Mapped[Optional[int]] = Column(BigInteger)
    checksum_md5: Mapped[Optional[str]] = Column(String(32))
    checksum_sha256: Mapped[Optional[str]] = Column(String(64))
    
    release_notes: Mapped[Optional[str]] = Column(Text)
    
    source: Mapped[Optional[str]] = Column(String(50))  # nexus, artifactory, custom
    source_id: Mapped[Optional[str]] = Column(String(200))
    
    is_latest: Mapped[bool] = Column(Boolean, default=False, index=True)
    
    metadata: Mapped[dict] = Column(JSONB, default=dict)
    
    def __repr__(self):
        return f"<ArtifactVersion {self.name}:{self.version}>"
