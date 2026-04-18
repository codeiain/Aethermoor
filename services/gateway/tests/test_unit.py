"""Unit tests for the gateway service pure functions."""
from __future__ import annotations

import os
import sys
import time
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("SERVICE_TOKEN", "test-service-token-gateway-unit")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import (
    _make_service_token,
    _check_rate_limit,
    _client_ip,
    _WINDOW_SECONDS,
    _DEFAULT_LIMIT,
    _ENDPOINT_LIMITS,
    _counters,
)


# ── Service token ─────────────────────────────────────────────────────────────

class TestServiceToken:
    def test_token_format(self):
        token = _make_service_token()
        parts = token.split(":")
        assert len(parts) == 2
        ts, digest = parts
        assert ts.isdigit()
        assert len(digest) == 64  # SHA-256 hex

    def test_timestamp_is_current_minute_bucket(self):
        token = _make_service_token()
        ts = int(token.split(":")[0])
        expected = int(time.time()) // 60
        assert ts in (expected, expected - 1)

    def test_two_tokens_in_same_minute_share_ts(self):
        t1 = _make_service_token()
        t2 = _make_service_token()
        assert t1.split(":")[0] == t2.split(":")[0]


# ── Client IP extraction ──────────────────────────────────────────────────────

class TestClientIp:
    def _req(self, forwarded=None, client_host=None):
        req = MagicMock()
        req.headers.get = lambda key, default=None: forwarded if key == "x-forwarded-for" else default
        req.client = MagicMock(host=client_host) if client_host else None
        return req

    def test_uses_x_forwarded_for_first(self):
        req = self._req(forwarded="1.2.3.4, 5.6.7.8", client_host="9.9.9.9")
        assert _client_ip(req) == "1.2.3.4"

    def test_falls_back_to_client_host(self):
        req = self._req(forwarded=None, client_host="10.0.0.1")
        assert _client_ip(req) == "10.0.0.1"

    def test_unknown_when_no_client(self):
        req = self._req(forwarded=None, client_host=None)
        assert _client_ip(req) == "unknown"

    def test_strips_whitespace_from_forwarded(self):
        req = self._req(forwarded="  2.3.4.5  , other")
        assert _client_ip(req) == "2.3.4.5"


# ── Rate limiting ─────────────────────────────────────────────────────────────

class TestRateLimit:
    def setup_method(self):
        _counters.clear()

    @pytest.mark.asyncio
    async def test_first_request_allowed(self):
        allowed = await _check_rate_limit("1.1.1.1", "/some/path")
        assert allowed is True

    @pytest.mark.asyncio
    async def test_within_limit_allowed(self):
        for _ in range(10):
            allowed = await _check_rate_limit("1.1.1.2", "/some/path")
            assert allowed is True

    @pytest.mark.asyncio
    async def test_exceed_custom_endpoint_limit(self):
        ip = "1.1.1.3"
        path = "/auth/login"
        limit = _ENDPOINT_LIMITS[path]
        for _ in range(limit):
            await _check_rate_limit(ip, path)
        result = await _check_rate_limit(ip, path)
        assert result is False

    @pytest.mark.asyncio
    async def test_different_ips_independent(self):
        path = "/auth/login"
        limit = _ENDPOINT_LIMITS[path]
        for _ in range(limit):
            await _check_rate_limit("2.2.2.2", path)
        # Different IP should still be allowed
        result = await _check_rate_limit("3.3.3.3", path)
        assert result is True

    @pytest.mark.asyncio
    async def test_window_reset_allows_new_requests(self):
        ip = "4.4.4.4"
        path = "/auth/register"
        limit = _ENDPOINT_LIMITS[path]
        for _ in range(limit):
            await _check_rate_limit(ip, path)
        # Manually expire the window
        key = f"{ip}:{path}"
        old_start, count = _counters[key]
        _counters[key] = (old_start - _WINDOW_SECONDS - 1, count)
        result = await _check_rate_limit(ip, path)
        assert result is True

    @pytest.mark.asyncio
    async def test_login_has_stricter_limit_than_default(self):
        assert _ENDPOINT_LIMITS["/auth/login"] < _DEFAULT_LIMIT

    @pytest.mark.asyncio
    async def test_register_has_stricter_limit_than_login(self):
        assert _ENDPOINT_LIMITS["/auth/register"] < _ENDPOINT_LIMITS["/auth/login"]
