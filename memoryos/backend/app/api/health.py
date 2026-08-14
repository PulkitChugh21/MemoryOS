"""
MemoryOS Backend — Health Check Route
"""

from fastapi import APIRouter
from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])
logger = get_logger("api.health")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Railway monitoring."""
    settings = get_settings()
    services = {}

    # Check database
    try:
        from app.db.session import get_engine
        engine = get_engine()
        services["database"] = "configured"
    except Exception:
        services["database"] = "error"

    # Check Qdrant
    try:
        from app.memory.semantic import get_qdrant_client
        client = get_qdrant_client()
        services["qdrant"] = "connected"
    except Exception:
        services["qdrant"] = "error"

    # Check Gemini
    services["gemini"] = "configured" if settings.gemini_api_key else "missing"

    return HealthResponse(
        status="ok",
        version="0.1.0",
        phase=1,
        services=services,
    )
