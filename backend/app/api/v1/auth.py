"""
Authentication API endpoints
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
)
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserBasicInfo,
)
from app.schemas.common import APIResponse


router = APIRouter()


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    User login to get access token
    """
    # Find user by username
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if request.login_type == "local":
        if not user.password_hash or not verify_password(
            request.password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
    elif request.login_type == "ldap":
        # TODO: Implement LDAP authentication
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="LDAP authentication not implemented"
        )
    
    # Check user status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login time
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={
            "username": user.username,
            "role": user.role.name if user.role else None
        }
    )
    refresh_token = create_refresh_token(subject=str(user.id))
    
    # Build response
    user_info = UserBasicInfo(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role.name if user.role else None,
        display_name=user.display_name
    )
    
    return APIResponse(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_info
        )
    )


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    payload = decode_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={
            "username": user.username,
            "role": user.role.name if user.role else None
        }
    )
    new_refresh_token = create_refresh_token(subject=str(user.id))
    
    user_info = UserBasicInfo(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role.name if user.role else None,
        display_name=user.display_name
    )
    
    return APIResponse(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_info
        )
    )


@router.post("/logout", response_model=APIResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    User logout (client should discard tokens)
    """
    # In a production system, you might want to:
    # 1. Add the token to a blacklist
    # 2. Invalidate all user sessions
    # For now, we just return success
    return APIResponse(message="Logged out successfully")


@router.get("/me", response_model=APIResponse[UserBasicInfo])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    return APIResponse(
        data=UserBasicInfo(
            id=str(current_user.id),
            username=current_user.username,
            email=current_user.email,
            role=current_user.role.name if current_user.role else None,
            display_name=current_user.display_name
        )
    )
