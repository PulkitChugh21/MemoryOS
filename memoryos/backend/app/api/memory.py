"""
MemoryOS Backend — Memory API Routes
Read access to episodic memory (conversation history, sessions).
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.memory.episodic import (
    count_episodes,
    get_recent_episodes,
    get_session_history,
    list_sessions,
)
from app.memory.semantic import get_collection_info
from app.schemas import EpisodeListResponse, EpisodeResponse, SessionListResponse

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.get("/{project_id}/episodes", response_model=EpisodeListResponse)
async def get_episodes(
    project_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=200),
    session_id: uuid.UUID | None = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)
    episodes = await get_recent_episodes(db, project_id, limit=limit, session_id=session_id)
    total = await count_episodes(db, project_id)
    return EpisodeListResponse(
        episodes=[EpisodeResponse.model_validate(ep) for ep in episodes], total=total
    )


@router.get("/{project_id}/sessions", response_model=SessionListResponse)
async def get_sessions(
    project_id: uuid.UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)
    sessions, total = await list_sessions(db, project_id, limit=limit, offset=offset)
    return SessionListResponse(sessions=sessions, total=total)


@router.get("/{project_id}/sessions/{session_id}", response_model=EpisodeListResponse)
async def get_session_detail(
    project_id: uuid.UUID,
    session_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)
    episodes = await get_session_history(db, project_id, session_id)
    return EpisodeListResponse(
        episodes=[EpisodeResponse.model_validate(ep) for ep in episodes], total=len(episodes)
    )


@router.get("/{project_id}/stats")
async def get_memory_stats(
    project_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)
    episode_count = await count_episodes(db, project_id)
    vector_info = await get_collection_info(project_id)
    _, session_count = await list_sessions(db, project_id, limit=0)
    return {
        "project_id": str(project_id),
        "episodic": {"total_episodes": episode_count, "total_sessions": session_count},
        "semantic": vector_info or {"status": "no_collection"},
    }
