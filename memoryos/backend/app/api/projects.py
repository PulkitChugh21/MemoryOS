"""
MemoryOS Backend — Projects API Routes
CRUD for projects, scoped to the authenticated user.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import get_current_user_id
from app.db.models import Project
from app.db.session import get_db
from app.memory.semantic import ensure_collection, delete_collection
from app.schemas import (
    ErrorResponse,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

logger = get_logger("api.projects")
router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
async def create_project(
    payload: ProjectCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project workspace."""
    uid = uuid.UUID(user_id)

    # Check for duplicate project name per user
    result = await db.execute(
        select(Project).where(
            Project.owner_id == uid,
            Project.name == payload.name,
            Project.status != "deleted",
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "PROJECT_EXISTS",
                    "message": f"A project named '{payload.name}' already exists.",
                    "details": {},
                }
            },
        )

    project = Project(
        id=uuid.uuid4(),
        owner_id=uid,
        name=payload.name,
        description=payload.description,
        tech_stack=payload.tech_stack,
        project_type=payload.project_type,
    )
    db.add(project)
    await db.flush()

    # Create the Qdrant collection for this project
    await ensure_collection(project.id)

    logger.info(
        "project_created",
        project_id=str(project.id),
        user_id=user_id,
        name=project.name,
    )

    return ProjectResponse.model_validate(project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all active projects for the authenticated user."""
    uid = uuid.UUID(user_id)

    result = await db.execute(
        select(Project)
        .where(Project.owner_id == uid, Project.status != "deleted")
        .order_by(Project.updated_at.desc())
    )
    projects = list(result.scalars().all())

    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=len(projects),
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_project(
    project_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific project by ID."""
    project = await _get_user_project(db, project_id, user_id)
    return ProjectResponse.model_validate(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    responses={404: {"model": ErrorResponse}},
)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update project details."""
    project = await _get_user_project(db, project_id, user_id)

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    await db.flush()

    logger.info(
        "project_updated",
        project_id=str(project_id),
        fields=list(update_data.keys()),
    )

    return ProjectResponse.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
async def delete_project(
    project_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft-delete a project (set status to 'deleted').
    Also removes the Qdrant collection.
    """
    project = await _get_user_project(db, project_id, user_id)
    project.status = "deleted"
    await db.flush()

    # Clean up Qdrant collection
    await delete_collection(project_id)

    logger.info("project_deleted", project_id=str(project_id))


# --- Helpers ---

async def _get_user_project(
    db: AsyncSession, project_id: uuid.UUID, user_id: str
) -> Project:
    """
    Get a project, ensuring it belongs to the authenticated user.
    Enforces user isolation (Rules.md §2).
    """
    uid = uuid.UUID(user_id)
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == uid,
            Project.status != "deleted",
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "PROJECT_NOT_FOUND",
                    "message": "Project not found or access denied.",
                    "details": {},
                }
            },
        )

    return project
