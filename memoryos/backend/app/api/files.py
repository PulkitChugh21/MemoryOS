"""
MemoryOS Backend — Files API Routes
Phase 2: File upload, download, list, version history, and diff.
Architecture.md §2.2: File Upload Flow.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import get_current_user_id
from app.db.models import ProjectFile
from app.db.session import get_db
from app.llm.fact_extractor import extract_facts_from_file
from app.memory.file_processor import (
    _validate_file,
    process_file_upload,
)
from app.memory.structured import store_fact
from app.schemas import (
    ErrorResponse,
    FileListResponse,
    FileResponse,
    FileUploadResponse,
    FileVersionResponse,
)

logger = get_logger("api.files")
router = APIRouter(prefix="/files", tags=["Files"])


@router.post(
    "/{project_id}/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def upload_file(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a file to a project's memory.
    Files are chunked, embedded, and stored for semantic retrieval.
    Re-uploading the same filename creates a new version.
    """
    # Validate project access
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)

    # Read file content
    file_content = await file.read()
    filename = file.filename or "unnamed_file"
    size_bytes = len(file_content)

    # Validate file
    validation_error = _validate_file(filename, size_bytes)
    if validation_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_FILE",
                    "message": validation_error,
                    "details": {},
                }
            },
        )

    # Store in Supabase Storage (or local fallback)
    file_path = f"{project_id}/{filename}"
    try:
        settings = get_settings()
        from supabase import create_client
        supabase_client = create_client(settings.supabase_url, settings.supabase_service_key)

        # Ensure bucket exists
        try:
            supabase_client.storage.get_bucket(settings.supabase_storage_bucket)
        except Exception:
            supabase_client.storage.create_bucket(
                settings.supabase_storage_bucket,
                options={"public": False},
            )

        # Upload (upsert to handle re-uploads)
        supabase_client.storage.from_(settings.supabase_storage_bucket).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type or "text/plain", "upsert": "true"},
        )
    except Exception as e:
        logger.warning("supabase_storage_error", error=str(e)[:200])
        # Continue without storage — metadata and embeddings still work
        file_path = f"local/{project_id}/{filename}"

    # Process: chunk, embed, version
    file_record, is_new_version, diff_summary = await process_file_upload(
        db=db,
        project_id=project_id,
        filename=filename,
        file_content=file_content,
        file_path=file_path,
    )

    # Extract facts from file content (non-blocking)
    facts_extracted = 0
    try:
        content_text = file_content.decode("utf-8", errors="replace")
        facts = await extract_facts_from_file(filename, content_text)
        for fact_data in facts:
            await store_fact(
                db=db,
                project_id=project_id,
                fact_type=fact_data["fact_type"],
                key=fact_data["key"],
                value=fact_data["value"],
                source="file_upload",
                confidence=fact_data["confidence"],
            )
            facts_extracted += 1
    except Exception as e:
        logger.warning("file_fact_extraction_error", error=str(e)[:150])

    await db.commit()

    logger.info(
        "file_uploaded",
        project_id=str(project_id),
        filename=filename,
        version=file_record.version,
        chunks=file_record.chunk_count,
        facts=facts_extracted,
    )

    return FileUploadResponse(
        file=FileResponse.model_validate(file_record),
        facts_extracted=facts_extracted,
        chunks_embedded=file_record.chunk_count,
        is_new_version=is_new_version,
        diff_summary=diff_summary,
    )


@router.get(
    "/{project_id}",
    response_model=FileListResponse,
)
async def list_files(
    project_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all current files for a project."""
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)

    result = await db.execute(
        select(ProjectFile)
        .where(
            ProjectFile.project_id == project_id,
            ProjectFile.is_current == True,  # noqa: E712
        )
        .order_by(ProjectFile.uploaded_at.desc())
    )
    files = list(result.scalars().all())

    return FileListResponse(
        files=[FileResponse.model_validate(f) for f in files],
        total=len(files),
    )


@router.get(
    "/{project_id}/{file_id}",
    response_model=FileResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_file(
    project_id: uuid.UUID,
    file_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get file metadata by ID."""
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)

    result = await db.execute(
        select(ProjectFile).where(
            ProjectFile.id == file_id,
            ProjectFile.project_id == project_id,
        )
    )
    file_record = result.scalar_one_or_none()

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "FILE_NOT_FOUND",
                    "message": "File not found.",
                    "details": {},
                }
            },
        )

    return FileResponse.model_validate(file_record)


@router.get(
    "/{project_id}/{file_id}/versions",
    response_model=list[FileVersionResponse],
)
async def get_file_versions(
    project_id: uuid.UUID,
    file_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get version history for a file."""
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)

    # Get the file to find its filename
    result = await db.execute(
        select(ProjectFile).where(
            ProjectFile.id == file_id,
            ProjectFile.project_id == project_id,
        )
    )
    file_record = result.scalar_one_or_none()
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "FILE_NOT_FOUND", "message": "File not found.", "details": {}}},
        )

    # Get all versions of this filename
    result = await db.execute(
        select(ProjectFile)
        .where(
            ProjectFile.project_id == project_id,
            ProjectFile.filename == file_record.filename,
        )
        .order_by(ProjectFile.version.desc())
    )
    versions = list(result.scalars().all())

    return [FileVersionResponse.model_validate(v) for v in versions]


@router.delete(
    "/{project_id}/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
async def delete_file(
    project_id: uuid.UUID,
    file_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a file (mark as non-current).
    Qdrant embeddings for this file's chunks remain for historical context.
    """
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)

    result = await db.execute(
        select(ProjectFile).where(
            ProjectFile.id == file_id,
            ProjectFile.project_id == project_id,
        )
    )
    file_record = result.scalar_one_or_none()

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "FILE_NOT_FOUND", "message": "File not found.", "details": {}}},
        )

    file_record.is_current = False
    await db.flush()

    # Try to delete from Supabase Storage
    try:
        settings = get_settings()
        from supabase import create_client
        supabase_client = create_client(settings.supabase_url, settings.supabase_service_key)
        supabase_client.storage.from_(settings.supabase_storage_bucket).remove([file_record.file_path])
    except Exception as e:
        logger.warning("storage_delete_error", error=str(e)[:150])

    logger.info("file_deleted", file_id=str(file_id), project_id=str(project_id))


@router.get(
    "/{project_id}/{file_id}/download",
)
async def download_file(
    project_id: uuid.UUID,
    file_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Download file content from Supabase Storage."""
    from app.api.projects import _get_user_project
    await _get_user_project(db, project_id, user_id)

    result = await db.execute(
        select(ProjectFile).where(
            ProjectFile.id == file_id,
            ProjectFile.project_id == project_id,
        )
    )
    file_record = result.scalar_one_or_none()

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "FILE_NOT_FOUND", "message": "File not found.", "details": {}}},
        )

    try:
        settings = get_settings()
        from supabase import create_client
        supabase_client = create_client(settings.supabase_url, settings.supabase_service_key)
        content = supabase_client.storage.from_(settings.supabase_storage_bucket).download(
            file_record.file_path
        )

        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=file_record.mime_type,
            headers={"Content-Disposition": f'attachment; filename="{file_record.filename}"'},
        )
    except Exception as e:
        logger.error("file_download_error", error=str(e)[:200])
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": {
                    "code": "STORAGE_ERROR",
                    "message": "Failed to download file from storage.",
                    "details": {},
                }
            },
        )
