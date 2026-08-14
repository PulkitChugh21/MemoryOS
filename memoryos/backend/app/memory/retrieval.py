"""
MemoryOS Backend — Retrieval Layer
Phase 1: Semantic-only retrieval (Qdrant cosine similarity).
Phase 2 will add BM25 hybrid search with RRF fusion.

Architecture.md §2.1: Re-rank by relevance_score * 0.6 + recency_score * 0.4,
then assemble top-8 chunks, summarize if over context budget.
"""

import uuid
from datetime import datetime, timezone

import tiktoken

from app.core.config import get_settings
from app.core.logging import get_logger
from app.memory.semantic import search_similar

logger = get_logger("memory.retrieval")


def _recency_score(created_at_iso: str) -> float:
    """
    Calculate a recency score between 0 and 1.
    More recent = higher score. Decays over 30 days.
    """
    try:
        if isinstance(created_at_iso, (int, float)):
            created = datetime.fromtimestamp(created_at_iso, tz=timezone.utc)
        else:
            created = datetime.fromisoformat(created_at_iso.replace("Z", "+00:00"))

        age_seconds = (datetime.now(timezone.utc) - created).total_seconds()
        age_days = age_seconds / 86400.0

        # Exponential decay over 30 days
        # Score = 1.0 at age 0, ~0.37 at age 30d, ~0.14 at age 60d
        import math
        return math.exp(-age_days / 30.0)
    except Exception:
        return 0.5  # Default if parsing fails


def _count_tokens(text: str) -> int:
    """Count tokens using tiktoken (Rules.md §2: never let context grow unbounded)."""
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # Rough fallback: ~4 chars per token
        return len(text) // 4


async def retrieve_context(
    project_id: uuid.UUID,
    query_vector: list[float],
    top_k: int | None = None,
    token_budget: int | None = None,
) -> list[dict]:
    """
    Retrieve relevant memory chunks for a query.

    Phase 1 strategy (semantic only):
    1. Search Qdrant for similar embeddings
    2. Re-rank by: relevance_score * 0.6 + recency_score * 0.4
    3. Take top-K chunks
    4. Enforce token budget — truncate if over

    Returns list of chunks with content, score, source_type.
    """
    settings = get_settings()
    top_k = top_k or settings.retrieval_top_k
    token_budget = token_budget or settings.context_token_budget

    # Step 1: Semantic search (Qdrant)
    raw_results = await search_similar(
        project_id=project_id,
        query_vector=query_vector,
        top_k=top_k * 2,  # Fetch extra for re-ranking headroom
        score_threshold=0.25,
    )

    if not raw_results:
        logger.debug("retrieval_empty", project_id=str(project_id))
        return []

    # Step 2: Re-rank — relevance * 0.6 + recency * 0.4
    for chunk in raw_results:
        recency = _recency_score(chunk.get("created_at", ""))
        chunk["recency_score"] = recency
        chunk["combined_score"] = (chunk["score"] * 0.6) + (recency * 0.4)

    raw_results.sort(key=lambda x: x["combined_score"], reverse=True)

    # Step 3: Take top-K
    ranked = raw_results[:top_k]

    # Step 4: Enforce token budget
    selected = []
    total_tokens = 0

    for chunk in ranked:
        chunk_tokens = _count_tokens(chunk["content"])
        if total_tokens + chunk_tokens > token_budget:
            # Try to fit a truncated version
            remaining_budget = token_budget - total_tokens
            if remaining_budget > 100:
                # Rough truncation by characters (4 chars ≈ 1 token)
                truncated = chunk["content"][:remaining_budget * 4]
                chunk["content"] = truncated + "..."
                chunk["truncated"] = True
                selected.append(chunk)
            break

        selected.append(chunk)
        total_tokens += chunk_tokens

    logger.info(
        "retrieval_complete",
        project_id=str(project_id),
        candidates=len(raw_results),
        selected=len(selected),
        total_tokens=total_tokens,
        token_budget=token_budget,
    )

    return selected
