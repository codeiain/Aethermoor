"""Integration tests for economy service endpoints.

External dependencies (DB, Redis, Auth) are mocked so tests run without
live infrastructure. Tests verify the full request/response cycle via
FastAPI's async test client.
"""
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# conftest.py handles env + sys.path before this import
from main import app
from zero_trust import make_service_token

pytestmark = pytest.mark.asyncio


def _service_headers() -> dict:
    return {"X-Service-Token": make_service_token()}


def _user_headers(token: str = "test-token") -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
def mock_db():
    """Provide a mock AsyncSession via dependency override."""
    session = MagicMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()
    session.begin = MagicMock()
    session.begin.return_value.__aenter__ = AsyncMock(return_value=None)
    session.begin.return_value.__aexit__ = AsyncMock(return_value=False)
    return session


@pytest_asyncio.fixture
def mock_config():
    return {
        "gold_cap": 1_000_000,
        "ah_fee_pct": 5.0,
        "listing_duration_hours": 48,
        "gold_drop_min": 1,
        "gold_drop_max": 10,
    }


# ── Health ────────────────────────────────────────────────────────────────────

async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "economy"}


# ── Gold balance ──────────────────────────────────────────────────────────────

async def test_get_gold_requires_service_token(client: AsyncClient):
    response = await client.get("/economy/gold/char-1")
    assert response.status_code == 401


async def test_get_gold_returns_zero_when_no_record(client: AsyncClient, mock_config):
    from database import get_db
    from models import CharacterGold

    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    async def override_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_db
    try:
        response = await client.get("/economy/gold/char-new", headers=_service_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["character_id"] == "char-new"
        assert data["balance"] == 0
    finally:
        app.dependency_overrides.clear()


async def test_get_gold_returns_balance(client: AsyncClient):
    from database import get_db
    from models import CharacterGold

    record = CharacterGold(character_id="char-1", balance=5000)
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = record
    mock_session.execute = AsyncMock(return_value=mock_result)

    async def override_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_db
    try:
        response = await client.get("/economy/gold/char-1", headers=_service_headers())
        assert response.status_code == 200
        assert response.json()["balance"] == 5000
    finally:
        app.dependency_overrides.clear()


# ── Gold award ────────────────────────────────────────────────────────────────

async def test_award_gold_requires_service_token(client: AsyncClient):
    response = await client.post(
        "/economy/gold/award",
        json={"character_id": "c1", "amount": 100},
    )
    assert response.status_code == 401


async def test_award_gold_success(client: AsyncClient, mock_config):
    from database import get_db
    from models import CharacterGold

    record = CharacterGold(character_id="char-1", balance=500)
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = record
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.flush = AsyncMock()
    mock_session.add = MagicMock()

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=None)
    cm.__aexit__ = AsyncMock(return_value=False)
    mock_session.begin = MagicMock(return_value=cm)

    async def override_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_db
    try:
        with patch("routers.economy.cache.get_config", AsyncMock(return_value=mock_config)):
            response = await client.post(
                "/economy/gold/award",
                json={"character_id": "char-1", "amount": 200, "description": "Quest reward"},
                headers=_service_headers(),
            )
        assert response.status_code == 200
        data = response.json()
        assert data["character_id"] == "char-1"
        assert data["balance_after"] == 700
        assert data["amount"] == 200
    finally:
        app.dependency_overrides.clear()


async def test_award_gold_respects_cap(client: AsyncClient, mock_config):
    from database import get_db
    from models import CharacterGold

    cap = mock_config["gold_cap"]
    record = CharacterGold(character_id="char-1", balance=cap - 10)
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = record
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.flush = AsyncMock()
    mock_session.add = MagicMock()

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=None)
    cm.__aexit__ = AsyncMock(return_value=False)
    mock_session.begin = MagicMock(return_value=cm)

    async def override_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_db
    try:
        with patch("routers.economy.cache.get_config", AsyncMock(return_value=mock_config)):
            response = await client.post(
                "/economy/gold/award",
                json={"character_id": "char-1", "amount": 1000},
                headers=_service_headers(),
            )
        assert response.status_code == 200
        data = response.json()
        assert data["balance_after"] == cap
        assert data["amount"] == 10  # capped to only 10
    finally:
        app.dependency_overrides.clear()


# ── Gold deduct ───────────────────────────────────────────────────────────────

async def test_deduct_gold_insufficient_funds(client: AsyncClient, mock_config):
    from database import get_db
    from models import CharacterGold

    record = CharacterGold(character_id="char-1", balance=50)
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = record
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.flush = AsyncMock()

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=None)
    cm.__aexit__ = AsyncMock(return_value=False)
    mock_session.begin = MagicMock(return_value=cm)

    async def override_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_db
    try:
        response = await client.post(
            "/economy/gold/deduct",
            json={"character_id": "char-1", "amount": 100},
            headers=_service_headers(),
        )
        assert response.status_code == 422
        assert "Insufficient gold" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


# ── Listings ──────────────────────────────────────────────────────────────────

async def test_create_listing_requires_auth(client: AsyncClient):
    response = await client.post(
        "/economy/listings",
        json={
            "character_id": "c1", "item_id": "sword",
            "item_name": "Iron Sword", "quantity": 1, "unit_price": 100,
        },
    )
    assert response.status_code == 403  # HTTPBearer returns 403 when header missing


async def test_browse_listings_requires_auth(client: AsyncClient):
    response = await client.get("/economy/listings")
    assert response.status_code == 403


async def test_create_listing_success(client: AsyncClient, mock_config):
    from database import get_db

    mock_session = MagicMock()
    mock_session.add = MagicMock()
    mock_session.flush = AsyncMock()

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=None)
    cm.__aexit__ = AsyncMock(return_value=False)
    mock_session.begin = MagicMock(return_value=cm)

    async def override_db():
        yield mock_session

    async def mock_verify_jwt(token: str) -> dict:
        return {"user_id": "user-1", "username": "tester"}

    app.dependency_overrides[get_db] = override_db
    try:
        with (
            patch("routers.economy.verify_user_jwt", mock_verify_jwt),
            patch("routers.economy.cache.get_config", AsyncMock(return_value=mock_config)),
        ):
            response = await client.post(
                "/economy/listings",
                json={
                    "character_id": "char-1",
                    "item_id": "iron_sword",
                    "item_name": "Iron Sword",
                    "quantity": 2,
                    "unit_price": 500,
                    "category": "weapon",
                },
                headers=_user_headers(),
            )
        assert response.status_code == 201
        data = response.json()
        assert data["item_id"] == "iron_sword"
        assert data["quantity"] == 2
        assert data["unit_price"] == 500
        assert data["total_price"] == 1000
        assert data["status"] == "active"
    finally:
        app.dependency_overrides.clear()


async def test_browse_listings_success(client: AsyncClient):
    from database import get_db
    from models import Listing, ListingStatus, ListingCategory

    future = datetime.now(timezone.utc) + timedelta(days=1)
    listing = Listing(
        id="listing-1",
        seller_character_id="char-1",
        item_id="sword",
        item_name="Iron Sword",
        quantity=1,
        unit_price=200,
        category=ListingCategory.WEAPON,
        level_required=1,
        status=ListingStatus.ACTIVE,
        expires_at=future,
        created_at=datetime.now(timezone.utc),
    )

    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [listing]
    mock_session.execute = AsyncMock(return_value=mock_result)

    async def override_db():
        yield mock_session

    async def mock_verify_jwt(token: str) -> dict:
        return {"user_id": "user-1", "username": "tester"}

    app.dependency_overrides[get_db] = override_db
    try:
        with patch("routers.economy.verify_user_jwt", mock_verify_jwt):
            response = await client.get("/economy/listings", headers=_user_headers())
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "listing-1"
        assert data[0]["total_price"] == 200
    finally:
        app.dependency_overrides.clear()


# ── Cancel listing ────────────────────────────────────────────────────────────

async def test_cancel_listing_wrong_seller(client: AsyncClient):
    from database import get_db
    from models import Listing, ListingStatus

    listing = Listing(
        id="listing-1",
        seller_character_id="char-OTHER",
        item_id="sword",
        item_name="Iron Sword",
        quantity=1,
        unit_price=200,
        status=ListingStatus.ACTIVE,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        created_at=datetime.now(timezone.utc),
        category="weapon",
        level_required=1,
    )

    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = listing
    mock_session.execute = AsyncMock(return_value=mock_result)

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=None)
    cm.__aexit__ = AsyncMock(return_value=False)
    mock_session.begin = MagicMock(return_value=cm)

    async def override_db():
        yield mock_session

    async def mock_verify_jwt(token: str) -> dict:
        return {"user_id": "user-1", "username": "tester"}

    app.dependency_overrides[get_db] = override_db
    try:
        with patch("routers.economy.verify_user_jwt", mock_verify_jwt):
            response = await client.delete(
                "/economy/listings/listing-1?character_id=char-1",
                headers=_user_headers(),
            )
        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


# ── Transaction history ───────────────────────────────────────────────────────

async def test_get_transactions_requires_auth(client: AsyncClient):
    response = await client.get("/economy/transactions?character_id=c1")
    assert response.status_code == 403


async def test_get_transactions_success(client: AsyncClient):
    from database import get_db
    from models import Transaction, TransactionType

    tx = Transaction(
        id="tx-1",
        character_id="char-1",
        type=TransactionType.GOLD_AWARD,
        amount=100,
        balance_after=600,
        description="Quest reward",
        created_at=datetime.now(timezone.utc),
    )

    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [tx]
    mock_session.execute = AsyncMock(return_value=mock_result)

    async def override_db():
        yield mock_session

    async def mock_verify_jwt(token: str) -> dict:
        return {"user_id": "user-1", "username": "tester"}

    app.dependency_overrides[get_db] = override_db
    try:
        with patch("routers.economy.verify_user_jwt", mock_verify_jwt):
            response = await client.get(
                "/economy/transactions?character_id=char-1",
                headers=_user_headers(),
            )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "gold_award"
        assert data[0]["amount"] == 100
    finally:
        app.dependency_overrides.clear()


# ── Admin config ──────────────────────────────────────────────────────────────

async def test_admin_config_requires_service_token(client: AsyncClient):
    response = await client.get("/economy/admin/config")
    assert response.status_code == 401


async def test_admin_get_config(client: AsyncClient, mock_config):
    with patch("routers.admin.cache.get_config", AsyncMock(return_value=mock_config)):
        response = await client.get("/economy/admin/config", headers=_service_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["gold_cap"] == 1_000_000
    assert data["ah_fee_pct"] == 5.0


async def test_admin_update_config(client: AsyncClient, mock_config):
    updated = {**mock_config, "gold_cap": 2_000_000, "ah_fee_pct": 3.0}
    with (
        patch("routers.admin.cache.set_config", AsyncMock()),
        patch("routers.admin.cache.get_config", AsyncMock(return_value=updated)),
    ):
        response = await client.post(
            "/economy/admin/config",
            json={"gold_cap": 2_000_000, "ah_fee_pct": 3.0},
            headers=_service_headers(),
        )
    assert response.status_code == 200
    data = response.json()
    assert data["gold_cap"] == 2_000_000
    assert data["ah_fee_pct"] == 3.0
