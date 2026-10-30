"""
MemoryOS Backend — Retrieval Layer
Phase 2: Hybrid search (Semantic + BM25) with RRF fusion.

Architecture.md §2.1 / §6:
  1. Semantic search (Qdrant cosine similarity)
  2. BM25 keyword search (in-memory, rank-bm25)
  3. RRF fusion: combined_score = Σ 1/(k + rank_i) across both lists
  4. Re-rank: rrf_score * 0.5 + recency * 0.3 + source_type_boost * 0.2
  5. Top-K, enforce token budget
"""

import uuid
from datetime import datetime, timezone

import tiktoken

from app.core.config import get_settings
from app.core.logging import get_logger
from app.memory.semantic import search_similar

logger = get_logger("memory.retrieval")

# RRF constant (standard value from the original RRF paper)
RRF_K = 60


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


def _source_type_boost(chunk: dict, query: str) -> float:
    """
    Boost score based on source type relevance to the query.
    - File content gets +0.1 when query mentions filenames
    - Facts get +0.1 for direct questions
    """
    source = chunk.get("source_type", "conversation")
    query_lower = query.lower()

    if source == "file":
        # Boost if query seems to reference files
        file_keywords = ["file", "code", "import", "function", "class", "upload"]
        if any(kw in query_lower for kw in file_keywords):
            return 0.1
        filename = chunk.get("filename", "")
        if filename and filename.lower() in query_lower:
            return 0.15
    elif source == "fact":
        # Boost for questions that facts would directly answer
        fact_keywords = ["what", "which", "who", "decision", "stack", "use", "prefer"]
        if any(kw in query_lower for kw in fact_keywords):
            return 0.1

    return 0.0


def _rrf_fuse(
    semantic_results: list[dict],
    bm25_results: list[dict],
    k: int = RRF_K,
) -> list[dict]:
    """
    Reciprocal Rank Fusion: merges two ranked lists into one.
    Score = Σ 1/(k + rank) for each list the document appears in.
    Documents are matched by their 'id' field.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, dict] = {}

    # Score semantic results by rank
    for rank, doc in enumerate(semantic_results):
        doc_id = doc.get("id", "")
        if not doc_id:
            continue
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
        doc_map[doc_id] = doc

    # Score BM25 results by rank
    for rank, doc in enumerate(bm25_results):
        doc_id = doc.get("id", "")
        if not doc_id:
            continue
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
        # Keep the richer doc (semantic results have more metadata)
        if doc_id not in doc_map:
            doc_map[doc_id] = doc

    # Build fused list
    fused = []
    for doc_id, rrf_score in scores.items():
        doc = dict(doc_map[doc_id])
        doc["rrf_score"] = rrf_score
        fused.append(doc)

    # Sort by RRF score descending
    fused.sort(key=lambda x: x["rrf_score"], reverse=True)
    return fused


async def retrieve_context(
    project_id: uuid.UUID,
    query_vector: list[float],
    query_text: str = "",
    db=None,
    top_k: int | None = None,
    token_budget: int | None = None,
) -> list[dict]:
    """
    Retrieve relevant memory chunks for a query.

    Phase 2 hybrid strategy:
    1. Semantic search (Qdrant) → scored results
    2. BM25 keyword search → scored results (if db session provided)
    3. RRF fusion: merge both ranked lists
    4. Re-rank: rrf_score * 0.5 + recency * 0.3 + source_type_boost * 0.2
    5. Top-K, enforce token budget

    Falls back to semantic-only if db is None (backward compatible with Phase 1).

    Returns list of chunks with content, score, source_type.
    """
    settings = get_settings()
    top_k = top_k or settings.retrieval_top_k
    token_budget = token_budget or settings.context_token_budget

    # Step 1: Semantic search (Qdrant)
    semantic_results = await search_similar(
        project_id=project_id,
        query_vector=query_vector,
        top_k=top_k * 2,  # Fetch extra for re-ranking headroom
        score_threshold=0.25,
    )

    # Step 2: BM25 keyword search (if DB session available)
    bm25_results = []
    if db is not None and query_text:
        try:
            from app.memory.bm25_search import bm25_search_project
            bm25_results = await bm25_search_project(
                db=db,
                project_id=project_id,
                query=query_text,
                top_k=top_k * 2,
            )
        except Exception as e:
            logger.warning("bm25_search_error", error=str(e)[:150])

    # Step 3: Fuse results
    if bm25_results:
        fused = _rrf_fuse(semantic_results, bm25_results)
    elif semantic_results:
        # Fallback: semantic only (assign pseudo-RRF scores)
        for rank, doc in enumerate(semantic_results):
            doc["rrf_score"] = 1.0 / (RRF_K + rank + 1)
        fused = semantic_results
    else:
        logger.debug("retrieval_empty", project_id=str(project_id))
        return []

    # Step 4: Re-rank with recency + source type boost
    for chunk in fused:
        recency = _recency_score(chunk.get("created_at", ""))
        source_boost = _source_type_boost(chunk, query_text) if query_text else 0.0
        chunk["recency_score"] = recency
        chunk["combined_score"] = (
            chunk["rrf_score"] * 0.5
            + recency * 0.3
            + source_boost * 0.2
        )

    fused.sort(key=lambda x: x["combined_score"], reverse=True)

    # Step 5: Take top-K
    ranked = fused[:top_k]

    # Step 6: Enforce token budget
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
        semantic_hits=len(semantic_results),
        bm25_hits=len(bm25_results),
        fused=len(fused),
        selected=len(selected),
        total_tokens=total_tokens,
        token_budget=token_budget,
    )

    return selected
