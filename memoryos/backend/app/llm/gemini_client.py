"""
MemoryOS Backend — Gemini API Client
Wrapper for Gemini LLM with retry + exponential backoff (Rules.md §3).
Currently uses gemini-3-flash-preview.
"""

import asyncio
from typing import AsyncGenerator, Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("llm.gemini")

_configured = False


def _ensure_configured():
    """Configure the Gemini API key once."""
    global _configured
    if not _configured:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True
        logger.info("gemini_api_configured")


async def generate_response(
    prompt: str,
    system_instruction: Optional[str] = None,
    max_retries: int = 3,
) -> str:
    """
    Generate a complete response from Gemini.
    Retries with exponential backoff on transient failures (Rules.md §3).
    Fails fast on quota exhaustion to avoid multi-minute hangs.

    Args:
        prompt: The full prompt including context and user message.
        system_instruction: Optional system-level instruction.
        max_retries: Max retry attempts (default 3 per Rules.md).

    Returns:
        The generated text response.
    """
    _ensure_configured()
    settings = get_settings()

    model = genai.GenerativeModel(
        model_name=settings.llm_model,
        system_instruction=system_instruction,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=settings.llm_max_output_tokens,
            temperature=settings.llm_temperature,
        ),
    )

    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                request_options={"timeout": 60},
            )
            return response.text

        except google_exceptions.ResourceExhausted as e:
            # Quota exhausted — fail fast, don't retry
            logger.error("gemini_quota_exhausted", error=str(e)[:150])
            raise RuntimeError(
                "Gemini API quota exhausted. Please wait or check your plan at https://ai.google.dev/gemini-api/docs/rate-limits"
            ) from e

        except Exception as e:
            error_str = str(e).lower()
            is_transient = any(
                keyword in error_str
                for keyword in ["rate limit", "timeout", "503", "overloaded"]
            )

            if is_transient and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(
                    "gemini_retry",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    wait_seconds=wait_time,
                    error=str(e)[:150],
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    "gemini_failed",
                    attempt=attempt + 1,
                    error=str(e)[:150],
                )
                raise


async def generate_response_stream(
    prompt: str,
    system_instruction: Optional[str] = None,
    max_retries: int = 3,
) -> AsyncGenerator[str, None]:
    """
    Stream a response from Gemini chunk by chunk.
    Used for SSE streaming in the chat endpoint.
    Retries with exponential backoff on transient failures.
    """
    _ensure_configured()
    settings = get_settings()

    model = genai.GenerativeModel(
        model_name=settings.llm_model,
        system_instruction=system_instruction,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=settings.llm_max_output_tokens,
            temperature=settings.llm_temperature,
        ),
    )

    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                stream=True,
                request_options={"timeout": 60},
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

            return  # Success — exit retry loop

        except google_exceptions.ResourceExhausted as e:
            logger.error("gemini_stream_quota_exhausted", error=str(e)[:150])
            raise RuntimeError(
                "Gemini API quota exhausted. Please wait or check your plan."
            ) from e

        except Exception as e:
            error_str = str(e).lower()
            is_transient = any(
                keyword in error_str
                for keyword in ["rate limit", "timeout", "503", "overloaded"]
            )

            if is_transient and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(
                    "gemini_stream_retry",
                    attempt=attempt + 1,
                    wait_seconds=wait_time,
                    error=str(e)[:150],
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    "gemini_stream_failed",
                    attempt=attempt + 1,
                    error=str(e)[:150],
                )
                raise
