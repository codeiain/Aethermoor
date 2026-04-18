"""Shared test fixtures for economy service tests."""
import os
import sys

# Set required env vars before any service module import
os.environ.setdefault("DATABASE_URL", "postgresql://unused:unused@localhost/unused")
os.environ.setdefault("REDIS_URL", "redis://:unused@localhost:6379/8")
os.environ.setdefault("SERVICE_TOKEN", "test-service-token-do-not-use-in-production")
os.environ.setdefault("AUTH_SERVICE_URL", "http://auth:8001")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
