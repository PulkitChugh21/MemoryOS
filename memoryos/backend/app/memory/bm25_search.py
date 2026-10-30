"""
MemoryOS Backend — BM25 Keyword Search
Phase 2: In-memory BM25 index built from DB content at query time.
Architecture.md §6: BM25 keyword + semantic combined with RRF fusion.

Uses rank-bm25 (pure Python, no external service — stays within $0/month model).
"""

import uuid
from typing import Optional

from rank_bm25 import BM25Okapi

from app.core.logging import get_logger

logger = get_logger("memory.bm25")


def _tokenize(text: str) -> list[str]:
    """
    Simple whitespace + lowercase tokenization.
    Strips punctuation for better keyword matching.
    """
    import re
    # Lowercase, split on non-alphanumeric, filter short tokens
    tokens = re.findall(r'\b[a-z0-9]+\b', text.lower())
    return [t for t in tokens if len(t) > 1]


def build_bm25_index(
    documents: list[dict],
) -> tuple[Optional[BM25Okapi], list[dict]]:
    """
    Build a BM25 index from a list of document dicts.

    Each document must have a 'content' key.
    Returns (bm25_index, documents) or (None, []) if empty.
    """
    if not documents:
        return None, []

    # Tokenize all documents
    tokenized_docs = []
    valid_docs = []
    for doc in documents:
        content = doc.get("content", "")
        if not content:
            continue
        tokens = _tokenize(content)
        if tokens:
            tokenized_docs.append(tokens)
            valid_docs.append(doc)

    if not tokenized_docs:
        return None, []

    try:
        index = BM25Okapi(tokenized_docs)
        return index, valid_docs
    except Exception as e:
        logger.warning("bm25_index_build_failed", error=str(e)[:150])
        return None, []


def bm25_search(
    index: BM25Okapi,
    documents: list[dict],
    query: str,
    top_k: int = 16,
) -> list[dict]:
    """
    Search a BM25 index with a query.

    Returns documents with added 'bm25_score' field, sorted by score descending.
    """
    tokens = _tokenize(query)
    if not tokens:
        return []

    try:
        scores = index.get_scores(tokens)
    except Exception as e:
        logger.warning("bm25_search_failed", error=str(e)[:150])
        return []

    # Pair documents with scores, filter zero scores
    scored_docs = []
    for doc, score in zip(documents, scores):
        if score > 0:
            result = dict(doc)
            result["bm25_score"] = float(score)
            scored_docs.append(result)

    # Sort by score descending, take top-K
    scored_docs.sort(key=lambda x: x["bm25_score"], reverse=True)
    return scored_docs[:top_k]


async def bm25_search_project(
    db,
    project_id: uuid.UUID,
    query: str,
    top_k: int = 16,
) -> list[dict]:
    """
    Full BM25 search pipeline for a project:
    1. Fetch recent episodes + facts from DB
    2. Build BM25 index in-memory
    3. Search and return ranked results

    The index is rebuilt per query — project memory is small enough for this.
    Caching can be added later if needed.
    """
    from app.memory.episodic import get_recent_episodes
    from app.memory.structured import get_all_facts_text

    # Gather all searchable content
    all_documents = []

    # Episodes (conversation turns)
    episodes = await get_recent_episodes(db, project_id, limit=200)
    for ep in episodes:
        all_documents.append({
            "id": str(ep.id),
            "content": ep.content,
            "source_type": "conversation",
            "role": ep.role,
            "created_at": ep.created_at.isoformat() if ep.created_at else "",
        })

    # Structured facts
    facts_text = await get_all_facts_text(db, project_id, limit=200)
    all_documents.extend(facts_text)

    if not all_documents:
        logger.debug("bm25_no_documents", project_id=str(project_id))
        return []

    # Build index and search
    index, valid_docs = build_bm25_index(all_documents)
    if index is None:
        return []

    results = bm25_search(index, valid_docs, query, top_k=top_k)

    logger.info(
        "bm25_search_complete",
        project_id=str(project_id),
        total_docs=len(all_documents),
        results=len(results),
    )

    return results
