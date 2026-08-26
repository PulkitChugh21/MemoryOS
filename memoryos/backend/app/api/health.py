"""
MemoryOS Backend — Health Check Route
"""

import os
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


@router.get("/health/debug")
async def health_debug():
    """Debug endpoint — tests actual database connection and reports CORS config."""
    settings = get_settings()
    results = {}

    # Test actual DB connection
    try:
        from app.db.session import get_engine
        from sqlalchemy import text
        engine = get_engine()
        async with engine.connect() as conn:
            row = await conn.execute(text("SELECT 1"))
            results["database"] = "connected_ok"
    except Exception as e:
        results["database"] = f"FAILED: {type(e).__name__}: {str(e)}"

    # Test Qdrant
    try:
        from app.memory.semantic import get_qdrant_client
        client = get_qdrant_client()
        collections = await client.get_collections()
        results["qdrant"] = f"connected_ok ({len(collections.collections)} collections)"
    except Exception as e:
        results["qdrant"] = f"FAILED: {type(e).__name__}: {str(e)}"

    # CORS config
    results["cors_origins"] = settings.cors_origins_list
    results["cors_env_raw"] = os.environ.get("CORS_ORIGINS", "NOT_SET")

    # DB URL (masked)
    db_url = settings.database_url
    if "@" in db_url:
        masked = db_url.split("@")[0][:20] + "...@" + db_url.split("@")[1][:30] + "..."
    else:
        masked = "invalid_format"
    results["database_url_masked"] = masked

    return results

