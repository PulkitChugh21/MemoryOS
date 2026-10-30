"""
MemoryOS Backend — Memory API Routes
Phase 1: Episodic memory (conversation history, sessions).
Phase 2: Structured facts + timeline.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.db.models import MemoryFact, ProjectFile
from app.memory.episodic import (
    count_episodes,
    get_recent_episodes,
    get_session_history,
    list_sessions,
)
from app.memory.semantic import get_collection_info
from app.memory.structured import count_facts, get_facts, get_fact_by_id
from app.schemas import (
    EpisodeListResponse,
    EpisodeResponse,
    FactListResponse,
    FactResponse,
    SessionListResponse,
    TimelineEvent,
    TimelineResponse,
)

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


# ===========================
# Facts Endpoints (Phase 2)
# ===========================

@router.get("/{project_id}/facts", response_model=FactListResponse)
async def get_project_facts(
    project_id: uuid.UUID,
    fact_type: str | None = Query(default=None),
    include_stale: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=500),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all structured facts for a project, optionally filtered by type."""
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)
    facts = await get_facts(db, project_id, fact_type=fact_type, include_stale=include_stale, limit=limit)
    total = await count_facts(db, project_id, include_stale=include_stale)
    return FactListResponse(
        facts=[FactResponse.model_validate(f) for f in facts], total=total
    )


@router.get("/{project_id}/facts/{fact_id}", response_model=FactResponse)
async def get_fact(
    project_id: uuid.UUID,
    fact_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific fact by ID."""
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)
    fact = await get_fact_by_id(db, project_id, fact_id)
    if not fact:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "FACT_NOT_FOUND", "message": "Fact not found.", "details": {}}},
        )
    return FactResponse.model_validate(fact)


# ===========================
# Timeline Endpoint (Phase 2)
# ===========================

@router.get("/{project_id}/timeline", response_model=TimelineResponse)
async def get_timeline(
    project_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=200),
    event_type: str | None = Query(default=None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get combined timeline events for a project.
    Merges conversation sessions, file uploads, and fact extractions
    into a single chronological feed.
    """
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)

    events: list[TimelineEvent] = []

    # Conversation events (session starts)
    if not event_type or event_type == "conversation":
        sessions, _ = await list_sessions(db, project_id, limit=limit)
        for s in sessions:
            events.append(TimelineEvent(
                event_type="conversation",
                event_id=uuid.UUID(s["session_id"]),
                title=s["first_message"][:100] if s["first_message"] else "New conversation",
                description=f"{s['turn_count']} messages",
                timestamp=datetime.fromisoformat(s["started_at"]),
                metadata={"turn_count": s["turn_count"], "session_id": s["session_id"]},
            ))

    # File events
    if not event_type or event_type in ("file_upload", "file_update"):
        file_result = await db.execute(
            select(ProjectFile)
            .where(ProjectFile.project_id == project_id)
            .order_by(ProjectFile.uploaded_at.desc())
            .limit(limit)
        )
        for f in file_result.scalars().all():
            evt_type = "file_update" if f.version > 1 else "file_upload"
            events.append(TimelineEvent(
                event_type=evt_type,
                event_id=f.id,
                title=f"{'Updated' if f.version > 1 else 'Uploaded'}: {f.filename}",
                description=f.diff_summary or f"v{f.version} — {f.size_bytes} bytes, {f.chunk_count} chunks",
                timestamp=f.uploaded_at,
                metadata={"filename": f.filename, "version": f.version, "size_bytes": f.size_bytes},
            ))

    # Fact events
    if not event_type or event_type == "fact_extracted":
        fact_result = await db.execute(
            select(MemoryFact)
            .where(MemoryFact.project_id == project_id)
            .order_by(MemoryFact.created_at.desc())
            .limit(limit)
        )
        for fact in fact_result.scalars().all():
            events.append(TimelineEvent(
                event_type="fact_extracted",
                event_id=fact.id,
                title=f"[{fact.fact_type}] {fact.key}",
                description=fact.value[:200],
                timestamp=fact.created_at,
                metadata={"fact_type": fact.fact_type, "confidence": fact.confidence, "source": fact.source},
            ))

    # Sort all events by timestamp descending
    events.sort(key=lambda e: e.timestamp, reverse=True)
    events = events[:limit]

    return TimelineResponse(events=events, total=len(events))


# ===========================
# Stats Endpoint (Updated)
# ===========================

@router.get("/{project_id}/stats")
async def get_memory_stats(
    project_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Memory stats including episodic, semantic, structured, and file counts."""
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)

    episode_count = await count_episodes(db, project_id)
    vector_info = await get_collection_info(project_id)
    _, session_count = await list_sessions(db, project_id, limit=0)
    fact_count = await count_facts(db, project_id)

    # File count
    file_result = await db.execute(
        select(func.count(ProjectFile.id)).where(
            ProjectFile.project_id == project_id,
            ProjectFile.is_current == True,  # noqa: E712
        )
    )
    file_count = file_result.scalar() or 0

    return {
        "project_id": str(project_id),
        "episodic": {"total_episodes": episode_count, "total_sessions": session_count},
        "semantic": vector_info or {"status": "no_collection"},
        "structured": {"total_facts": fact_count},
        "files": {"total_files": file_count},
    }
