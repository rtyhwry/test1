"""
Application configuration
"""
from functools import lru_cache
from typing import List, Optional
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "EV Test Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/evtest"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_RECYCLE: int = 3600
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TASK_QUEUE_DB: int = 1
    REDIS_CACHE_DB: int = 2
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # JWT Authentication
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password Hashing
    PASSWORD_HASH_ROUNDS: int = 12
    
    # File Storage (MinIO)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_REPORTS: str = "test-reports"
    MINIO_BUCKET_LOGS: str = "test-logs"
    MINIO_BUCKET_ARTIFACTS: str = "artifacts"
    
    # GitLab Integration
    GITLAB_URL: Optional[str] = None
    GITLAB_TOKEN: Optional[str] = None
    
    # ALM Integration
    ALM_URL: Optional[str] = None
    ALM_USERNAME: Optional[str] = None
    ALM_PASSWORD: Optional[str] = None
    
    # Artifact Repository
    ARTIFACT_REPO_URL: Optional[str] = None
    ARTIFACT_REPO_USERNAME: Optional[str] = None
    ARTIFACT_REPO_PASSWORD: Optional[str] = None
    
    # Notification
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@evtest.example.com"
    
    WEBHOOK_TIMEOUT: int = 30
    
    # Task Execution
    DEFAULT_TASK_TIMEOUT: int = 3600  # 1 hour
    MAX_TASK_TIMEOUT: int = 86400  # 24 hours
    DEFAULT_CASE_TIMEOUT: int = 300  # 5 minutes
    
    # Scheduler
    SCHEDULER_CHECK_INTERVAL: int = 5  # seconds
    SCHEDULER_MAX_CONCURRENT_TASKS: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Encryption key for sensitive data
    ENCRYPTION_KEY: str = "your-encryption-key-32-bytes-long"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL"""
        return self.DATABASE_URL.replace("+asyncpg", "")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
