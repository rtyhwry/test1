"""
Health check endpoints
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.api.deps import get_db
from app.core.config import settings


router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint
    """
    services = {
        "database": "healthy",
        "redis": "unknown",
        "rabbitmq": "unknown",
        "storage": "unknown"
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        services["database"] = "unhealthy"
    
    # TODO: Check Redis connection
    # TODO: Check RabbitMQ connection
    # TODO: Check MinIO connection
    
    overall_status = "healthy" if all(
        s == "healthy" or s == "unknown" for s in services.values()
    ) else "unhealthy"
    
    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": services
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check endpoint for Kubernetes
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes
    """
    return {"status": "alive"}
