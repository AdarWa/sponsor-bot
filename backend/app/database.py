"""Async database session and declarative base configuration."""
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """Declarative base class for SQLAlchemy models."""

    pass


engine = create_async_engine(
    settings.resolved_database_url,
    future=True,
    connect_args=settings.sqlalchemy_connect_args(),
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that provides an AsyncSession per request."""

    async with async_session_maker() as session:
        yield session
