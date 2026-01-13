"""
Pydantic schemas for API request/response validation
"""
from app.schemas.common import (
    PaginationParams,
    PaginatedResponse,
    APIResponse,
    ErrorDetail,
)
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
from app.schemas.environment import (
    TestHostCreate,
    TestHostUpdate,
    TestHostResponse,
    TestDeviceCreate,
    TestDeviceUpdate,
    TestDeviceResponse,
    EnvironmentCreate,
    EnvironmentUpdate,
    EnvironmentResponse,
)
from app.schemas.test_suite import (
    TestSuiteCreate,
    TestSuiteUpdate,
    TestSuiteResponse,
    TestCaseCreate,
    TestCaseUpdate,
    TestCaseResponse,
)
from app.schemas.task import (
    TestTaskCreate,
    TestTaskUpdate,
    TestTaskResponse,
    TaskExecutionResponse,
    TestCaseResultResponse,
    TaskAction,
)
from app.schemas.report import (
    TestReportResponse,
    ReportStatistics,
)

__all__ = [
    # Common
    "PaginationParams",
    "PaginatedResponse",
    "APIResponse",
    "ErrorDetail",
    # Auth
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    # Environment
    "TestHostCreate",
    "TestHostUpdate",
    "TestHostResponse",
    "TestDeviceCreate",
    "TestDeviceUpdate",
    "TestDeviceResponse",
    "EnvironmentCreate",
    "EnvironmentUpdate",
    "EnvironmentResponse",
    # Test Suite
    "TestSuiteCreate",
    "TestSuiteUpdate",
    "TestSuiteResponse",
    "TestCaseCreate",
    "TestCaseUpdate",
    "TestCaseResponse",
    # Task
    "TestTaskCreate",
    "TestTaskUpdate",
    "TestTaskResponse",
    "TaskExecutionResponse",
    "TestCaseResultResponse",
    "TaskAction",
    # Report
    "TestReportResponse",
    "ReportStatistics",
]
