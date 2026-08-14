"""
MemoryOS Backend — Semantic Memory (Tier 2)
Qdrant vector store read/write for embedding-based retrieval.
Collection per project: project_{project_id}_memories (Architecture.md §5).
"""

import uuid
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("memory.semantic")

# Module-level client singleton
_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """Get or create the Qdrant client singleton."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30,
        )
        logger.info("qdrant_client_connected", url=settings.qdrant_url)
    return _client


def _collection_name(project_id: uuid.UUID) -> str:
    """
    Generate collection name for a project.
    Format: project_{project_id}_memories (Architecture.md §5)
    """
    return f"project_{str(project_id).replace('-', '_')}_memories"


async def ensure_collection(project_id: uuid.UUID) -> str:
    """
    Create the Qdrant collection for a project if it doesn't exist.
    Uses gemini-embedding-001 (3072-dim), cosine distance.
    Auto-recreates if existing collection has a dimension mismatch.
    """
    client = get_qdrant_client()
    collection = _collection_name(project_id)
    settings = get_settings()
    need_create = False

    try:
        info = client.get_collection(collection)
        # Check if vector dimension matches current embedding model
        existing_dim = info.config.params.vectors.size
        if existing_dim != settings.embedding_dimension:
            logger.warning(
                "collection_dimension_mismatch",
                collection=collection,
                existing=existing_dim,
                expected=settings.embedding_dimension,
            )
            client.delete_collection(collection)
            need_create = True
        else:
            logger.debug("collection_exists", collection=collection)
    except (UnexpectedResponse, Exception):
        need_create = True

    if need_create:
        client.create_collection(
            collection_name=collection,
            vectors_config=qdrant_models.VectorParams(
                size=settings.embedding_dimension,
                distance=qdrant_models.Distance.COSINE,
            ),
        )

        # Create payload indexes for efficient filtering
        client.create_payload_index(
            collection_name=collection,
            field_name="source_type",
            field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
        )
        client.create_payload_index(
            collection_name=collection,
            field_name="created_at",
            field_schema=qdrant_models.PayloadSchemaType.FLOAT,
        )

        logger.info(
            "collection_created",
            collection=collection,
            dimension=settings.embedding_dimension,
        )

    return collection


async def upsert_embedding(
    project_id: uuid.UUID,
    point_id: str,
    vector: list[float],
    payload: dict,
) -> None:
    """
    Upsert a single vector with metadata into the project's collection.

    Args:
        project_id: The project this memory belongs to.
        point_id: Unique ID for this vector (usually episode UUID).
        vector: Embedding from gemini-embedding-001 (3072-dim).
        payload: Metadata dict — must include source_type, content, created_at.
    """
    client = get_qdrant_client()
    collection = await ensure_collection(project_id)

    client.upsert(
        collection_name=collection,
        points=[
            qdrant_models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
        ],
    )

    logger.debug(
        "embedding_upserted",
        collection=collection,
        point_id=point_id,
        source_type=payload.get("source_type"),
    )


async def search_similar(
    project_id: uuid.UUID,
    query_vector: list[float],
    top_k: int = 8,
    score_threshold: float = 0.3,
) -> list[dict]:
    """
    Search for similar memories in the project's vector collection.

    Returns a list of dicts with: id, score, content, source_type, created_at.
    Results are already ranked by cosine similarity.
    """
    client = get_qdrant_client()
    collection = _collection_name(project_id)

    try:
        results = client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
        )
    except (UnexpectedResponse, Exception) as e:
        logger.warning(
            "search_failed",
            collection=collection,
            error=str(e),
        )
        return []

    return [
        {
            "id": str(hit.id),
            "score": hit.score,
            "content": hit.payload.get("content", ""),
            "source_type": hit.payload.get("source_type", "unknown"),
            "role": hit.payload.get("role", ""),
            "created_at": hit.payload.get("created_at", ""),
        }
        for hit in results
    ]


async def delete_collection(project_id: uuid.UUID) -> None:
    """Delete the entire Qdrant collection for a project (used on project deletion)."""
    client = get_qdrant_client()
    collection = _collection_name(project_id)

    try:
        client.delete_collection(collection)
        logger.info("collection_deleted", collection=collection)
    except Exception as e:
        logger.warning("collection_delete_failed", collection=collection, error=str(e))


async def get_collection_info(project_id: uuid.UUID) -> Optional[dict]:
    """Get collection stats (vector count, etc.) for health monitoring."""
    client = get_qdrant_client()
    collection = _collection_name(project_id)

    try:
        info = client.get_collection(collection)
        return {
            "name": collection,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status.value if info.status else "unknown",
        }
    except Exception:
        return None
