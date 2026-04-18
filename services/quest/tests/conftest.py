"""Pytest fixtures for quest service unit tests.

Unit tests only — no real database or HTTP clients. All external dependencies
are mocked via monkeypatching or dependency_overrides.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("SERVICE_TOKEN", "test-service-token")
os.environ.setdefault("AUTH_SERVICE_URL", "http://auth:8001")
os.environ.setdefault("CHARACTER_SERVICE_URL", "http://character:8002")
os.environ.setdefault("INVENTORY_SERVICE_URL", "http://inventory:8010")

import pytest
