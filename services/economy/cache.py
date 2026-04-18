"""Redis client and live-configurable economy settings."""
import os

from redis.asyncio import Redis

_redis_client: Redis | None = None

REDIS_URL: str = os.environ["REDIS_URL"]

# Default economy config values
_DEFAULTS: dict[str, str] = {
    "gold_cap": "1000000",
    "ah_fee_pct": "5.0",
    "listing_duration_hours": "48",
    "gold_drop_min": "1",
    "gold_drop_max": "10",
}

_CONFIG_KEY = "economy:config"


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


async def get_config() -> dict:
    """Fetch live economy config from Redis, falling back to defaults."""
    redis = get_redis()
    stored = await redis.hgetall(_CONFIG_KEY)
    merged = {**_DEFAULTS, **stored}
    return {
        "gold_cap": int(merged["gold_cap"]),
        "ah_fee_pct": float(merged["ah_fee_pct"]),
        "listing_duration_hours": int(merged["listing_duration_hours"]),
        "gold_drop_min": int(merged["gold_drop_min"]),
        "gold_drop_max": int(merged["gold_drop_max"]),
    }


async def set_config(updates: dict) -> None:
    """Persist updated economy config fields to Redis."""
    redis = get_redis()
    serialized = {k: str(v) for k, v in updates.items()}
    await redis.hset(_CONFIG_KEY, mapping=serialized)
