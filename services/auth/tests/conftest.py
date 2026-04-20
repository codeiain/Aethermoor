"""Pytest fixtures for auth service integration tests.

Requires real Postgres and Redis (set via env vars or docker-compose).
No mocks — as per project policy (see DEPENDENCY_SECURITY_REVIEW.md).
"""
import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Environment — integration tests read from environment (populated by docker-compose or CI)
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql+asyncpg://aethermoor:aethermoor@localhost:55432/aethermoor"),
).replace("postgresql://", "postgresql+asyncpg://", 1)

TEST_REDIS_URL = os.environ.get(
    "TEST_REDIS_URL",
    os.environ.get("REDIS_URL", "redis://:testpassword@localhost:6379/1"),
)

# Patch env before importing service modules
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["REDIS_URL"] = TEST_REDIS_URL
os.environ.setdefault("JWT_SECRET", "integration-test-secret-not-for-production")
os.environ.setdefault("SERVICE_TOKEN", "integration-test-service-token-not-for-production")

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Base, engine as _engine
from main import app


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create tables once per test session, drop them on teardown."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture
async def client(test_engine) -> AsyncClient:
    """Async HTTP client wired to the FastAPI app via ASGI transport."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
