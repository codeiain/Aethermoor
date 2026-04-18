"""E2E test configuration.

These tests require a live AETHERMOOR stack (all services up via docker compose).
Set GATEWAY_URL to the gateway base URL (default: http://localhost:8000).

Run: pytest tests/e2e/ -v
Skip if stack is down: tests auto-skip when the gateway is unreachable.
"""
from __future__ import annotations

import os
import uuid

import httpx
import pytest
import pytest_asyncio

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8000")


def _unique_username() -> str:
    return f"e2e_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def http_client():
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=15.0) as client:
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def require_gateway(http_client: httpx.AsyncClient):
    """Skip entire suite if the gateway is unreachable."""
    try:
        resp = await http_client.get("/health")
        if resp.status_code != 200:
            pytest.skip(f"Gateway returned {resp.status_code} — stack not ready")
    except httpx.ConnectError:
        pytest.skip(f"Gateway unreachable at {GATEWAY_URL} — start the stack first")


@pytest_asyncio.fixture(scope="session")
async def registered_user(http_client: httpx.AsyncClient) -> dict:
    """Register a fresh user for the session and return {username, password, token}."""
    username = _unique_username()
    password = "E2ePassword1!"
    resp = await http_client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 201, f"register failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"username": username, "password": password, "token": token}


@pytest_asyncio.fixture(scope="session")
async def auth_headers(registered_user: dict) -> dict:
    return {"Authorization": f"Bearer {registered_user['token']}"}


@pytest_asyncio.fixture(scope="session")
async def character(http_client: httpx.AsyncClient, auth_headers: dict) -> dict:
    """Create a character for the session and return the character dict."""
    resp = await http_client.post(
        "/players/create",
        json={"name": "E2eHero", "class_name": "warrior", "slot": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 201, f"character creation failed: {resp.text}"
    return resp.json()
