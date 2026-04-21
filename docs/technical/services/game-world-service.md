---
tags:
  - world
  - zones
  - npc
---

# Game World Service

**Port:** 8003  
**Language:** Python 3.12 / FastAPI  
**Databases:** PostgreSQL 16 (zones, NPCs, events) + Redis 7 (player positions, NPC state, live config)

Owns all game world data: zone definitions, tilemaps, player presence, NPC lifecycle, and world events.

## Responsibilities

- Zone registry with tilemap JSONB storage
- Player zone entry/exit, nearby-player queries (15-tile Chebyshev radius)
- NPC templates and runtime state (patrol paths, alive/dead, respawn timers)
- Server-side A* pathfinding for NPC patrol (512-node cap for Pi budget)
- World event scheduling and activation
- Live-configurable settings via Redis (no service restart required)
- Fishing dock soft-cap enforcement (8 players per dock, Redis Lua atomic CAS)

## API Endpoints

### Public (unauthenticated)

| Method | Path | Description |
|---|---|---|
| `GET` | `/world/zones` | List all active zones with player counts |
| `GET` | `/world/zones/{zoneId}` | Zone detail + tilemap JSONB + NPC templates |
| `GET` | `/world/zones/{zoneId}/npcs` | Current NPC state for a zone |
| `GET` | `/world/events` | Active world events |

### User (require `Authorization: Bearer <JWT>`)

| Method | Path | Description |
|---|---|---|
| `GET` | `/world/zones/{zoneId}/players` | Nearby players within 15-tile radius |

### Internal (require `X-Service-Token`)

| Method | Path | Description |
|---|---|---|
| `POST` | `/world/zones/{zoneId}/enter` | Record player zone entry, increment Redis counter |
| `POST` | `/world/zones/{zoneId}/exit` | Record player zone exit, decrement Redis counter |
| `POST` | `/world/zones/{zoneId}/npcs/tick` | Advance NPC tick (also called by background task) |
| `POST` | `/world/npcs/kill` | Mark NPC dead (called by combat service) |
| `POST` | `/world/events/{id}/activate` | Activate a world event |
| `POST` | `/world/events/{id}/deactivate` | Deactivate a world event |
| `GET` | `/world/admin/config/{key}` | Read live config value |
| `PUT` | `/world/admin/config/{key}` | Update live config value in Redis |

### Ops

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe |
| `GET` | `/metrics` | Prometheus metrics |

## Data Architecture

| Data | Store | Reason |
|---|---|---|
| Zone definitions, NPC templates, world events | PostgreSQL | Persistent, queryable |
| Player positions within zones | Redis HASH | High write frequency, sub-ms reads |
| Zone player counts | Redis STRING (INCR/DECR) | Atomic counters |
| NPC runtime state | Redis HASH | Updated every tick (~1s), must be fast |
| Fishing dock counters | Redis STRING + Lua | Race-condition-free soft cap |
| Live config | Redis STRING | Zero-restart reconfiguration |

## NPC Tick Loop

A background `asyncio.Task` launched at startup ticks NPCs every second:

1. Iterates active zones.
2. **Skips zones with zero players** — saves CPU on idle zones (critical for Raspberry Pi).
3. For each NPC: revives any whose `respawn_at` has passed, then moves patrol NPCs one step via A*.
4. Writes updated state to Redis.

The tick is capped at 512 A* nodes per NPC per tick. At that cap, a single tick for 20 NPCs costs ~20ms on a Pi 4 — within the 1-second tick budget.

## A* Pathfinding

`pathfinding.py` — `CollisionGrid.from_tilemap()` builds a walkability grid from the tilemap Collision layer. `next_step(from_x, from_y, to_x, to_y)` returns the next tile to move to, using heapq-based A* with a 512-node expansion cap.

**Constraints:**
- Max effective range: ~22 tiles at the 512-node cap (open terrain)
- For large dungeons, increase cap to 2048 and monitor Pi CPU
- Escort NPCs must be server-authoritative — no client prediction (prevents wall-clipping exploits)
- Client should interpolate NPC positions between 1-second server ticks using Phaser.js tweens

## Fishing Dock Soft Cap

8 players per dock. Enforced with an atomic Redis Lua script to prevent the check-then-increment race:

```lua
local key = KEYS[1]
local cap = tonumber(ARGV[1])
local current = tonumber(redis.call('GET', key) or 0)
if current < cap then
    redis.call('INCR', key)
    return 1
else
    return 0
end
```

Redis executes Lua atomically. No race condition possible. See `cache.py` → `fishing_dock_enter()`.

## Live Config

Config values are stored in Redis under `world:config:{key}`. Services read on each operation, not at startup, so a `PUT /world/admin/config/{key}` takes effect immediately — no restart or redeploy needed.

Code-level defaults in `_CONFIG_DEFAULTS` apply if a key has never been set.

## Tilemap Format

Zone tilemaps are stored as JSONB in PostgreSQL and returned verbatim to the frontend. Format follows Phaser.js / Tiled JSON:

- `Ground` layer — visual tile IDs
- `Collision` layer — walkability mask (0 = walkable, non-zero = blocked)

The Collision layer drives both server-side A* and client-side collision detection in the frontend.

## Seeded Zones

| Zone ID | Name | Biome | Size |
|---|---|---|---|
| `starter_town` | Millhaven | town | 40×30 |
| `whispering_forest` | Whispering Forest | forest | 60×60 |
| `sunken_crypt_b1` | Sunken Crypt B1 | dungeon | 30×30 |

## Environment Variables

| Variable | Description |
|---|---|
| `SERVICE_TOKEN` | Shared HMAC secret |
| `DATABASE_URL` | PostgreSQL DSN |
| `REDIS_URL` | Redis DSN |
| `AUTH_SERVICE_URL` | Auth service URL |
| `CHARACTER_SERVICE_URL` | Character service URL |

## Running Tests

```bash
cd services/world
DATABASE_URL=postgresql+asyncpg://aethermoor:aethermoor@localhost:5432/aethermoor_test \
REDIS_URL=redis://localhost:6379/15 \
SERVICE_TOKEN=dev-token \
pytest tests/ -v
```
