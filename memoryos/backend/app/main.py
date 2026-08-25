"""
MemoryOS Backend — FastAPI Application Entrypoint
The main application that wires together all routes and middleware.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.db.session import dispose_engine

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    settings = get_settings()
    setup_logging(debug=settings.app_debug)
    logger.info(
        "memoryos_starting",
        env=settings.app_env,
        debug=settings.app_debug,
        phase=1,
    )
    yield
    await dispose_engine()
    logger.info("memoryos_shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="MemoryOS API",
        description="Persistent AI workspace with self-healing memory",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.app_debug else None,
        redoc_url="/redoc" if settings.app_debug else None,
    )

    # CORS middleware
    origins = settings.cors_origins_list
    logger.info("cors_origins_configured", origins=origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handler — never leak stack traces (Rules.md §3)
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred.",
                    "details": {},
                }
            },
        )

    # Register routers
    from app.api.auth import router as auth_router
    from app.api.projects import router as projects_router
    from app.api.chat import router as chat_router
    from app.api.memory import router as memory_router
    from app.api.health import router as health_router

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(projects_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(memory_router, prefix="/api/v1")
    app.include_router(health_router, prefix="/api/v1")

    return app


# Application instance — used by uvicorn
app = create_app()
