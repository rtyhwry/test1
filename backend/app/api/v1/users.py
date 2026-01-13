"""
User management API endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db, get_current_user, get_pagination, require_permission
from app.core.security import get_password_hash, Permission
from app.models.user import User, Role
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
)
from app.schemas.common import APIResponse, PaginatedResponse, PaginationParams


router = APIRouter()


# ==================== User Endpoints ====================

@router.get("", response_model=APIResponse[PaginatedResponse[UserListResponse]])
async def list_users(
    pagination: PaginationParams = Depends(get_pagination),
    status: Optional[str] = Query(None),
    role_id: Optional[UUID] = Query(None),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.USER_READ))
):
    """
    List all users with pagination
    """
    query = select(User)
    count_query = select(func.count(User.id))
    
    # Apply filters
    if status:
        query = query.where(User.status == status)
        count_query = count_query.where(User.status == status)
    
    if role_id:
        query = query.where(User.role_id == role_id)
        count_query = count_query.where(User.role_id == role_id)
    
    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.where(
            (User.username.ilike(keyword_filter)) |
            (User.email.ilike(keyword_filter)) |
            (User.display_name.ilike(keyword_filter))
        )
        count_query = count_query.where(
            (User.username.ilike(keyword_filter)) |
            (User.email.ilike(keyword_filter)) |
            (User.display_name.ilike(keyword_filter))
        )
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    items = [UserListResponse.model_validate(u) for u in users]
    
    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
    )


@router.post("", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_CREATE))
):
    """
    Create a new user
    """
    # Check if username exists
    result = await db.execute(
        select(User).where(User.username == user_in.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    result = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create user
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        display_name=user_in.display_name,
        department=user_in.department,
        phone=user_in.phone,
        role_id=user_in.role_id,
        auth_type=user_in.auth_type
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return APIResponse(data=UserResponse.model_validate(user))


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.USER_READ))
):
    """
    Get user by ID
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return APIResponse(data=UserResponse.model_validate(user))


@router.put("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_UPDATE))
):
    """
    Update user
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return APIResponse(data=UserResponse.model_validate(user))


@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_DELETE))
):
    """
    Delete user
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.delete(user)
    await db.commit()
    
    return APIResponse(message="User deleted successfully")


# ==================== Role Endpoints ====================

@router.get("/roles", response_model=APIResponse[list[RoleResponse]])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    List all roles
    """
    result = await db.execute(select(Role).order_by(Role.name))
    roles = result.scalars().all()
    
    return APIResponse(
        data=[RoleResponse.model_validate(r) for r in roles]
    )


@router.post("/roles", response_model=APIResponse[RoleResponse], status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.USER_ALL))
):
    """
    Create a new role
    """
    # Check if role name exists
    result = await db.execute(
        select(Role).where(Role.name == role_in.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )
    
    role = Role(
        name=role_in.name,
        display_name=role_in.display_name,
        description=role_in.description,
        permissions=role_in.permissions
    )
    
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    return APIResponse(data=RoleResponse.model_validate(role))


@router.put("/roles/{role_id}", response_model=APIResponse[RoleResponse])
async def update_role(
    role_id: UUID,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.USER_ALL))
):
    """
    Update role
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify system role"
        )
    
    # Update fields
    update_data = role_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)
    
    await db.commit()
    await db.refresh(role)
    
    return APIResponse(data=RoleResponse.model_validate(role))
