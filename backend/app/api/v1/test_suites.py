"""
Test Suite and Test Case API endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user, get_pagination, require_permission
from app.core.security import Permission
from app.models.user import User
from app.models.test_suite import TestSuite, TestCase
from app.schemas.test_suite import (
    TestSuiteCreate,
    TestSuiteUpdate,
    TestSuiteResponse,
    TestCaseCreate,
    TestCaseUpdate,
    TestCaseResponse,
    TestCaseListResponse,
)
from app.schemas.common import APIResponse, PaginatedResponse, PaginationParams


router = APIRouter()


# ==================== Test Suite Endpoints ====================

@router.get("", response_model=APIResponse[PaginatedResponse[TestSuiteResponse]])
async def list_test_suites(
    pagination: PaginationParams = Depends(get_pagination),
    project_id: Optional[UUID] = Query(None),
    source: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_READ))
):
    """
    List all test suites with pagination
    """
    query = select(TestSuite).options(selectinload(TestSuite.test_cases))
    count_query = select(func.count(TestSuite.id))
    
    if project_id:
        query = query.where(TestSuite.project_id == project_id)
        count_query = count_query.where(TestSuite.project_id == project_id)
    
    if source:
        query = query.where(TestSuite.source == source)
        count_query = count_query.where(TestSuite.source == source)
    
    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.where(TestSuite.name.ilike(keyword_filter))
        count_query = count_query.where(TestSuite.name.ilike(keyword_filter))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(TestSuite.created_at.desc())
    
    result = await db.execute(query)
    suites = result.scalars().all()
    
    items = []
    for suite in suites:
        response = TestSuiteResponse.model_validate(suite)
        response.case_count = len(suite.test_cases)
        items.append(response)
    
    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
    )


@router.post("", response_model=APIResponse[TestSuiteResponse], status_code=status.HTTP_201_CREATED)
async def create_test_suite(
    suite_in: TestSuiteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TASK_CREATE))
):
    """
    Create a new test suite
    """
    suite = TestSuite(
        name=suite_in.name,
        description=suite_in.description,
        project_id=suite_in.project_id,
        source=suite_in.source,
        alm_suite_id=suite_in.alm_suite_id,
        git_repo=suite_in.git_repo,
        git_branch=suite_in.git_branch,
        git_path=suite_in.git_path,
        framework=suite_in.framework,
        setup_commands=suite_in.setup_commands,
        teardown_commands=suite_in.teardown_commands,
        tags=suite_in.tags,
        created_by=current_user.id
    )
    
    db.add(suite)
    await db.commit()
    await db.refresh(suite)
    
    return APIResponse(data=TestSuiteResponse.model_validate(suite))


@router.get("/{suite_id}", response_model=APIResponse[TestSuiteResponse])
async def get_test_suite(
    suite_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_READ))
):
    """
    Get test suite by ID
    """
    result = await db.execute(
        select(TestSuite)
        .where(TestSuite.id == suite_id)
        .options(selectinload(TestSuite.test_cases))
    )
    suite = result.scalar_one_or_none()
    
    if not suite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test suite not found"
        )
    
    response = TestSuiteResponse.model_validate(suite)
    response.case_count = len(suite.test_cases)
    
    return APIResponse(data=response)


@router.put("/{suite_id}", response_model=APIResponse[TestSuiteResponse])
async def update_test_suite(
    suite_id: UUID,
    suite_in: TestSuiteUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_UPDATE))
):
    """
    Update test suite
    """
    result = await db.execute(select(TestSuite).where(TestSuite.id == suite_id))
    suite = result.scalar_one_or_none()
    
    if not suite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test suite not found"
        )
    
    update_data = suite_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(suite, field, value)
    
    await db.commit()
    await db.refresh(suite)
    
    return APIResponse(data=TestSuiteResponse.model_validate(suite))


@router.delete("/{suite_id}", response_model=APIResponse)
async def delete_test_suite(
    suite_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_DELETE))
):
    """
    Delete test suite
    """
    result = await db.execute(select(TestSuite).where(TestSuite.id == suite_id))
    suite = result.scalar_one_or_none()
    
    if not suite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test suite not found"
        )
    
    await db.delete(suite)
    await db.commit()
    
    return APIResponse(message="Test suite deleted successfully")


@router.post("/{suite_id}/sync", response_model=APIResponse)
async def sync_test_suite(
    suite_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TASK_UPDATE))
):
    """
    Sync test cases from GitLab or ALM
    """
    result = await db.execute(select(TestSuite).where(TestSuite.id == suite_id))
    suite = result.scalar_one_or_none()
    
    if not suite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test suite not found"
        )
    
    # TODO: Implement sync logic based on source
    # This would involve calling GitLab API or ALM API
    
    return APIResponse(message="Sync task submitted")


# ==================== Test Case Endpoints ====================

@router.get("/{suite_id}/cases", response_model=APIResponse[PaginatedResponse[TestCaseListResponse]])
async def list_test_cases(
    suite_id: UUID,
    pagination: PaginationParams = Depends(get_pagination),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_READ))
):
    """
    List test cases in a suite
    """
    # Verify suite exists
    suite_result = await db.execute(select(TestSuite).where(TestSuite.id == suite_id))
    if not suite_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test suite not found"
        )
    
    query = select(TestCase).where(TestCase.suite_id == suite_id)
    count_query = select(func.count(TestCase.id)).where(TestCase.suite_id == suite_id)
    
    if priority:
        query = query.where(TestCase.priority == priority)
        count_query = count_query.where(TestCase.priority == priority)
    
    if status:
        query = query.where(TestCase.status == status)
        count_query = count_query.where(TestCase.status == status)
    
    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.where(TestCase.name.ilike(keyword_filter))
        count_query = count_query.where(TestCase.name.ilike(keyword_filter))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(TestCase.created_at.desc())
    
    result = await db.execute(query)
    cases = result.scalars().all()
    
    items = [TestCaseListResponse.model_validate(c) for c in cases]
    
    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
    )


@router.post("/cases", response_model=APIResponse[TestCaseResponse], status_code=status.HTTP_201_CREATED)
async def create_test_case(
    case_in: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TASK_CREATE))
):
    """
    Create a new test case
    """
    # Verify suite exists
    suite_result = await db.execute(select(TestSuite).where(TestSuite.id == case_in.suite_id))
    if not suite_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test suite not found"
        )
    
    case = TestCase(
        suite_id=case_in.suite_id,
        name=case_in.name,
        description=case_in.description,
        alm_case_id=case_in.alm_case_id,
        priority=case_in.priority,
        case_type=case_in.case_type,
        script_path=case_in.script_path,
        class_name=case_in.class_name,
        method_name=case_in.method_name,
        parameters=case_in.parameters,
        timeout=case_in.timeout,
        retry_count=case_in.retry_count,
        preconditions=case_in.preconditions,
        steps=case_in.steps,
        expected_results=case_in.expected_results,
        tags=case_in.tags,
        capabilities_required=case_in.capabilities_required,
        is_automated=case_in.is_automated,
        created_by=current_user.id
    )
    
    db.add(case)
    await db.commit()
    await db.refresh(case)
    
    return APIResponse(data=TestCaseResponse.model_validate(case))


@router.get("/cases/{case_id}", response_model=APIResponse[TestCaseResponse])
async def get_test_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_READ))
):
    """
    Get test case by ID
    """
    result = await db.execute(select(TestCase).where(TestCase.id == case_id))
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )
    
    return APIResponse(data=TestCaseResponse.model_validate(case))


@router.put("/cases/{case_id}", response_model=APIResponse[TestCaseResponse])
async def update_test_case(
    case_id: UUID,
    case_in: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_UPDATE))
):
    """
    Update test case
    """
    result = await db.execute(select(TestCase).where(TestCase.id == case_id))
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )
    
    update_data = case_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)
    
    await db.commit()
    await db.refresh(case)
    
    return APIResponse(data=TestCaseResponse.model_validate(case))


@router.delete("/cases/{case_id}", response_model=APIResponse)
async def delete_test_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.TASK_DELETE))
):
    """
    Delete test case
    """
    result = await db.execute(select(TestCase).where(TestCase.id == case_id))
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found"
        )
    
    await db.delete(case)
    await db.commit()
    
    return APIResponse(message="Test case deleted successfully")
