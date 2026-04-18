"""Unit tests for the chat service stub."""
from __future__ import annotations

import os
import sys

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("SERVICE_TOKEN", "test-service-token-chat-unit")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app


class TestChatHealth:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "chat"

    @pytest.mark.asyncio
    async def test_metrics_endpoint_returns_text(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/metrics")
        assert resp.status_code == 200
        assert "text/plain" in resp.headers["content-type"]
