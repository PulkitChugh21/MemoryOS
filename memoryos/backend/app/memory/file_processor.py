"""
MemoryOS Backend — File Processor
Phase 2: Parse, chunk, embed, and version uploaded files.
Architecture.md §2.2 File Upload Flow.

Pipeline:
1. Parse — read file content based on MIME type
2. Chunk — split into ~500-token overlapping chunks
3. Embed — generate embeddings for each chunk via Gemini
4. Upsert — store chunk embeddings in Qdrant with source_type: "file"
5. Version check — if file exists, generate diff, mark old as non-current
"""

import os
import uuid
import mimetypes
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.models import ProjectFile
from app.llm.embeddings import generate_embedding
from app.memory.semantic import upsert_embedding

logger = get_logger("memory.file_processor")


def _get_mime_type(filename: str) -> str:
    """Detect MIME type from filename."""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "text/plain"


def _validate_file(filename: str, size_bytes: int) -> Optional[str]:
    """
    Validate file extension and size.
    Returns error message string if invalid, None if valid.
    """
    settings = get_settings()

    # Check file size
    if size_bytes > settings.max_file_size_bytes:
        max_mb = settings.max_file_size_bytes / (1024 * 1024)
        return f"File too large. Maximum size is {max_mb:.0f}MB."

    # Check extension
    _, ext = os.path.splitext(filename.lower())
    if ext and ext not in settings.allowed_extensions_list:
        return f"File type '{ext}' is not supported."

    return None


def chunk_text(
    text: str,
    chunk_size_chars: int = 2000,
    overlap_chars: int = 400,
) -> list[str]:
    """
    Split text into overlapping chunks.
    Uses character-based splitting (~4 chars per token).

    Args:
        text: The full text to chunk.
        chunk_size_chars: Target chunk size in characters (~500 tokens).
        overlap_chars: Overlap between chunks (~100 tokens).

    Returns:
        List of text chunks.
    """
    if not text or not text.strip():
        return []

    if len(text) <= chunk_size_chars:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size_chars

        # Try to break at a natural boundary (newline, sentence end)
        if end < len(text):
            # Look for newline near the end
            newline_pos = text.rfind("\n", start + chunk_size_chars // 2, end + 200)
            if newline_pos > start:
                end = newline_pos + 1
            else:
                # Look for sentence boundary
                for sep in [". ", ";\n", "}\n", "\n\n"]:
                    sep_pos = text.rfind(sep, start + chunk_size_chars // 2, end + 100)
                    if sep_pos > start:
                        end = sep_pos + len(sep)
                        break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start forward, accounting for overlap
        start = end - overlap_chars
        if start <= chunks[-1] if not chunks else 0:
            start = end  # Prevent infinite loop

    return chunks


async def embed_and_store_chunks(
    project_id: uuid.UUID,
    file_id: uuid.UUID,
    filename: str,
    chunks: list[str],
) -> int:
    """
    Embed each chunk and store in Qdrant.
    Returns the number of successfully embedded chunks.
    """
    embedded_count = 0

    for i, chunk in enumerate(chunks):
        try:
            embedding = await generate_embedding(chunk)
            if embedding:
                point_id = f"file_{str(file_id).replace('-', '')}_{i}"
                await upsert_embedding(
                    project_id=project_id,
                    point_id=point_id,
                    vector=embedding,
                    payload={
                        "content": chunk,
                        "source_type": "file",
                        "filename": filename,
                        "file_id": str(file_id),
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
                embedded_count += 1
        except Exception as e:
            logger.warning(
                "chunk_embed_failed",
                filename=filename,
                chunk_index=i,
                error=str(e)[:150],
            )

    logger.info(
        "file_chunks_embedded",
        filename=filename,
        total_chunks=len(chunks),
        embedded=embedded_count,
    )
    return embedded_count


async def generate_diff_summary(
    old_content: str,
    new_content: str,
    filename: str,
) -> Optional[str]:
    """
    Generate an LLM-powered diff summary between two file versions.
    Returns a human-readable summary of changes.
    """
    import asyncio
    import google.generativeai as genai
    from app.core.config import get_settings

    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)

    prompt = f"""Compare these two versions of the file "{filename}" and provide a brief summary of what changed.

## Previous Version (truncated):
{old_content[:3000]}

## New Version (truncated):
{new_content[:3000]}

Provide a concise 2-3 sentence summary of the key differences. Focus on what was added, removed, or modified."""

    try:
        model = genai.GenerativeModel(
            model_name=settings.llm_model,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=256,
                temperature=0.2,
            ),
        )
        response = await asyncio.to_thread(
            model.generate_content,
            prompt,
            request_options={"timeout": 30},
        )
        return response.text.strip()
    except Exception as e:
        logger.warning("diff_summary_failed", filename=filename, error=str(e)[:150])
        return None


async def check_existing_file(
    db: AsyncSession,
    project_id: uuid.UUID,
    filename: str,
) -> Optional[ProjectFile]:
    """Check if a file with the same name already exists (current version)."""
    result = await db.execute(
        select(ProjectFile).where(
            ProjectFile.project_id == project_id,
            ProjectFile.filename == filename,
            ProjectFile.is_current == True,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def process_file_upload(
    db: AsyncSession,
    project_id: uuid.UUID,
    filename: str,
    file_content: bytes,
    file_path: str,
) -> tuple[ProjectFile, bool, Optional[str]]:
    """
    Full file processing pipeline.

    Returns:
        (file_record, is_new_version, diff_summary)
    """
    content_text = file_content.decode("utf-8", errors="replace")
    mime_type = _get_mime_type(filename)
    size_bytes = len(file_content)
    is_new_version = False
    diff_summary = None

    # Check for existing version
    existing = await check_existing_file(db, project_id, filename)

    if existing:
        is_new_version = True
        # Mark old version as non-current
        existing.is_current = False
        await db.flush()

        new_version = existing.version + 1
        parent_id = existing.id
    else:
        new_version = 1
        parent_id = None

    # Create file record
    file_record = ProjectFile(
        id=uuid.uuid4(),
        project_id=project_id,
        filename=filename,
        file_path=file_path,
        mime_type=mime_type,
        size_bytes=size_bytes,
        version=new_version,
        parent_version_id=parent_id,
        is_current=True,
    )
    db.add(file_record)
    await db.flush()

    # Chunk the content
    settings = get_settings()
    chunk_size_chars = settings.file_chunk_size_tokens * 4  # ~4 chars per token
    overlap_chars = settings.file_chunk_overlap_tokens * 4
    chunks = chunk_text(content_text, chunk_size_chars, overlap_chars)

    # Embed and store chunks
    embedded_count = await embed_and_store_chunks(
        project_id=project_id,
        file_id=file_record.id,
        filename=filename,
        chunks=chunks,
    )
    file_record.chunk_count = embedded_count

    # Generate diff summary if this is a new version
    if is_new_version and existing:
        # We'd need the old content — for now, generate a simple summary
        diff_summary = f"Updated from version {existing.version} to {new_version}. File size: {size_bytes} bytes, {embedded_count} chunks embedded."
        file_record.diff_summary = diff_summary

    await db.flush()

    logger.info(
        "file_processed",
        filename=filename,
        version=new_version,
        chunks=embedded_count,
        is_new_version=is_new_version,
    )

    return file_record, is_new_version, diff_summary
