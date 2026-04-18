"""Async Redis client for world service real-time state.

Redis DB 1 is allocated to the world service (see docker-compose.yml).

Key schema:
  world:zone:{zone_id}:count            — STRING integer  (current player count)
  world:zone:{zone_id}:positions        — HASH { char_id: "x,y" }
  world:zone:{zone_id}:npc:{npc_id}     — HASH { state, x, y, target_x, target_y, respawn_at }
  world:fishing:{zone_id}:{dock_id}     — STRING integer  (fishers at dock, soft cap 8)
  world:config:{key}                    — STRING          (live-reconfigurable values)
  world:event:{event_id}:active         — STRING "1"      (TTL-based active event flag)
"""
import os

from redis.asyncio import Redis

REDIS_URL: str = os.environ["REDIS_URL"]

_redis_client: Redis | None = None

# NPC state values
NPC_STATE_ALIVE = "alive"
NPC_STATE_DEAD = "dead"
NPC_STATE_RESPAWNING = "respawning"

FISHING_DOCK_SOFT_CAP = 8

# Lua script: atomic check-and-increment for fishing dock soft cap.
# Returns 1 if the fisher was added (count < cap), 0 if the dock is full.
_FISHING_ENTER_LUA = """
local key = KEYS[1]
local cap = tonumber(ARGV[1])
local current = tonumber(redis.call('GET', key) or 0)
if current < cap then
    redis.call('INCR', key)
    return 1
else
    return 0
end
"""


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


# ── Zone player count ────────────────────────────────────────────────────────

async def increment_zone_count(zone_id: str) -> int:
    """Atomically add one player to the zone. Returns new count."""
    redis = get_redis()
    return int(await redis.incr(f"world:zone:{zone_id}:count"))


async def decrement_zone_count(zone_id: str) -> int:
    """Atomically remove one player from the zone. Returns new count (min 0)."""
    redis = get_redis()
    key = f"world:zone:{zone_id}:count"
    count = int(await redis.decr(key))
    if count < 0:
        await redis.set(key, 0)
        return 0
    return count


async def get_zone_count(zone_id: str) -> int:
    redis = get_redis()
    val = await redis.get(f"world:zone:{zone_id}:count")
    return int(val) if val else 0


# ── Player positions ─────────────────────────────────────────────────────────

async def set_player_position(zone_id: str, character_id: str, x: int, y: int) -> None:
    """Store (or update) a player's position in the zone hash."""
    redis = get_redis()
    await redis.hset(f"world:zone:{zone_id}:positions", character_id, f"{x},{y}")


async def remove_player_position(zone_id: str, character_id: str) -> None:
    """Remove a player's position entry when they exit the zone."""
    redis = get_redis()
    await redis.hdel(f"world:zone:{zone_id}:positions", character_id)


async def get_all_player_positions(zone_id: str) -> dict[str, tuple[int, int]]:
    """Return {character_id: (x, y)} for all players currently in the zone."""
    redis = get_redis()
    raw: dict[str, str] = await redis.hgetall(f"world:zone:{zone_id}:positions")
    result: dict[str, tuple[int, int]] = {}
    for char_id, coords in raw.items():
        try:
            x_str, y_str = coords.split(",", 1)
            result[char_id] = (int(x_str), int(y_str))
        except ValueError:
            continue
    return result


async def get_nearby_players(
    zone_id: str, x: int, y: int, radius: int = 15
) -> list[dict]:
    """Return players within `radius` tiles of (x, y) in the zone.

    Uses Chebyshev distance (max of |dx|, |dy|) to match tile-grid "nearby" semantics.
    O(n) scan — acceptable given zone max_player caps (typically 100–500 on a Pi).
    """
    all_positions = await get_all_player_positions(zone_id)
    nearby = []
    for char_id, (px, py) in all_positions.items():
        if max(abs(px - x), abs(py - y)) <= radius:
            nearby.append({"character_id": char_id, "x": px, "y": py})
    return nearby


# ── NPC state ────────────────────────────────────────────────────────────────

async def set_npc_state(
    zone_id: str,
    npc_id: str,
    state: str,
    x: int,
    y: int,
    target_x: int | None = None,
    target_y: int | None = None,
    respawn_at: int | None = None,
) -> None:
    """Write NPC state to Redis hash."""
    redis = get_redis()
    key = f"world:zone:{zone_id}:npc:{npc_id}"
    data: dict[str, str] = {
        "state": state,
        "x": str(x),
        "y": str(y),
        "target_x": str(target_x if target_x is not None else x),
        "target_y": str(target_y if target_y is not None else y),
        "respawn_at": str(respawn_at if respawn_at is not None else 0),
    }
    await redis.hset(key, mapping=data)


async def get_npc_state(zone_id: str, npc_id: str) -> dict | None:
    """Return NPC state dict or None if not found."""
    redis = get_redis()
    raw = await redis.hgetall(f"world:zone:{zone_id}:npc:{npc_id}")
    if not raw:
        return None
    return {
        "state": raw.get("state", NPC_STATE_ALIVE),
        "x": int(raw.get("x", 0)),
        "y": int(raw.get("y", 0)),
        "target_x": int(raw.get("target_x", 0)),
        "target_y": int(raw.get("target_y", 0)),
        "respawn_at": int(raw.get("respawn_at", 0)),
    }


async def get_zone_npc_ids(zone_id: str, npc_template_ids: list[str]) -> list[dict]:
    """Return state for all NPCs in a zone (batch fetch)."""
    if not npc_template_ids:
        return []
    redis = get_redis()
    states = []
    for npc_id in npc_template_ids:
        raw = await redis.hgetall(f"world:zone:{zone_id}:npc:{npc_id}")
        if raw:
            states.append({
                "npc_id": npc_id,
                "state": raw.get("state", NPC_STATE_ALIVE),
                "x": int(raw.get("x", 0)),
                "y": int(raw.get("y", 0)),
            })
    return states


# ── Fishing dock soft cap ────────────────────────────────────────────────────

async def fishing_dock_enter(zone_id: str, dock_id: str) -> bool:
    """Attempt to add a fisher to a dock. Returns True if successful (slot available).

    Uses a Lua script for atomic check-and-increment, preventing race conditions
    where multiple players simultaneously see a count < cap and all get admitted.
    """
    redis = get_redis()
    key = f"world:fishing:{zone_id}:{dock_id}"
    result = await redis.eval(_FISHING_ENTER_LUA, 1, key, str(FISHING_DOCK_SOFT_CAP))
    return bool(result)


async def fishing_dock_exit(zone_id: str, dock_id: str) -> None:
    """Remove a fisher from the dock counter."""
    redis = get_redis()
    key = f"world:fishing:{zone_id}:{dock_id}"
    count = int(await redis.get(key) or 0)
    if count > 0:
        await redis.decr(key)


async def get_fishing_dock_count(zone_id: str, dock_id: str) -> int:
    redis = get_redis()
    val = await redis.get(f"world:fishing:{zone_id}:{dock_id}")
    return int(val) if val else 0


# ── Live-configurable world settings ────────────────────────────────────────

_CONFIG_DEFAULTS: dict[str, str] = {
    "npc_respawn_default_sec": "30",
    "zone_broadcast_interval_sec": "5",
    "nearby_radius_tiles": "15",
}


async def get_config(key: str) -> str:
    """Read a live-configurable setting from Redis, falling back to code default."""
    redis = get_redis()
    val = await redis.get(f"world:config:{key}")
    if val is not None:
        return val
    return _CONFIG_DEFAULTS.get(key, "")


async def set_config(key: str, value: str) -> None:
    """Persist a live-configurable setting to Redis (no service restart required)."""
    redis = get_redis()
    await redis.set(f"world:config:{key}", value)
