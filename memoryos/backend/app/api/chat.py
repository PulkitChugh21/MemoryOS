"""
MemoryOS Backend — Chat API Routes
/chat/{project_id} — the core loop (Architecture.md §2.1).
Supports both SSE streaming and non-streaming responses.

Key design: DB sessions are opened/closed in short bursts around each
DB operation, NOT held open across slow Gemini API calls. Supabase
free-tier drops idle connections after ~10s, so we never hold a
session during embedding/LLM calls.
"""

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.logging import get_logger
from app.core.security import get_current_user_id
from app.db.models import Project, MemoryEpisode
from app.db.session import get_db, get_session_factory
from app.llm.embeddings import generate_embedding, generate_query_embedding
from app.llm.gemini_client import generate_response, generate_response_stream
from app.llm.prompt_builder import build_prompt
from app.memory.episodic import get_recent_episodes, store_episode
from app.memory.retrieval import retrieve_context
from app.memory.semantic import upsert_embedding
from app.schemas import ChatMessage, ChatResponse, ErrorResponse

logger = get_logger("api.chat")
router = APIRouter(prefix="/chat", tags=["Chat"])


async def _validate_project_access(
    project_id: uuid.UUID, user_id: str
) -> Project:
    """Verify the user owns this project (Rules.md §2). Uses its own short DB session."""
    factory = get_session_factory()
    async with factory() as db:
        uid = uuid.UUID(user_id)
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.owner_id == uid,
                Project.status != "deleted",
            )
        )
        project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "PROJECT_NOT_FOUND",
                    "message": "Project not found or access denied.",
                    "details": {},
                }
            },
        )
    return project


async def _get_recent_history(
    project_id: uuid.UUID, session_id: uuid.UUID, limit: int = 20
) -> list[dict]:
    """Fetch recent conversation history in its own short DB session."""
    factory = get_session_factory()
    async with factory() as db:
        episodes = await get_recent_episodes(db, project_id, limit=limit, session_id=session_id)
        return [{"role": ep.role, "content": ep.content} for ep in episodes]


async def _store_episodes_and_embed(
    project_id: uuid.UUID,
    session_id: uuid.UUID,
    user_message: str,
    response_text: str,
    query_embedding: list[float] | None,
) -> None:
    """Store both turns in DB + Qdrant in a single short DB session."""
    factory = get_session_factory()
    async with factory() as db:
        # Store user episode
        user_episode = await store_episode(
            db=db,
            project_id=project_id,
            session_id=session_id,
            role="user",
            content=user_message,
            token_count=len(user_message) // 4,
        )

        # Store assistant episode
        assistant_episode = await store_episode(
            db=db,
            project_id=project_id,
            session_id=session_id,
            role="assistant",
            content=response_text,
            token_count=len(response_text) // 4,
        )

        # Embed and upsert user message if we have an embedding
        if query_embedding:
            user_point_id = str(user_episode.id).replace("-", "")
            await upsert_embedding(
                project_id=project_id,
                point_id=user_point_id,
                vector=query_embedding,
                payload={
                    "content": user_message,
                    "role": "user",
                    "source_type": "conversation",
                    "session_id": str(session_id),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            user_episode.embedding_id = user_point_id

        # Embed assistant response (separate Gemini API call — but DB session is
        # still fresh here, this is fine as embed_content is fast ~1-2s)
        response_embedding = await generate_embedding(response_text)
        if response_embedding:
            assistant_point_id = str(assistant_episode.id).replace("-", "")
            await upsert_embedding(
                project_id=project_id,
                point_id=assistant_point_id,
                vector=response_embedding,
                payload={
                    "content": response_text,
                    "role": "assistant",
                    "source_type": "conversation",
                    "session_id": str(session_id),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            assistant_episode.embedding_id = assistant_point_id

        await db.commit()


@router.post(
    "/{project_id}",
    response_model=ChatResponse,
    responses={404: {"model": ErrorResponse}},
)
async def chat(
    project_id: uuid.UUID,
    payload: ChatMessage,
    user_id: str = Depends(get_current_user_id),
):
    """
    Send a message to the project's AI assistant.
    Non-streaming endpoint — returns the full response.

    Flow (Architecture.md §2.1):
    1. Validate project access (short DB session)
    2. Embed the query (Gemini API — no DB held)
    3. Retrieve relevant memory (Qdrant — no DB held)
    4. Get recent history (short DB session)
    5. Build prompt + generate LLM response (Gemini API — no DB held)
    6. Store both turns + embed for future retrieval (short DB session)
    """
    # Step 1: Validate project access (short DB session, then released)
    project = await _validate_project_access(project_id, user_id)

    session_id = payload.session_id or uuid.uuid4()

    # Step 2: Embed the query (Gemini API — no DB connection needed)
    query_embedding = await generate_query_embedding(payload.message)

    # Step 3: Retrieve relevant memory from Qdrant (no DB needed)
    retrieved_chunks = []
    if query_embedding:
        retrieved_chunks = await retrieve_context(
            project_id=project_id,
            query_vector=query_embedding,
        )

    # Step 4: Get recent conversation history (short DB session)
    recent_history = await _get_recent_history(project_id, session_id)

    # Step 5: Build prompt and generate response (Gemini API — no DB held)
    project_context = ""
    if project.tech_stack:
        project_context = f"Tech stack: {', '.join(project.tech_stack)}"

    system_instruction, user_prompt = build_prompt(
        user_message=payload.message,
        retrieved_chunks=retrieved_chunks,
        recent_history=recent_history,
        project_name=project.name,
        project_context=project_context,
    )

    try:
        response_text = await generate_response(
            prompt=user_prompt,
            system_instruction=system_instruction,
        )
    except Exception as e:
        logger.error(
            "chat_llm_error",
            project_id=str(project_id),
            error=str(e)[:200],
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": {
                    "code": "LLM_ERROR",
                    "message": "Failed to generate a response. Please try again.",
                    "details": {},
                }
            },
        )

    # Step 6: Store both turns in DB + embed for Qdrant (short DB session)
    try:
        await _store_episodes_and_embed(
            project_id=project_id,
            session_id=session_id,
            user_message=payload.message,
            response_text=response_text,
            query_embedding=query_embedding,
        )
    except Exception as e:
        # Memory storage failure shouldn't block the response
        logger.error("chat_storage_error", error=str(e)[:200])

    logger.info(
        "chat_complete",
        project_id=str(project_id),
        session_id=str(session_id),
        sources_used=len(retrieved_chunks),
    )

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        sources_used=len(retrieved_chunks),
    )


@router.post(
    "/{project_id}/stream",
    responses={404: {"model": ErrorResponse}},
)
async def chat_stream(
    project_id: uuid.UUID,
    payload: ChatMessage,
    user_id: str = Depends(get_current_user_id),
):
    """
    SSE streaming chat endpoint.
    Streams the AI response token-by-token via Server-Sent Events.
    After streaming completes, stores both turns in memory.
    """
    # Validate project (short DB session)
    project = await _validate_project_access(project_id, user_id)

    session_id = payload.session_id or uuid.uuid4()

    # Retrieve context (no DB held during Gemini/Qdrant calls)
    query_embedding = await generate_query_embedding(payload.message)
    retrieved_chunks = []
    if query_embedding:
        retrieved_chunks = await retrieve_context(
            project_id=project_id,
            query_vector=query_embedding,
        )

    # Get recent history (short DB session)
    recent_history = await _get_recent_history(project_id, session_id)

    project_context = ""
    if project.tech_stack:
        project_context = f"Tech stack: {', '.join(project.tech_stack)}"

    system_instruction, user_prompt = build_prompt(
        user_message=payload.message,
        retrieved_chunks=retrieved_chunks,
        recent_history=recent_history,
        project_name=project.name,
        project_context=project_context,
    )

    # Store user message (short DB session)
    try:
        factory = get_session_factory()
        async with factory() as db:
            user_episode = await store_episode(
                db=db,
                project_id=project_id,
                session_id=session_id,
                role="user",
                content=payload.message,
                token_count=len(payload.message) // 4,
            )

            if query_embedding:
                user_point_id = str(user_episode.id).replace("-", "")
                await upsert_embedding(
                    project_id=project_id,
                    point_id=user_point_id,
                    vector=query_embedding,
                    payload={
                        "content": payload.message,
                        "role": "user",
                        "source_type": "conversation",
                        "session_id": str(session_id),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    },
                )

            await db.commit()
    except Exception as e:
        logger.error("stream_user_store_error", error=str(e)[:200])

    async def event_generator():
        """Generate SSE events from Gemini streaming response."""
        full_response = []

        try:
            # Send session metadata first
            yield {
                "event": "metadata",
                "data": json.dumps({
                    "session_id": str(session_id),
                    "sources_used": len(retrieved_chunks),
                }),
            }

            # Stream response chunks
            async for chunk in generate_response_stream(
                prompt=user_prompt,
                system_instruction=system_instruction,
            ):
                full_response.append(chunk)
                yield {
                    "event": "chunk",
                    "data": json.dumps({"text": chunk}),
                }

            # After streaming completes, store the full response
            complete_response = "".join(full_response)

            factory = get_session_factory()
            async with factory() as post_db:
                assistant_episode = await store_episode(
                    db=post_db,
                    project_id=project_id,
                    session_id=session_id,
                    role="assistant",
                    content=complete_response,
                    token_count=len(complete_response) // 4,
                )

                # Embed for future retrieval
                resp_embedding = await generate_embedding(complete_response)
                if resp_embedding:
                    assistant_point_id = str(assistant_episode.id).replace("-", "")
                    await upsert_embedding(
                        project_id=project_id,
                        point_id=assistant_point_id,
                        vector=resp_embedding,
                        payload={
                            "content": complete_response,
                            "role": "assistant",
                            "source_type": "conversation",
                            "session_id": str(session_id),
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        },
                    )

                await post_db.commit()

            # Send completion event
            yield {
                "event": "done",
                "data": json.dumps({
                    "session_id": str(session_id),
                    "total_length": len(complete_response),
                }),
            }

        except Exception as e:
            logger.error("stream_error", error=str(e)[:200])
            yield {
                "event": "error",
                "data": json.dumps({
                    "error": {
                        "code": "STREAM_ERROR",
                        "message": "An error occurred during streaming.",
                    }
                }),
            }

    return EventSourceResponse(event_generator())
