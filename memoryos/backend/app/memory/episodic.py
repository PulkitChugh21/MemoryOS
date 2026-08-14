"""
MemoryOS Backend — Episodic Memory (Tier 1)
Read/write conversation turns to PostgreSQL.
Every query is scoped by project_id (Rules.md §2).
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import MemoryEpisode

logger = get_logger("memory.episodic")


async def store_episode(
    db: AsyncSession,
    project_id: uuid.UUID,
    session_id: uuid.UUID,
    role: str,
    content: str,
    embedding_id: Optional[str] = None,
    token_count: int = 0,
    confidence: float = 1.0,
) -> MemoryEpisode:
    """
    Store a single conversation turn in episodic memory.
    Both user messages and assistant responses are stored.
    """
    episode = MemoryEpisode(
        id=uuid.uuid4(),
        project_id=project_id,
        session_id=session_id,
        role=role,
        content=content,
        embedding_id=embedding_id,
        token_count=token_count,
        confidence=confidence,
        created_at=datetime.now(timezone.utc),
    )
    db.add(episode)
    await db.flush()

    logger.info(
        "episode_stored",
        project_id=str(project_id),
        session_id=str(session_id),
        role=role,
        token_count=token_count,
    )

    return episode


async def get_recent_episodes(
    db: AsyncSession,
    project_id: uuid.UUID,
    limit: int = 50,
    session_id: Optional[uuid.UUID] = None,
) -> list[MemoryEpisode]:
    """
    Retrieve recent conversation turns for a project.
    If session_id is provided, only returns turns from that session.
    Always scoped by project_id (Rules.md §2).
    """
    query = (
        select(MemoryEpisode)
        .where(MemoryEpisode.project_id == project_id)
        .order_by(MemoryEpisode.created_at.desc())
        .limit(limit)
    )

    if session_id:
        query = query.where(MemoryEpisode.session_id == session_id)

    result = await db.execute(query)
    episodes = list(result.scalars().all())

    # Return in chronological order (oldest first) for context building
    episodes.reverse()
    return episodes


async def get_session_history(
    db: AsyncSession,
    project_id: uuid.UUID,
    session_id: uuid.UUID,
) -> list[MemoryEpisode]:
    """Get all turns from a specific session, in chronological order."""
    query = (
        select(MemoryEpisode)
        .where(
            MemoryEpisode.project_id == project_id,
            MemoryEpisode.session_id == session_id,
        )
        .order_by(MemoryEpisode.created_at.asc())
    )

    result = await db.execute(query)
    return list(result.scalars().all())


async def list_sessions(
    db: AsyncSession,
    project_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """
    List unique sessions for a project with metadata.
    Returns: (sessions_list, total_count)
    """
    # Count total distinct sessions
    count_query = (
        select(func.count(distinct(MemoryEpisode.session_id)))
        .where(MemoryEpisode.project_id == project_id)
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get session summaries
    session_query = (
        select(
            MemoryEpisode.session_id,
            func.min(MemoryEpisode.created_at).label("started_at"),
            func.max(MemoryEpisode.created_at).label("last_activity"),
            func.count(MemoryEpisode.id).label("turn_count"),
        )
        .where(MemoryEpisode.project_id == project_id)
        .group_by(MemoryEpisode.session_id)
        .order_by(func.max(MemoryEpisode.created_at).desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(session_query)
    rows = result.all()

    sessions = []
    for row in rows:
        # Get the first user message as a preview
        first_msg_query = (
            select(MemoryEpisode.content)
            .where(
                MemoryEpisode.project_id == project_id,
                MemoryEpisode.session_id == row.session_id,
                MemoryEpisode.role == "user",
            )
            .order_by(MemoryEpisode.created_at.asc())
            .limit(1)
        )
        first_msg_result = await db.execute(first_msg_query)
        first_message = first_msg_result.scalar() or ""

        sessions.append({
            "session_id": str(row.session_id),
            "first_message": first_message[:200],  # Truncate preview
            "started_at": row.started_at.isoformat(),
            "last_activity": row.last_activity.isoformat(),
            "turn_count": row.turn_count,
        })

    return sessions, total


async def count_episodes(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> int:
    """Count total episodes for a project."""
    query = (
        select(func.count(MemoryEpisode.id))
        .where(MemoryEpisode.project_id == project_id)
    )
    result = await db.execute(query)
    return result.scalar() or 0
