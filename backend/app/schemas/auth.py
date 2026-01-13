"""
Authentication schemas
"""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """Login request"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)
    login_type: str = Field(default="local", pattern="^(local|ldap)$")


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: "UserBasicInfo"


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserBasicInfo(BaseModel):
    """Basic user info in token response"""
    id: str
    username: str
    email: Optional[str] = None
    role: Optional[str] = None
    display_name: Optional[str] = None
    
    model_config = {"from_attributes": True}


# Update forward reference
TokenResponse.model_rebuild()
