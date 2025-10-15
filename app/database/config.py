"""Database configuration and engine setup"""

import os
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from app.models.base import Base

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_database_url() -> str:
    """Get database URL from environment"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://lottery_user:lottery_pass@localhost:5432/lottery_db"
    )


def get_engine() -> AsyncEngine:
    """Get or create database engine"""
    global _engine
    
    if _engine is None:
        database_url = get_database_url()
        logger.info(f"Creating database engine: {database_url.split('@')[1] if '@' in database_url else 'local'}")
        
        _engine = create_async_engine(
            database_url,
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
    
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create session factory"""
    global _session_factory
    
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session (for dependency injection)"""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create all tables"""
    engine = get_engine()
    
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Database tables created successfully")


async def close_db() -> None:
    """Close database connections"""
    global _engine, _session_factory
    
    if _engine:
        logger.info("Closing database connections...")
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("✅ Database connections closed")
