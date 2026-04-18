"""Integration tests for the auth service.

Runs against real Postgres and Redis (no mocks).
Set TEST_DATABASE_URL and TEST_REDIS_URL (or DATABASE_URL / REDIS_URL) in the
environment before running, or use: docker-compose run auth pytest tests/

Each test uses a unique username/email to avoid ordering dependencies.
"""
import os
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


def _unique(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# ── Health ────────────────────────────────────────────────────────────────────

async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert resp.json()["service"] == "auth"


# ── Register ──────────────────────────────────────────────────────────────────

async def test_register_success(client: AsyncClient):
    username = _unique("user")
    resp = await client.post("/auth/register", json={
        "username": username,
        "email": f"{username}@test.example",
        "password": "SecurePass1!",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 15 * 60


async def test_register_duplicate_username(client: AsyncClient):
    username = _unique("dup")
    payload = {"username": username, "email": f"{username}@test.example", "password": "SecurePass1!"}
    await client.post("/auth/register", json=payload)
    # Second registration with same username
    resp = await client.post("/auth/register", json={**payload, "email": f"other_{username}@test.example"})
    assert resp.status_code == 409


async def test_register_short_password(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "username": _unique("u"),
        "email": f"{_unique('e')}@test.example",
        "password": "short",
    })
    assert resp.status_code == 422


async def test_register_invalid_username(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "username": "ab",  # too short (< 3 chars)
        "email": "valid@test.example",
        "password": "SecurePass1!",
    })
    assert resp.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────────

async def test_login_success(client: AsyncClient):
    username = _unique("login")
    await client.post("/auth/register", json={
        "username": username, "email": f"{username}@test.example", "password": "SecurePass1!"
    })
    resp = await client.post("/auth/login", json={"username": username, "password": "SecurePass1!"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password(client: AsyncClient):
    username = _unique("badpw")
    await client.post("/auth/register", json={
        "username": username, "email": f"{username}@test.example", "password": "SecurePass1!"
    })
    resp = await client.post("/auth/login", json={"username": username, "password": "WrongPass99!"})
    assert resp.status_code == 401


async def test_login_unknown_user(client: AsyncClient):
    resp = await client.post("/auth/login", json={"username": "nobody_xyz", "password": "anything"})
    assert resp.status_code == 401


# ── Me ────────────────────────────────────────────────────────────────────────

async def test_me_with_valid_token(client: AsyncClient):
    username = _unique("me")
    reg = await client.post("/auth/register", json={
        "username": username, "email": f"{username}@test.example", "password": "SecurePass1!"
    })
    token = reg.json()["access_token"]
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == username


async def test_me_no_token(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_me_invalid_token(client: AsyncClient):
    resp = await client.get("/auth/me", headers={"Authorization": "Bearer not.a.real.token"})
    assert resp.status_code == 401


# ── Refresh ───────────────────────────────────────────────────────────────────

async def test_refresh_success(client: AsyncClient):
    username = _unique("refresh")
    reg = await client.post("/auth/register", json={
        "username": username, "email": f"{username}@test.example", "password": "SecurePass1!"
    })
    refresh_token = reg.json()["refresh_token"]
    resp = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    # Old refresh token should be rotated (invalid after use)
    resp2 = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp2.status_code == 401


async def test_refresh_with_access_token_fails(client: AsyncClient):
    username = _unique("badrefresh")
    reg = await client.post("/auth/register", json={
        "username": username, "email": f"{username}@test.example", "password": "SecurePass1!"
    })
    access_token = reg.json()["access_token"]
    resp = await client.post("/auth/refresh", json={"refresh_token": access_token})
    assert resp.status_code == 401


# ── Logout ────────────────────────────────────────────────────────────────────

async def test_logout_invalidates_refresh_token(client: AsyncClient):
    username = _unique("logout")
    reg = await client.post("/auth/register", json={
        "username": username, "email": f"{username}@test.example", "password": "SecurePass1!"
    })
    tokens = reg.json()
    await client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    # Refresh should now fail
    resp = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 401


async def test_logout_idempotent(client: AsyncClient):
    """Logging out twice with the same token should not error."""
    username = _unique("logout2")
    reg = await client.post("/auth/register", json={
        "username": username, "email": f"{username}@test.example", "password": "SecurePass1!"
    })
    rt = reg.json()["refresh_token"]
    r1 = await client.post("/auth/logout", json={"refresh_token": rt})
    r2 = await client.post("/auth/logout", json={"refresh_token": rt})
    assert r1.status_code == 200
    assert r2.status_code == 200


# ── Internal verify-service-token ─────────────────────────────────────────────

async def test_verify_service_token_valid(client: AsyncClient):
    from zero_trust import make_service_token
    username = _unique("vst")
    reg = await client.post("/auth/register", json={
        "username": username, "email": f"{username}@test.example", "password": "SecurePass1!"
    })
    access_token = reg.json()["access_token"]

    resp = await client.post(
        "/auth/verify-service-token",
        json={"token": access_token},
        headers={"X-Service-Token": make_service_token()},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["username"] == username


async def test_verify_service_token_invalid_jwt(client: AsyncClient):
    from zero_trust import make_service_token
    resp = await client.post(
        "/auth/verify-service-token",
        json={"token": "not.a.valid.token"},
        headers={"X-Service-Token": make_service_token()},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


async def test_verify_service_token_requires_service_token(client: AsyncClient):
    resp = await client.post(
        "/auth/verify-service-token",
        json={"token": "anything"},
        # No X-Service-Token header
    )
    assert resp.status_code == 401
