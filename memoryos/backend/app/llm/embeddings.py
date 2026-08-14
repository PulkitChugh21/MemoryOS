"""
MemoryOS Backend — Embedding Generation
Uses Gemini gemini-embedding-001 (3072-dim, free tier).
"""

import asyncio
from typing import Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("llm.embeddings")

_configured = False


def _ensure_configured():
    """Configure the Gemini API key once."""
    global _configured
    if not _configured:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True


async def generate_embedding(
    text: str,
    task_type: str = "RETRIEVAL_DOCUMENT",
    max_retries: int = 3,
) -> Optional[list[float]]:
    """
    Generate a 3072-dim embedding vector using Gemini gemini-embedding-001.

    Args:
        text: The text to embed.
        task_type: One of RETRIEVAL_QUERY, RETRIEVAL_DOCUMENT, SEMANTIC_SIMILARITY,
                   CLASSIFICATION, CLUSTERING.
        max_retries: Max retry attempts (Rules.md §3).

    Returns:
        3072-dimensional float vector, or None on failure.
    """
    _ensure_configured()
    settings = get_settings()

    # Truncate very long texts to avoid API limits
    if len(text) > 10000:
        text = text[:10000]

    for attempt in range(max_retries):
        try:
            result = await asyncio.to_thread(
                genai.embed_content,
                model=settings.embedding_model,
                content=text,
                task_type=task_type,
            )
            embedding = result["embedding"]
            logger.debug(
                "embedding_generated",
                text_length=len(text),
                vector_dim=len(embedding),
            )
            return embedding

        except google_exceptions.ResourceExhausted as e:
            # Quota exhausted — fail fast, don't retry endlessly
            logger.error("embedding_quota_exhausted", error=str(e)[:150])
            return None

        except Exception as e:
            error_str = str(e).lower()
            is_transient = any(
                keyword in error_str
                for keyword in ["rate limit", "timeout", "503", "429"]
            )

            if is_transient and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(
                    "embedding_retry",
                    attempt=attempt + 1,
                    wait_seconds=wait_time,
                    error=str(e)[:150],
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    "embedding_failed",
                    text_length=len(text),
                    error=str(e)[:150],
                )
                return None


async def generate_query_embedding(query: str) -> Optional[list[float]]:
    """
    Generate an embedding optimized for query/retrieval.
    Uses RETRIEVAL_QUERY task type for better search results.
    """
    return await generate_embedding(text=query, task_type="RETRIEVAL_QUERY")
