"""
MemoryOS Backend — Structured Memory (Tier 3)
Read/write facts, preferences, and entities to PostgreSQL.
Phase 2: fact extraction from conversations + file uploads.
Every query is scoped by project_id (Rules.md §2).
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import MemoryFact

logger = get_logger("memory.structured")

# Domain-aware TTL defaults (Architecture.md §3 Tier 3)
DEFAULT_TTL_DAYS = {
    "tech_stack": 7,
    "decision": 30,
    "preference": 90,
    "entity": 90,
    "goal": 90,
    "milestone": 180,
    "open_question": 14,
    "file_fact": 7,
}


async def store_fact(
    db: AsyncSession,
    project_id: uuid.UUID,
    fact_type: str,
    key: str,
    value: str,
    source: str = "conversation",
    source_episode_id: Optional[uuid.UUID] = None,
    confidence: float = 0.8,
) -> MemoryFact:
    """
    Store a structured fact in memory.
    Deduplicates: if a fact with the same project_id + key exists,
    updates the value instead of creating a duplicate.
    """
    # Check for existing fact with same key in this project
    result = await db.execute(
        select(MemoryFact).where(
            MemoryFact.project_id == project_id,
            MemoryFact.key == key,
            MemoryFact.is_stale == False,  # noqa: E712
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing fact
        existing.value = value
        existing.confidence = max(existing.confidence, confidence)
        existing.source = source
        existing.source_episode_id = source_episode_id
        existing.updated_at = datetime.now(timezone.utc)
        await db.flush()

        logger.info(
            "fact_updated",
            project_id=str(project_id),
            fact_type=fact_type,
            key=key,
        )
        return existing

    # Create new fact
    ttl = DEFAULT_TTL_DAYS.get(fact_type)
    fact = MemoryFact(
        id=uuid.uuid4(),
        project_id=project_id,
        fact_type=fact_type,
        key=key,
        value=value,
        source=source,
        source_episode_id=source_episode_id,
        confidence=confidence,
        ttl_days=ttl,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(fact)
    await db.flush()

    logger.info(
        "fact_stored",
        project_id=str(project_id),
        fact_type=fact_type,
        key=key,
        confidence=confidence,
    )
    return fact


async def get_facts(
    db: AsyncSession,
    project_id: uuid.UUID,
    fact_type: Optional[str] = None,
    include_stale: bool = False,
    limit: int = 100,
) -> list[MemoryFact]:
    """
    Get facts for a project, optionally filtered by type.
    Always scoped by project_id (Rules.md §2).
    """
    query = (
        select(MemoryFact)
        .where(MemoryFact.project_id == project_id)
        .order_by(MemoryFact.updated_at.desc())
        .limit(limit)
    )

    if fact_type:
        query = query.where(MemoryFact.fact_type == fact_type)

    if not include_stale:
        query = query.where(MemoryFact.is_stale == False)  # noqa: E712

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_fact_by_id(
    db: AsyncSession,
    project_id: uuid.UUID,
    fact_id: uuid.UUID,
) -> Optional[MemoryFact]:
    """Get a specific fact by ID, scoped to project."""
    result = await db.execute(
        select(MemoryFact).where(
            MemoryFact.id == fact_id,
            MemoryFact.project_id == project_id,
        )
    )
    return result.scalar_one_or_none()


async def search_facts(
    db: AsyncSession,
    project_id: uuid.UUID,
    query: str,
    limit: int = 20,
) -> list[MemoryFact]:
    """
    Search facts by key or value using ILIKE.
    Used by BM25 hybrid search and the facts API.
    """
    search_pattern = f"%{query}%"
    result = await db.execute(
        select(MemoryFact)
        .where(
            MemoryFact.project_id == project_id,
            MemoryFact.is_stale == False,  # noqa: E712
            or_(
                MemoryFact.key.ilike(search_pattern),
                MemoryFact.value.ilike(search_pattern),
            ),
        )
        .order_by(MemoryFact.confidence.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_fact(
    db: AsyncSession,
    project_id: uuid.UUID,
    fact_id: uuid.UUID,
    value: Optional[str] = None,
    confidence: Optional[float] = None,
    is_stale: Optional[bool] = None,
) -> Optional[MemoryFact]:
    """Update a fact's value, confidence, or staleness."""
    fact = await get_fact_by_id(db, project_id, fact_id)
    if not fact:
        return None

    if value is not None:
        fact.value = value
    if confidence is not None:
        fact.confidence = confidence
    if is_stale is not None:
        fact.is_stale = is_stale

    fact.updated_at = datetime.now(timezone.utc)
    await db.flush()

    logger.info("fact_updated", fact_id=str(fact_id), project_id=str(project_id))
    return fact


async def mark_stale(
    db: AsyncSession,
    project_id: uuid.UUID,
    fact_id: uuid.UUID,
) -> Optional[MemoryFact]:
    """Mark a fact as stale (Phase 3 self-healing hook)."""
    return await update_fact(db, project_id, fact_id, is_stale=True)


async def count_facts(
    db: AsyncSession,
    project_id: uuid.UUID,
    include_stale: bool = False,
) -> int:
    """Count total facts for a project."""
    query = (
        select(func.count(MemoryFact.id))
        .where(MemoryFact.project_id == project_id)
    )
    if not include_stale:
        query = query.where(MemoryFact.is_stale == False)  # noqa: E712

    result = await db.execute(query)
    return result.scalar() or 0


async def get_all_facts_text(
    db: AsyncSession,
    project_id: uuid.UUID,
    limit: int = 200,
) -> list[dict]:
    """
    Get all facts as text dicts for BM25 indexing and prompt building.
    Returns: [{key, value, fact_type, confidence, created_at}, ...]
    """
    facts = await get_facts(db, project_id, limit=limit)
    return [
        {
            "id": str(f.id),
            "content": f"{f.key}: {f.value}",
            "key": f.key,
            "value": f.value,
            "fact_type": f.fact_type,
            "confidence": f.confidence,
            "source_type": "fact",
            "created_at": f.created_at.isoformat() if f.created_at else "",
        }
        for f in facts
    ]
