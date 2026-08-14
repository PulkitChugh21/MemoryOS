"""
MemoryOS Backend — Async Database Session Factory
Creates async SQLAlchemy sessions connected to Supabase PostgreSQL.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

# Engine is created lazily on first import
_engine = None
_session_factory = None


def get_engine():
    """Get or create the async SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.app_debug,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Check connection health before use
            pool_recycle=300,    # Recycle connections every 5 min (Supabase drops idle)
        )
    return _engine


def get_session_factory():
    """Get or create the async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db() -> AsyncSession:
    """
    FastAPI dependency: yields an async database session.
    Session is automatically closed after the request completes.
    Usage in routes:
        async def my_route(db: AsyncSession = Depends(get_db)):
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine():
    """Dispose the engine on app shutdown to clean up connections."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
