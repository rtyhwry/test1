"""
Project management API endpoints
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
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.schemas.common import APIResponse, PaginatedResponse, PaginationParams


router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedResponse[ProjectListResponse]])
async def list_projects(
    pagination: PaginationParams = Depends(get_pagination),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PROJECT_READ))
):
    """
    List all projects with pagination
    """
    query = select(Project)
    count_query = select(func.count(Project.id))
    
    # Apply filters
    if status:
        query = query.where(Project.status == status)
        count_query = count_query.where(Project.status == status)
    
    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.where(
            (Project.name.ilike(keyword_filter)) |
            (Project.code.ilike(keyword_filter))
        )
        count_query = count_query.where(
            (Project.name.ilike(keyword_filter)) |
            (Project.code.ilike(keyword_filter))
        )
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(Project.created_at.desc())
    
    result = await db.execute(query)
    projects = result.scalars().all()
    
    items = [ProjectListResponse.model_validate(p) for p in projects]
    
    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
    )


@router.post("", response_model=APIResponse[ProjectResponse], status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PROJECT_CREATE))
):
    """
    Create a new project
    """
    # Check if project code exists
    result = await db.execute(
        select(Project).where(Project.code == project_in.code)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project code already exists"
        )
    
    project = Project(
        name=project_in.name,
        code=project_in.code,
        description=project_in.description,
        owner_id=project_in.owner_id or current_user.id,
        team_members=project_in.team_members,
        settings=project_in.settings,
        created_by=current_user.id
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return APIResponse(data=ProjectResponse.model_validate(project))


@router.get("/{project_id}", response_model=APIResponse[ProjectResponse])
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.PROJECT_READ))
):
    """
    Get project by ID
    """
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.environments),
            selectinload(Project.test_tasks)
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    response = ProjectResponse.model_validate(project)
    response.environment_count = len(project.environments)
    response.task_count = len(project.test_tasks)
    
    return APIResponse(data=response)


@router.put("/{project_id}", response_model=APIResponse[ProjectResponse])
async def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PROJECT_UPDATE))
):
    """
    Update project
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update fields
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    return APIResponse(data=ProjectResponse.model_validate(project))


@router.delete("/{project_id}", response_model=APIResponse)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.PROJECT_DELETE))
):
    """
    Delete project
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    await db.delete(project)
    await db.commit()
    
    return APIResponse(message="Project deleted successfully")
