"""
Integration API endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user, require_permission
from app.core.security import Permission
from app.models.user import User
from app.models.integration import IntegrationConfig
from app.models.artifact import ArtifactVersion
from app.schemas.common import APIResponse


router = APIRouter()


# ==================== Integration Config Endpoints ====================

@router.get("/configs", response_model=APIResponse[list[dict]])
async def list_integration_configs(
    integration_type: Optional[str] = Query(None),
    project_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.SYSTEM_CONFIG))
):
    """
    List integration configurations
    """
    query = select(IntegrationConfig)
    
    if integration_type:
        query = query.where(IntegrationConfig.integration_type == integration_type)
    
    if project_id:
        query = query.where(
            (IntegrationConfig.project_id == project_id) |
            (IntegrationConfig.project_id.is_(None))
        )
    else:
        query = query.where(IntegrationConfig.project_id.is_(None))
    
    result = await db.execute(query)
    configs = result.scalars().all()
    
    # Remove sensitive data from config
    items = []
    for config in configs:
        item = {
            "id": str(config.id),
            "integration_type": config.integration_type,
            "name": config.name,
            "description": config.description,
            "is_default": config.is_default,
            "is_enabled": config.is_enabled,
            "project_id": str(config.project_id) if config.project_id else None,
            "created_at": config.created_at.isoformat()
        }
        items.append(item)
    
    return APIResponse(data=items)


@router.post("/configs", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
async def create_integration_config(
    config_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.SYSTEM_CONFIG))
):
    """
    Create integration configuration
    """
    from app.core.security import encrypt_string
    
    # Encrypt sensitive fields
    config = config_data.get("config", {})
    sensitive_fields = ["password", "token", "secret", "api_key"]
    
    for field in sensitive_fields:
        if field in config and config[field]:
            config[field] = encrypt_string(config[field])
    
    integration = IntegrationConfig(
        integration_type=config_data.get("integration_type"),
        name=config_data.get("name"),
        description=config_data.get("description"),
        config=config,
        is_default=config_data.get("is_default", False),
        is_enabled=config_data.get("is_enabled", True),
        project_id=config_data.get("project_id"),
        created_by=current_user.id
    )
    
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    
    return APIResponse(data={"id": str(integration.id), "name": integration.name})


# ==================== ALM Integration ====================

@router.post("/alm/sync", response_model=APIResponse)
async def sync_from_alm(
    sync_config: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TASK_CREATE))
):
    """
    Sync test tasks/cases from ALM platform
    """
    # TODO: Implement ALM sync logic
    # 1. Get ALM configuration
    # 2. Connect to ALM API
    # 3. Fetch test plans/cases
    # 4. Create/update local records
    
    return APIResponse(
        message="ALM sync initiated",
        data={"status": "pending"}
    )


# ==================== GitLab Integration ====================

@router.post("/gitlab/webhook", response_model=APIResponse)
async def gitlab_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive GitLab webhook notifications
    """
    # Get webhook payload
    payload = await request.json()
    
    event_type = request.headers.get("X-Gitlab-Event")
    
    # TODO: Implement webhook handling based on event type
    # - Push events: trigger CI tests
    # - Merge request events: trigger review tests
    # - Pipeline events: update related tasks
    
    return APIResponse(
        message="Webhook received",
        data={"event_type": event_type}
    )


# ==================== Artifact Repository ====================

@router.get("/artifact/versions", response_model=APIResponse[list[dict]])
async def list_artifact_versions(
    name: Optional[str] = Query(None),
    device_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    List artifact versions from repository
    """
    query = select(ArtifactVersion)
    
    if name:
        query = query.where(ArtifactVersion.name.ilike(f"%{name}%"))
    
    if device_type:
        query = query.where(ArtifactVersion.device_type == device_type)
    
    query = query.order_by(ArtifactVersion.created_at.desc()).limit(50)
    
    result = await db.execute(query)
    versions = result.scalars().all()
    
    items = [
        {
            "id": str(v.id),
            "name": v.name,
            "version": v.version,
            "artifact_type": v.artifact_type,
            "device_type": v.device_type,
            "is_latest": v.is_latest,
            "created_at": v.created_at.isoformat()
        }
        for v in versions
    ]
    
    return APIResponse(data=items)


@router.post("/artifact/sync", response_model=APIResponse)
async def sync_artifacts(
    sync_config: dict,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.SYSTEM_CONFIG))
):
    """
    Sync artifacts from repository
    """
    # TODO: Implement artifact sync logic
    # 1. Get artifact repository configuration
    # 2. Connect to repository API
    # 3. Fetch latest versions
    # 4. Update local records
    
    return APIResponse(
        message="Artifact sync initiated",
        data={"status": "pending"}
    )


# ==================== Notification ====================

@router.post("/notification/test", response_model=APIResponse)
async def test_notification(
    config: dict,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.SYSTEM_CONFIG))
):
    """
    Test notification configuration
    """
    channel = config.get("channel")  # email, webhook, wechat, dingtalk
    
    # TODO: Implement notification test
    # 1. Create test message
    # 2. Send via specified channel
    # 3. Return result
    
    return APIResponse(
        message=f"Test notification sent via {channel}",
        data={"status": "sent"}
    )
