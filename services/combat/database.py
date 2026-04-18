"""Async SQLAlchemy engine and session factory for the combat service."""
import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

_raw_url: str = os.environ["DATABASE_URL"]
DATABASE_URL = (
    _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if _raw_url.startswith("postgresql://")
    else _raw_url
)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
