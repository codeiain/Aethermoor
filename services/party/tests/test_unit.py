"""Unit tests for the party service — no Redis required."""
from __future__ import annotations

import os
import sys
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Set required env vars before importing service module
os.environ.setdefault("SERVICE_TOKEN", "test-service-token-party-unit")
os.environ.setdefault("REDIS_URL", "redis://:unused@localhost:6379/5")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import (
    PartyService,
    xp_multiplier,
    _make_service_token,
    _verify_service_token,
    MAX_PARTY_SIZE,
)


# ── XP multiplier ──────────────────────────────────────────────────────────────

class TestXpMultiplier:
    @pytest.mark.parametrize("size,expected", [
        (1, 1.00),
        (2, 1.10),
        (3, 1.12),
        (4, 1.15),
        (5, 1.18),
        (6, 1.00),  # unknown → fallback 1.0
    ])
    def test_multiplier_by_size(self, size, expected):
        assert xp_multiplier(size) == expected

    def test_solo_has_no_bonus(self):
        assert xp_multiplier(1) == 1.0

    def test_full_party_has_max_bonus(self):
        assert xp_multiplier(MAX_PARTY_SIZE) == 1.18


# ── Zero-trust service token ──────────────────────────────────────────────────

class TestServiceToken:
    def test_make_and_verify(self):
        token = _make_service_token()
        assert _verify_service_token(token) is True

    def test_none_rejected(self):
        assert _verify_service_token(None) is False

    def test_empty_rejected(self):
        assert _verify_service_token("") is False

    def test_malformed_rejected(self):
        assert _verify_service_token("notimestamp") is False

    def test_expired_rejected(self):
        import hashlib
        import hmac
        old_bucket = (int(time.time()) // 60) - 5
        secret = os.environ["SERVICE_TOKEN"]
        digest = hmac.new(
            secret.encode(),
            str(old_bucket).encode(),
            hashlib.sha256,
        ).hexdigest()
        assert _verify_service_token(f"{old_bucket}:{digest}") is False

    def test_wrong_secret_rejected(self):
        import hashlib
        import hmac
        ts = int(time.time()) // 60
        bad_digest = hmac.new(
            b"wrong-secret",
            str(ts).encode(),
            hashlib.sha256,
        ).hexdigest()
        assert _verify_service_token(f"{ts}:{bad_digest}") is False


# ── PartyService — mocked Redis ───────────────────────────────────────────────

def _make_redis_mock(**overrides) -> AsyncMock:
    """Build a minimal async Redis mock."""
    mock = AsyncMock()
    mock.hset = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=1)
    mock.sadd = AsyncMock(return_value=1)
    mock.srem = AsyncMock(return_value=1)
    mock.smembers = AsyncMock(return_value=set())
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.hgetall = AsyncMock(return_value={})
    mock.sismember = AsyncMock(return_value=False)
    mock.hset = AsyncMock(return_value=1)
    for k, v in overrides.items():
        setattr(mock, k, v)
    return mock


class TestPartyServiceCreate:
    @pytest.mark.asyncio
    async def test_create_party_returns_party_data(self):
        redis_mock = _make_redis_mock()
        svc = PartyService(redis_mock)

        result = await svc.create_party("char-001", "Aldric")

        assert result["leader_id"] == "char-001"
        assert "char-001" in result["members"]
        assert result["loot_mode"] == "free_for_all"
        assert "party_id" in result

    @pytest.mark.asyncio
    async def test_create_party_increments_redis_sets(self):
        redis_mock = _make_redis_mock()
        svc = PartyService(redis_mock)

        await svc.create_party("char-001", "Aldric")

        redis_mock.hset.assert_called_once()
        redis_mock.sadd.assert_called()


class TestPartyServiceGetParty:
    @pytest.mark.asyncio
    async def test_returns_none_when_player_not_in_party(self):
        redis_mock = _make_redis_mock(get=AsyncMock(return_value=None))
        svc = PartyService(redis_mock)

        result = await svc.get_party("char-999")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_party_data_missing(self):
        redis_mock = _make_redis_mock(
            get=AsyncMock(return_value="party-abc"),
            hgetall=AsyncMock(return_value={}),
        )
        svc = PartyService(redis_mock)

        result = await svc.get_party("char-001")

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_party_with_members(self):
        redis_mock = _make_redis_mock(
            get=AsyncMock(return_value="party-abc"),
            hgetall=AsyncMock(return_value={
                "leader_id": "char-001",
                "leader_name": "Aldric",
                "loot_mode": "free_for_all",
            }),
            smembers=AsyncMock(return_value={"char-001", "char-002"}),
        )
        svc = PartyService(redis_mock)

        result = await svc.get_party("char-001")

        assert result["leader_id"] == "char-001"
        assert len(result["members"]) == 2
        assert result["xp_multiplier"] == xp_multiplier(2)


class TestPartyServiceLeave:
    @pytest.mark.asyncio
    async def test_leave_returns_false_when_not_in_party(self):
        redis_mock = _make_redis_mock(get=AsyncMock(return_value=None))
        svc = PartyService(redis_mock)

        result = await svc.leave_party("char-999")

        assert result is False

    @pytest.mark.asyncio
    async def test_non_leader_leave_removes_member(self):
        party_id = "party-abc"
        redis_mock = _make_redis_mock(
            get=AsyncMock(return_value=party_id),
            hgetall=AsyncMock(return_value={
                "leader_id": "char-leader",
                "leader_name": "Leader",
                "loot_mode": "free_for_all",
            }),
            smembers=AsyncMock(return_value={"char-leader", "char-member"}),
        )
        svc = PartyService(redis_mock)

        result = await svc.leave_party("char-member")

        assert result is True
        redis_mock.srem.assert_called()
        redis_mock.delete.assert_called()


class TestPartyServiceKick:
    @pytest.mark.asyncio
    async def test_cannot_kick_self(self):
        from fastapi import HTTPException
        party_id = "party-abc"
        redis_mock = _make_redis_mock(
            get=AsyncMock(return_value=party_id),
            hgetall=AsyncMock(return_value={
                "leader_id": "char-leader",
                "leader_name": "Leader",
                "loot_mode": "free_for_all",
            }),
            smembers=AsyncMock(return_value={"char-leader", "char-member"}),
        )
        svc = PartyService(redis_mock)

        with pytest.raises(HTTPException) as exc_info:
            await svc.kick_member("char-leader", "char-leader")

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_non_leader_cannot_kick(self):
        from fastapi import HTTPException
        party_id = "party-abc"
        redis_mock = _make_redis_mock(
            get=AsyncMock(return_value=party_id),
            hgetall=AsyncMock(return_value={
                "leader_id": "char-leader",
                "leader_name": "Leader",
                "loot_mode": "free_for_all",
            }),
            smembers=AsyncMock(return_value={"char-leader", "char-member"}),
        )
        svc = PartyService(redis_mock)

        with pytest.raises(HTTPException) as exc_info:
            await svc.kick_member("char-member", "char-leader")

        assert exc_info.value.status_code == 403


class TestPartyServiceLootMode:
    @pytest.mark.asyncio
    async def test_invalid_loot_mode_raises(self):
        from fastapi import HTTPException
        redis_mock = _make_redis_mock(
            get=AsyncMock(return_value="party-abc"),
            hgetall=AsyncMock(return_value={
                "leader_id": "char-001",
                "leader_name": "Aldric",
                "loot_mode": "free_for_all",
            }),
            smembers=AsyncMock(return_value={"char-001"}),
        )
        svc = PartyService(redis_mock)

        with pytest.raises(HTTPException) as exc_info:
            await svc.set_loot_mode("char-001", "last_man_standing")

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_valid_loot_mode_accepted(self):
        party_id = "party-abc"
        call_count = [0]

        async def get_side_effect(key):
            call_count[0] += 1
            if "player" in key:
                return party_id
            return None

        redis_mock = _make_redis_mock(
            get=AsyncMock(side_effect=get_side_effect),
            hgetall=AsyncMock(return_value={
                "leader_id": "char-001",
                "leader_name": "Aldric",
                "loot_mode": "round_robin",
            }),
            smembers=AsyncMock(return_value={"char-001"}),
        )
        svc = PartyService(redis_mock)

        result = await svc.set_loot_mode("char-001", "round_robin")

        redis_mock.hset.assert_called()


class TestPartyServiceInvite:
    @pytest.mark.asyncio
    async def test_invite_fails_when_sender_not_in_party(self):
        from fastapi import HTTPException
        redis_mock = _make_redis_mock(get=AsyncMock(return_value=None))
        svc = PartyService(redis_mock)

        with pytest.raises(HTTPException) as exc_info:
            await svc.send_invite("char-001", "Aldric", "char-002")

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_decline_invite_invalid_format_returns_false(self):
        redis_mock = _make_redis_mock()
        svc = PartyService(redis_mock)

        result = await svc.decline_invite("no-colons-here-none")

        assert result is False
