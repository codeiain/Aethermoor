"""Unit tests for the social service — no Redis required."""
from __future__ import annotations

import os
import sys
import time
from unittest.mock import AsyncMock

import pytest

os.environ.setdefault("SERVICE_TOKEN", "test-service-token-social-unit")
os.environ.setdefault("REDIS_URL", "redis://:unused@localhost:6379/7")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import (
    SocialService,
    _make_service_token,
    _verify_service_token,
)


# ── Service token ─────────────────────────────────────────────────────────────

class TestServiceToken:
    def test_make_and_verify(self):
        token = _make_service_token()
        assert _verify_service_token(token) is True

    def test_none_rejected(self):
        assert _verify_service_token(None) is False

    def test_empty_rejected(self):
        assert _verify_service_token("") is False

    def test_malformed_no_colon(self):
        assert _verify_service_token("notimestamp") is False

    def test_expired_token_rejected(self):
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


# ── SocialService helpers ─────────────────────────────────────────────────────

def _make_redis_mock(**overrides) -> AsyncMock:
    mock = AsyncMock()
    mock.set = AsyncMock(return_value=True)
    mock.get = AsyncMock(return_value=None)
    mock.delete = AsyncMock(return_value=1)
    mock.sadd = AsyncMock(return_value=1)
    mock.srem = AsyncMock(return_value=1)
    mock.smembers = AsyncMock(return_value=set())
    mock.sismember = AsyncMock(return_value=False)
    for k, v in overrides.items():
        setattr(mock, k, v)
    return mock


# ── Online status ─────────────────────────────────────────────────────────────

class TestOnlineStatus:
    @pytest.mark.asyncio
    async def test_set_online_returns_online_true(self):
        svc = SocialService(_make_redis_mock())
        result = await svc.set_online_status("char-001", "Aldric")
        assert result["online"] is True
        assert result["character_id"] == "char-001"

    @pytest.mark.asyncio
    async def test_set_offline_returns_online_false(self):
        svc = SocialService(_make_redis_mock(srem=AsyncMock(return_value=1)))
        result = await svc.set_offline_status("char-001")
        assert result["online"] is False
        assert result["character_id"] == "char-001"

    @pytest.mark.asyncio
    async def test_get_status_offline_player(self):
        redis_mock = _make_redis_mock(
            sismember=AsyncMock(return_value=False),
            get=AsyncMock(return_value=None),
        )
        svc = SocialService(redis_mock)
        result = await svc.get_online_status("char-999")
        assert result["online"] is False

    @pytest.mark.asyncio
    async def test_get_status_online_player_with_data(self):
        import json
        redis_mock = _make_redis_mock(
            sismember=AsyncMock(return_value=True),
            get=AsyncMock(return_value=json.dumps({"name": "Aldric", "last_seen": 1000.0})),
        )
        svc = SocialService(redis_mock)
        result = await svc.get_online_status("char-001")
        assert result["online"] is True
        assert result["last_seen"] == 1000.0


# ── Friend requests ───────────────────────────────────────────────────────────

class TestFriendRequests:
    @pytest.mark.asyncio
    async def test_send_request_fails_if_target_not_found(self):
        from fastapi import HTTPException
        redis_mock = _make_redis_mock(get=AsyncMock(return_value=None))
        svc = SocialService(redis_mock)

        with pytest.raises(HTTPException) as exc_info:
            await svc.send_friend_request("char-001", "Aldric", "UnknownPlayer")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_send_request_blocked_player_rejected(self):
        from fastapi import HTTPException
        redis_mock = _make_redis_mock(
            get=AsyncMock(return_value="char-002"),
            sismember=AsyncMock(return_value=True),
        )
        svc = SocialService(redis_mock)

        with pytest.raises(HTTPException) as exc_info:
            await svc.send_friend_request("char-001", "Aldric", "Brom")

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_send_request_already_friends_rejected(self):
        from fastapi import HTTPException
        call_count = [0]

        async def sismember_side_effect(key, val):
            call_count[0] += 1
            if "blocked" in key:
                return False
            if "friends" in key:
                return True
            return False

        redis_mock = _make_redis_mock(
            get=AsyncMock(return_value="char-002"),
            sismember=AsyncMock(side_effect=sismember_side_effect),
        )
        svc = SocialService(redis_mock)

        with pytest.raises(HTTPException) as exc_info:
            await svc.send_friend_request("char-001", "Aldric", "Brom")

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_accept_request_invalid_format_raises(self):
        from fastapi import HTTPException
        svc = SocialService(_make_redis_mock())

        with pytest.raises(HTTPException) as exc_info:
            await svc.accept_friend_request("nocolon")

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_accept_request_not_found_raises(self):
        from fastapi import HTTPException
        redis_mock = _make_redis_mock(get=AsyncMock(return_value=None))
        svc = SocialService(redis_mock)

        with pytest.raises(HTTPException) as exc_info:
            await svc.accept_friend_request("char-001:char-002")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_accept_request_success(self):
        import json
        request_data = json.dumps({
            "from_id": "char-001",
            "from_name": "Aldric",
            "to_id": "char-002",
            "timestamp": time.time(),
        })
        redis_mock = _make_redis_mock(get=AsyncMock(return_value=request_data))
        svc = SocialService(redis_mock)

        result = await svc.accept_friend_request("char-001:char-002")

        assert result["success"] is True
        assert result["friend_id"] == "char-002"
        redis_mock.sadd.assert_called()
        redis_mock.delete.assert_called()

    @pytest.mark.asyncio
    async def test_decline_request_invalid_format(self):
        svc = SocialService(_make_redis_mock())
        result = await svc.decline_friend_request("nocol")
        assert result is False

    @pytest.mark.asyncio
    async def test_remove_friend_always_succeeds(self):
        svc = SocialService(_make_redis_mock())
        result = await svc.remove_friend("char-001", "char-002")
        assert result is True


# ── Block list ────────────────────────────────────────────────────────────────

class TestBlockList:
    @pytest.mark.asyncio
    async def test_cannot_block_yourself(self):
        from fastapi import HTTPException
        redis_mock = _make_redis_mock(get=AsyncMock(return_value="char-001"))
        svc = SocialService(redis_mock)

        with pytest.raises(HTTPException) as exc_info:
            await svc.block_player("char-001", "self")

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_block_player_not_found(self):
        from fastapi import HTTPException
        redis_mock = _make_redis_mock(get=AsyncMock(return_value=None))
        svc = SocialService(redis_mock)

        with pytest.raises(HTTPException) as exc_info:
            await svc.block_player("char-001", "ghost")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_block_player_success(self):
        redis_mock = _make_redis_mock(get=AsyncMock(return_value="char-002"))
        svc = SocialService(redis_mock)

        result = await svc.block_player("char-001", "Brom")

        assert result["success"] is True
        assert result["blocked_id"] == "char-002"
        redis_mock.sadd.assert_called()

    @pytest.mark.asyncio
    async def test_unblock_player_always_succeeds(self):
        svc = SocialService(_make_redis_mock())
        result = await svc.unblock_player("char-001", "char-002")
        assert result is True

    @pytest.mark.asyncio
    async def test_is_blocked_check(self):
        redis_mock = _make_redis_mock(sismember=AsyncMock(return_value=True))
        svc = SocialService(redis_mock)

        result = await svc.is_blocked("char-002", "char-001")

        assert result is True
