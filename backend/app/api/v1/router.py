"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    projects,
    environments,
    test_suites,
    tasks,
    reports,
    integrations,
    health,
)

api_router = APIRouter()

# Include all routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["Projects"]
)
api_router.include_router(
    environments.router,
    prefix="/environments",
    tags=["Environments"]
)
api_router.include_router(
    test_suites.router,
    prefix="/test-suites",
    tags=["Test Suites"]
)
api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"]
)
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"]
)
api_router.include_router(
    integrations.router,
    prefix="/integrations",
    tags=["Integrations"]
)
api_router.include_router(
    health.router,
    tags=["Health"]
)
