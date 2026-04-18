"""Async Redis client for token blacklisting and rate limiting."""
import os

from redis.asyncio import Redis

_redis_client: Redis | None = None

REDIS_URL: str = os.environ["REDIS_URL"]

# TTL constants (seconds)
REFRESH_TOKEN_TTL = 7 * 24 * 60 * 60   # 7 days
ACCESS_TOKEN_TTL = 15 * 60              # 15 minutes (max blacklist window)
RATE_LIMIT_WINDOW = 60                  # 1-minute sliding window


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


# ── Token store helpers ───────────────────────────────────────────────────────

async def store_refresh_token(jti: str, user_id: str) -> None:
    """Persist a refresh token JTI so it can be invalidated on logout."""
    redis = get_redis()
    await redis.setex(f"refresh:{jti}", REFRESH_TOKEN_TTL, user_id)


async def revoke_refresh_token(jti: str) -> None:
    """Remove a refresh token JTI (logout / rotation)."""
    redis = get_redis()
    await redis.delete(f"refresh:{jti}")


async def is_refresh_token_valid(jti: str) -> bool:
    """Return True if the refresh token JTI is still stored (not revoked)."""
    redis = get_redis()
    return await redis.exists(f"refresh:{jti}") == 1


async def blacklist_access_token(jti: str, ttl: int) -> None:
    """Blacklist an access token JTI until it would naturally expire."""
    if ttl > 0:
        redis = get_redis()
        await redis.setex(f"blacklist:{jti}", ttl, "1")


async def is_access_token_blacklisted(jti: str) -> bool:
    redis = get_redis()
    return await redis.exists(f"blacklist:{jti}") == 1


# ── Rate limiting ─────────────────────────────────────────────────────────────

async def check_rate_limit(key: str, max_requests: int) -> bool:
    """Sliding-window rate limiter using Redis INCR + EXPIRE.

    Returns True if the request is allowed, False if the limit is exceeded.
    Key should encode endpoint + client IP (e.g. "rl:login:192.168.1.1").
    """
    redis = get_redis()
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, RATE_LIMIT_WINDOW)
    return current <= max_requests
