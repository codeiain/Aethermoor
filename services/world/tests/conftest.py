"""Pytest configuration and fixtures for world service integration tests.

Integration tests run against real PostgreSQL + Redis.
DATABASE_URL and REDIS_URL must be set in the environment.
"""
import asyncio
import os
import sys

import pytest
import pytest_asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set required env vars before any service imports
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://aethermoor:aethermoor@localhost:5432/aethermoor_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")  # DB 15: test isolation
os.environ.setdefault("SERVICE_TOKEN", "test-service-token-for-world-tests")
os.environ.setdefault("AUTH_SERVICE_URL", "http://auth:8001")
os.environ.setdefault("CHARACTER_SERVICE_URL", "http://character:8002")

from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database import Base, get_db
from main import app

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
if TEST_DATABASE_URL.startswith("postgresql://"):
    TEST_DATABASE_URL = TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

_test_engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
_TestSession = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create tables once per test session, drop them after."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _test_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    """Truncate all tables between tests for isolation."""
    yield
    async with _test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture(autouse=True)
async def clean_redis():
    """Flush the test Redis DB between tests."""
    redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    yield
    await redis.flushdb()
    await redis.aclose()


@pytest_asyncio.fixture
async def db_session():
    async with _TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """AsyncClient with DB session override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seeded_client(db_session):
    """Client with seed zones pre-loaded."""
    from seed import seed_zones

    await seed_zones(db_session)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
