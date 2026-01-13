"""
Environment management API endpoints
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user, get_pagination, require_permission
from app.core.security import Permission
from app.models.user import User
from app.models.environment import Environment, TestHost, TestDevice
from app.schemas.environment import (
    EnvironmentCreate,
    EnvironmentUpdate,
    EnvironmentResponse,
    EnvironmentActionRequest,
    EnvironmentReserveRequest,
    TestHostCreate,
    TestHostUpdate,
    TestHostResponse,
    TestDeviceCreate,
    TestDeviceUpdate,
    TestDeviceResponse,
)
from app.schemas.common import APIResponse, PaginatedResponse, PaginationParams


router = APIRouter()


# ==================== Environment Endpoints ====================

@router.get("", response_model=APIResponse[PaginatedResponse[EnvironmentResponse]])
async def list_environments(
    pagination: PaginationParams = Depends(get_pagination),
    project_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    env_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.ENV_READ))
):
    """
    List all environments with pagination
    """
    query = select(Environment).options(selectinload(Environment.host))
    count_query = select(func.count(Environment.id))
    
    # Apply filters
    if project_id:
        query = query.where(Environment.project_id == project_id)
        count_query = count_query.where(Environment.project_id == project_id)
    
    if status:
        query = query.where(Environment.status == status)
        count_query = count_query.where(Environment.status == status)
    
    if env_type:
        query = query.where(Environment.env_type == env_type)
        count_query = count_query.where(Environment.env_type == env_type)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(Environment.created_at.desc())
    
    result = await db.execute(query)
    environments = result.scalars().all()
    
    items = [EnvironmentResponse.model_validate(e) for e in environments]
    
    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
    )


@router.post("", response_model=APIResponse[EnvironmentResponse], status_code=status.HTTP_201_CREATED)
async def create_environment(
    env_in: EnvironmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ENV_CREATE))
):
    """
    Create a new environment
    """
    environment = Environment(
        name=env_in.name,
        description=env_in.description,
        env_type=env_in.env_type,
        host_id=env_in.host_id,
        device_ids=[str(d) for d in env_in.device_ids],
        project_id=env_in.project_id,
        capabilities=env_in.capabilities,
        tags=env_in.tags,
        created_by=current_user.id
    )
    
    db.add(environment)
    await db.commit()
    await db.refresh(environment)
    
    return APIResponse(data=EnvironmentResponse.model_validate(environment))


@router.get("/{env_id}", response_model=APIResponse[EnvironmentResponse])
async def get_environment(
    env_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.ENV_READ))
):
    """
    Get environment by ID
    """
    result = await db.execute(
        select(Environment)
        .where(Environment.id == env_id)
        .options(selectinload(Environment.host))
    )
    environment = result.scalar_one_or_none()
    
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment not found"
        )
    
    return APIResponse(data=EnvironmentResponse.model_validate(environment))


@router.put("/{env_id}", response_model=APIResponse[EnvironmentResponse])
async def update_environment(
    env_id: UUID,
    env_in: EnvironmentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.ENV_UPDATE))
):
    """
    Update environment
    """
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    environment = result.scalar_one_or_none()
    
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment not found"
        )
    
    # Update fields
    update_data = env_in.model_dump(exclude_unset=True)
    if "device_ids" in update_data:
        update_data["device_ids"] = [str(d) for d in update_data["device_ids"]]
    
    for field, value in update_data.items():
        setattr(environment, field, value)
    
    await db.commit()
    await db.refresh(environment)
    
    return APIResponse(data=EnvironmentResponse.model_validate(environment))


@router.delete("/{env_id}", response_model=APIResponse)
async def delete_environment(
    env_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.ENV_DELETE))
):
    """
    Delete environment
    """
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    environment = result.scalar_one_or_none()
    
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment not found"
        )
    
    if environment.status == "busy":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete busy environment"
        )
    
    await db.delete(environment)
    await db.commit()
    
    return APIResponse(message="Environment deleted successfully")


@router.post("/{env_id}/actions", response_model=APIResponse)
async def environment_action(
    env_id: UUID,
    action_in: EnvironmentActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ENV_UPDATE))
):
    """
    Perform action on environment
    """
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    environment = result.scalar_one_or_none()
    
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment not found"
        )
    
    if action_in.action == "maintenance":
        environment.status = "maintenance"
    elif action_in.action == "release":
        environment.status = "idle"
        environment.reserved_by = None
        environment.reserved_until = None
    
    await db.commit()
    
    return APIResponse(message=f"Action '{action_in.action}' completed")


@router.post("/{env_id}/reserve", response_model=APIResponse)
async def reserve_environment(
    env_id: UUID,
    reserve_in: EnvironmentReserveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ENV_UPDATE))
):
    """
    Reserve environment for specific time period
    """
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    environment = result.scalar_one_or_none()
    
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment not found"
        )
    
    if environment.status not in ["idle", "reserved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reserve environment in '{environment.status}' status"
        )
    
    environment.status = "reserved"
    environment.reserved_by = current_user.id
    environment.reserved_until = reserve_in.end_time
    
    await db.commit()
    
    return APIResponse(message="Environment reserved successfully")


# ==================== TestHost Endpoints ====================

@router.get("/hosts", response_model=APIResponse[list[TestHostResponse]])
async def list_hosts(
    project_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.ENV_READ))
):
    """
    List all test hosts
    """
    query = select(TestHost)
    
    if project_id:
        query = query.where(TestHost.project_id == project_id)
    if status:
        query = query.where(TestHost.status == status)
    
    query = query.order_by(TestHost.name)
    result = await db.execute(query)
    hosts = result.scalars().all()
    
    return APIResponse(data=[TestHostResponse.model_validate(h) for h in hosts])


@router.post("/hosts", response_model=APIResponse[TestHostResponse], status_code=status.HTTP_201_CREATED)
async def create_host(
    host_in: TestHostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ENV_CREATE))
):
    """
    Create a new test host
    """
    from app.core.security import encrypt_string
    
    host = TestHost(
        name=host_in.name,
        description=host_in.description,
        ip_address=host_in.ip_address,
        ssh_port=host_in.ssh_port,
        username=host_in.username,
        auth_type=host_in.auth_type,
        password_encrypted=encrypt_string(host_in.password) if host_in.password else None,
        ssh_key_encrypted=encrypt_string(host_in.ssh_key) if host_in.ssh_key else None,
        work_directory=host_in.work_directory,
        capabilities=host_in.capabilities,
        tags=host_in.tags,
        max_concurrent_tasks=host_in.max_concurrent_tasks,
        project_id=host_in.project_id,
        created_by=current_user.id
    )
    
    db.add(host)
    await db.commit()
    await db.refresh(host)
    
    return APIResponse(data=TestHostResponse.model_validate(host))


# ==================== TestDevice Endpoints ====================

@router.get("/devices", response_model=APIResponse[list[TestDeviceResponse]])
async def list_devices(
    host_id: Optional[UUID] = Query(None),
    project_id: Optional[UUID] = Query(None),
    device_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.ENV_READ))
):
    """
    List all test devices
    """
    query = select(TestDevice)
    
    if host_id:
        query = query.where(TestDevice.host_id == host_id)
    if project_id:
        query = query.where(TestDevice.project_id == project_id)
    if device_type:
        query = query.where(TestDevice.device_type == device_type)
    
    query = query.order_by(TestDevice.name)
    result = await db.execute(query)
    devices = result.scalars().all()
    
    return APIResponse(data=[TestDeviceResponse.model_validate(d) for d in devices])


@router.post("/devices", response_model=APIResponse[TestDeviceResponse], status_code=status.HTTP_201_CREATED)
async def create_device(
    device_in: TestDeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ENV_CREATE))
):
    """
    Create a new test device
    """
    device = TestDevice(
        name=device_in.name,
        description=device_in.description,
        device_type=device_in.device_type,
        model=device_in.model,
        serial_number=device_in.serial_number,
        host_id=device_in.host_id,
        connection_type=device_in.connection_type,
        connection_config=device_in.connection_config,
        capabilities=device_in.capabilities,
        tags=device_in.tags,
        project_id=device_in.project_id,
        created_by=current_user.id
    )
    
    db.add(device)
    await db.commit()
    await db.refresh(device)
    
    return APIResponse(data=TestDeviceResponse.model_validate(device))
