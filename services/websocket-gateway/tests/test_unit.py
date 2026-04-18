"""Unit tests for the WebSocket Gateway — no Redis or live WebSocket required."""
from __future__ import annotations

import os
import sys
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("SERVICE_TOKEN", "test-service-token-wsgateway-unit")
os.environ.setdefault("REDIS_URL", "redis://:unused@localhost:6379/5")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import websockets  # noqa: F401 — ensure import doesn't break
from main import (
    ConnectionManager,
    _make_service_token,
    _verify_service_token,
    verify_player_token,
)


# ── Service token ─────────────────────────────────────────────────────────────

class TestServiceToken:
    def test_make_token_has_correct_format(self):
        token = _make_service_token()
        parts = token.split(":")
        assert len(parts) == 2
        ts, digest = parts
        assert ts.isdigit()
        assert len(digest) == 64

    def test_verify_current_token(self):
        token = _make_service_token()
        assert _verify_service_token(token) is True

    def test_empty_string_rejected(self):
        assert _verify_service_token("") is False

    def test_malformed_rejected(self):
        assert _verify_service_token("notvalidformat") is False

    def test_wrong_secret_rejected(self):
        import hashlib
        import hmac
        ts = int(time.time()) // 60
        bad_digest = hmac.new(b"wrong", str(ts).encode(), hashlib.sha256).hexdigest()
        assert _verify_service_token(f"{ts}:{bad_digest}") is False


# ── ConnectionManager ─────────────────────────────────────────────────────────

class TestConnectionManager:
    def _ws_mock(self) -> AsyncMock:
        ws = AsyncMock()
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        ws.close = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_connect_adds_player(self):
        mgr = ConnectionManager()
        ws = self._ws_mock()

        await mgr.connect(ws, "player-1", "zone:001")

        assert "player-1" in mgr.active
        assert "player-1" in mgr.channels["zone:001"]
        ws.accept.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_disconnect_removes_player(self):
        mgr = ConnectionManager()
        ws = self._ws_mock()
        await mgr.connect(ws, "player-1", "zone:001")

        await mgr.disconnect("player-1")

        assert "player-1" not in mgr.active
        assert "player-1" not in mgr.channels.get("zone:001", set())

    @pytest.mark.asyncio
    async def test_disconnect_unknown_player_is_noop(self):
        mgr = ConnectionManager()
        await mgr.disconnect("ghost-player")  # Should not raise

    @pytest.mark.asyncio
    async def test_send_to_player_sends_json(self):
        mgr = ConnectionManager()
        ws = self._ws_mock()
        await mgr.connect(ws, "player-1", "zone:001")

        msg = {"type": "chat", "message": "hello"}
        await mgr.send_to_player("player-1", msg)

        ws.send_json.assert_awaited_once_with(msg)

    @pytest.mark.asyncio
    async def test_send_to_unknown_player_is_noop(self):
        mgr = ConnectionManager()
        # Should not raise even if player not connected
        await mgr.send_to_player("ghost", {"type": "chat"})

    @pytest.mark.asyncio
    async def test_broadcast_reaches_all_channel_members(self):
        mgr = ConnectionManager()
        ws1, ws2, ws3 = self._ws_mock(), self._ws_mock(), self._ws_mock()
        await mgr.connect(ws1, "player-1", "zone:001")
        await mgr.connect(ws2, "player-2", "zone:001")
        await mgr.connect(ws3, "player-3", "zone:002")

        msg = {"type": "zone_event", "event": "rain"}
        await mgr.broadcast_to_channel("zone:001", msg)

        ws1.send_json.assert_awaited_once_with(msg)
        ws2.send_json.assert_awaited_once_with(msg)
        ws3.send_json.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_broadcast_empty_channel_is_noop(self):
        mgr = ConnectionManager()
        await mgr.broadcast_to_channel("zone:empty", {"type": "event"})

    @pytest.mark.asyncio
    async def test_multiple_players_same_channel(self):
        mgr = ConnectionManager()
        ws1, ws2 = self._ws_mock(), self._ws_mock()
        await mgr.connect(ws1, "p1", "zone:X")
        await mgr.connect(ws2, "p2", "zone:X")

        assert len(mgr.channels["zone:X"]) == 2

    @pytest.mark.asyncio
    async def test_disconnect_leaves_other_players_in_channel(self):
        mgr = ConnectionManager()
        ws1, ws2 = self._ws_mock(), self._ws_mock()
        await mgr.connect(ws1, "p1", "zone:X")
        await mgr.connect(ws2, "p2", "zone:X")

        await mgr.disconnect("p1")

        assert "p2" in mgr.channels["zone:X"]
        assert "p1" not in mgr.channels["zone:X"]


# ── verify_player_token ───────────────────────────────────────────────────────

class TestVerifyPlayerToken:
    @pytest.mark.asyncio
    async def test_invalid_service_token_rejected(self):
        result = await verify_player_token("player-1", "some-token", "bad-service-token")
        assert result is False

    @pytest.mark.asyncio
    async def test_no_redis_client_rejected(self):
        import main
        original = main._redis_client
        main._redis_client = None
        try:
            token = _make_service_token()
            result = await verify_player_token("player-1", "some-token", token)
            assert result is False
        finally:
            main._redis_client = original
