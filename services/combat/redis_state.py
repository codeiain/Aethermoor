"""Redis-backed combat state storage for the AETHERMOOR Combat Service.

Redis DB 2 is allocated to the combat service.

Key schema:
  combat:{combat_id}:state   — JSON string of CombatState (TTL 30 min)
"""
from __future__ import annotations

import json
import os

from redis.asyncio import Redis

REDIS_URL: str = os.environ["REDIS_URL"]

_redis_client: Redis | None = None

_COMBAT_TTL_SECONDS = 1800  # 30 minutes


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


def _state_key(combat_id: str) -> str:
    return f"combat:{combat_id}:state"


async def save_combat_state(combat_id: str, state_dict: dict) -> None:
    """Persist combat state to Redis with a 30-minute TTL."""
    redis = get_redis()
    await redis.set(
        _state_key(combat_id),
        json.dumps(state_dict),
        ex=_COMBAT_TTL_SECONDS,
    )


async def load_combat_state(combat_id: str) -> dict | None:
    """Load combat state from Redis. Returns None if not found or expired."""
    redis = get_redis()
    raw = await redis.get(_state_key(combat_id))
    if raw is None:
        return None
    return json.loads(raw)


async def delete_combat_state(combat_id: str) -> None:
    """Remove a combat state from Redis (called after persisting to DB)."""
    redis = get_redis()
    await redis.delete(_state_key(combat_id))


async def refresh_combat_ttl(combat_id: str) -> None:
    """Reset the TTL on an active combat (called on each action)."""
    redis = get_redis()
    await redis.expire(_state_key(combat_id), _COMBAT_TTL_SECONDS)
