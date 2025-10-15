"""Database connection context manager"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_session_factory


class DatabaseSession:
    """Context manager for database sessions"""
    
    def __init__(self):
        self.session: Optional[AsyncSession] = None
    
    async def __aenter__(self) -> AsyncSession:
        """Enter async context"""
        session_factory = get_session_factory()
        self.session = session_factory()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context"""
        if self.session:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
            await self.session.close()
