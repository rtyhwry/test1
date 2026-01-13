"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64
import hashlib

from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """Create a JWT access token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.now(timezone.utc)
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT refresh token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.now(timezone.utc)
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def get_encryption_key() -> bytes:
    """Get or derive encryption key from settings"""
    key = settings.ENCRYPTION_KEY.encode()
    # Derive a 32-byte key using SHA256
    return base64.urlsafe_b64encode(hashlib.sha256(key).digest())


def encrypt_string(plain_text: str) -> str:
    """Encrypt a string"""
    if not plain_text:
        return plain_text
    
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(plain_text.encode())
    return encrypted.decode()


def decrypt_string(encrypted_text: str) -> str:
    """Decrypt a string"""
    if not encrypted_text:
        return encrypted_text
    
    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_text.encode())
        return decrypted.decode()
    except Exception:
        return encrypted_text


class Permission:
    """Permission constants"""
    # Task permissions
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_EXECUTE = "task:execute"
    TASK_ALL = "task:*"
    
    # Environment permissions
    ENV_CREATE = "env:create"
    ENV_READ = "env:read"
    ENV_UPDATE = "env:update"
    ENV_DELETE = "env:delete"
    ENV_ALL = "env:*"
    
    # Report permissions
    REPORT_READ = "report:read"
    REPORT_EXPORT = "report:export"
    REPORT_ALL = "report:*"
    
    # Project permissions
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_ALL = "project:*"
    
    # User management permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_ALL = "user:*"
    
    # System permissions
    SYSTEM_CONFIG = "system:config"
    SYSTEM_ALL = "system:*"
    
    # Super admin
    ALL = "*"


def check_permission(user_permissions: list, required_permission: str) -> bool:
    """Check if user has required permission"""
    if Permission.ALL in user_permissions:
        return True
    
    if required_permission in user_permissions:
        return True
    
    # Check wildcard permissions (e.g., task:* includes task:read)
    permission_category = required_permission.split(":")[0]
    wildcard_permission = f"{permission_category}:*"
    
    return wildcard_permission in user_permissions


# Role definitions
ROLE_PERMISSIONS = {
    "admin": [Permission.ALL],
    "manager": [
        Permission.TASK_ALL,
        Permission.ENV_ALL,
        Permission.REPORT_ALL,
        Permission.PROJECT_READ,
        Permission.USER_READ
    ],
    "engineer": [
        Permission.TASK_READ,
        Permission.TASK_CREATE,
        Permission.TASK_EXECUTE,
        Permission.ENV_READ,
        Permission.REPORT_READ,
        Permission.REPORT_EXPORT,
        Permission.PROJECT_READ
    ],
    "viewer": [
        Permission.TASK_READ,
        Permission.ENV_READ,
        Permission.REPORT_READ
    ]
}
