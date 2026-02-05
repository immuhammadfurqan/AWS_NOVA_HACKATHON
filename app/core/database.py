"""
AARLP Database Module

PostgreSQL + pgvector setup for:
- Async connection management
- Vector storage for resume embeddings
- State persistence
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import Column, String, Text, Float, DateTime, Boolean, Integer, text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings


Base = declarative_base()


# ============================================================================
# Database Connection
# ============================================================================

_engine = None
_session_factory = None


def get_engine():
    """Get or create the async engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_factory():
    """Get or create the session factory."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_database():
    """Initialize database tables and pgvector extension."""
    engine = get_engine()
    
    async with engine.begin() as conn:
        # Import all models to ensure they are registered with Base.metadata
        from app.jobs.models import JobRecord
        from app.candidates.models import ApplicantRecord, PrescreeningResponseRecord
        from app.interviews.models import InterviewRecord
        from app.auth.models import User
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_database():
    """Close database connections."""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
