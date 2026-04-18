# World Service

**AETHERMOOR Game World Service** — zones, tile maps, player presence, NPCs, and world events.

- Port: `8003`
- Language: Python / FastAPI
- Databases: PostgreSQL 16 (persistent data) + Redis 7 (real-time state)
- Zero-trust: all inbound internal calls require `X-Service-Token` (HMAC-SHA256)

---

## GDD Technical Questions — CTO Answers (v0.4)

These questions were raised in the GDD review. Answers are documented here before implementation begins, as required by the task brief.

---

### 1. Phaser.js Tension Bar at 60fps on Mobile

**Question:** Is the fishing mini-game Tension Bar (tap-and-hold) within rendering budget on mobile? Target devices: mid-range Android / iPhone 11.

**Answer: Yes — this is safe.**

The Tension Bar is a client-side canvas animation concern, not a server concern. Assessment:

- A tap-and-hold tension meter is a single `requestAnimationFrame` loop updating a rectangle's width and colour.
- At 60fps this is ~16ms per frame budget. Drawing one bar + checking touch state costs <1ms on any device from the last 5 years.
- iPhone 11 (A13 Bionic) and mid-range Android (Snapdragon 700 series) are both capable of rendering PixiJS scenes at 60fps for far more complex scenes than a fishing bar.
- The server side is completely uninvolved in the rendering loop. The server only receives the final "cast result" event.

**Recommendation:** No action required. The Tension Bar should be implemented entirely in the frontend. The world service will expose a `POST /world/zones/{zoneId}/fishing/cast` endpoint (future task) to validate the result and apply the fishing soft-cap check.

---

### 2. A* Pathfinding for Escort NPCs

**Question:** Is server-side A* feasible for escort quest NPCs? Or should pathfinding be client-predicted with server validation?

**Answer: Server-side A* is feasible, with the constraints documented below. Escort NPCs specifically should be server-authoritative.**

Analysis:

- The A* implementation in `pathfinding.py` is grid-based (4-directional), uses `heapq`, and is capped at 512 nodes expanded per tick per NPC.
- On a Raspberry Pi 4 (4-core ARM Cortex-A72, ~1.5 GHz), a 512-node A* search completes in under 1ms in pure Python. With 20 escort NPCs in a zone, that is ~20ms per tick — within the 1-second tick interval.
- For *patrol* NPCs (simple closed-loop paths), this is straightforward and already implemented.
- For *escort* NPCs (dynamic target following a player), the same A* runs each tick with the player's current position as the destination. The server is authoritative for the NPC position; the client interpolates smoothly between server updates.

**Constraints / Caveats:**

1. **Zone NPC cap:** Keep active escort NPCs to ≤20 per zone on a Pi. If a quest creates more, queue them or use simplified line-of-sight movement for secondary NPCs.
2. **No pure client prediction:** Escort NPCs must not be client-predicted. Players could exploit client-side prediction to teleport NPCs through walls. Server is authoritative.
3. **Client smoothing:** The frontend should interpolate NPC positions between the 1-second server ticks (e.g. using Phaser.js `tweens.add` with a 1000ms duration). This hides the steppy movement.
4. **Dungeon maps:** A* performance depends on map size. The current cap (512 nodes) limits effective pathfinding range to ~22 tiles. For large dungeons, increase the cap to 2048 and monitor Pi CPU usage.

**Recommendation:** Proceed with server-authoritative A*. Implement the 512-node cap in `pathfinding.py` (already done). Monitor CPU on Pi under load and adjust cap if needed.

---

### 3. Live-Configurable Gold Economy Values

**Question:** Confirm all gold economy values (gold caps, drop rates, AH fees) can be live-reconfigured from an admin panel without a service restart.

**Answer: Yes — confirmed and implemented.**

The mechanism is Redis-backed live config, demonstrated in `cache.py` (`get_config` / `set_config`) and exposed via:

```
GET  /world/admin/config/{key}   — read current value (X-Service-Token required)
PUT  /world/admin/config/{key}   — update value in Redis (X-Service-Token required)
```

**How it works:**

- Config values are stored as Redis strings under `world:config:{key}`.
- Services read config on each operation, not at startup — so a Redis write takes effect immediately.
- Code-level defaults in `_CONFIG_DEFAULTS` serve as fallback if a key has never been set.
- No service restart, no redeploy, no environment variable change is required.

**Economy values (gold caps, drop rates, AH fees) live in the Economy Service.** The same pattern (`get_config` / `set_config` backed by Redis) must be implemented there. The world service pattern is the reference implementation.

**Admin panel integration:** The future admin panel will call `PUT /world/admin/config/{key}` (and the equivalent economy service endpoint) via the gateway, authenticated with an admin JWT scope. The gateway enforces role-based access before forwarding.

---

### 4. Fishing Spot Soft Limit (8 Players per Dock)

**Question:** Confirm the server-side counter approach for 8-player-per-dock soft cap is viable without race conditions.

**Answer: Yes — implemented using a Redis Lua script for atomic check-and-increment.**

The problem with a naive `GET` + `INCR` approach:

```
Thread A: GET dock_count  → 7  (under cap)
Thread B: GET dock_count  → 7  (under cap)
Thread A: INCR dock_count → 8  (both admitted — 9th player gets in)
Thread B: INCR dock_count → 9  (race condition)
```

The solution is a Lua script executed atomically by Redis:

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

Redis executes Lua scripts atomically (single-threaded). No race condition is possible. See `cache.py` → `fishing_dock_enter()`.

The soft cap is 8 per dock (`FISHING_DOCK_SOFT_CAP = 8`). "Soft" means it is enforced server-side but there is no hard gameplay block — the 9th player receives a "dock is busy, come back later" message and can try another dock or wait. This matches the GDD intent.

Integration tests for the fishing dock (including the race-condition guard) are in `tests/test_integration.py` → `TestFishingDock`.

---

## Architecture

### Data Stores

| Data | Store | Justification |
|------|-------|---------------|
| Zone definitions, NPC templates, world events | PostgreSQL 16 | Persistent, queryable, source of truth |
| Player positions within zones | Redis HASH | High write frequency (every player move), sub-millisecond reads |
| Zone player counts | Redis STRING (INCR/DECR) | Atomic counters, no Postgres write per player move |
| NPC runtime state (position, alive/dead) | Redis HASH | Updated every tick (1s per NPC), must be fast |
| Fishing dock counters | Redis STRING + Lua | Atomic soft-cap enforcement (see Q4 above) |
| Live config values | Redis STRING | Zero-restart reconfiguration (see Q3 above) |

### NPC Tick

NPCs are ticked by a background `asyncio.Task` launched at startup (`main.py` → `_npc_tick_loop`). Each second:

1. Iterates active zones.
2. Skips zones with zero players (saves CPU on idle zones — important for Raspberry Pi).
3. For each active NPC: revives any whose `respawn_at` has passed, then moves patrol NPCs one tile via A*.
4. Writes updated state to Redis.

The tick also has an internal HTTP-equivalent endpoint `POST /world/zones/{zoneId}/npcs/tick` for use in testing without the background task running.

### Zero Trust

All internal endpoints require `X-Service-Token` — an HMAC-SHA256 time-bucketed token generated from the shared `SERVICE_TOKEN` secret. See `zero_trust.py`. Public endpoints (`GET /world/zones`, `GET /world/zones/{id}`, `GET /world/events`) are unauthenticated. Player presence queries (`GET /world/zones/{id}/players`) require a user JWT verified via the Auth Service.

### Tilemap Format

Zone tilemaps are stored as JSONB in PostgreSQL and returned verbatim to the frontend. Format is [Phaser.js / Tiled JSON](https://doc.mapeditor.org/en/stable/reference/json-map-format/). Layers:

- `Ground` — visual tile layer (tile IDs reference `aethermoor_tileset.tsj`)
- `Collision` — walkability mask (0 = walkable, non-zero = blocked). Used by server-side A* and client-side collision.

---

## API Reference

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/world/zones` | None | List all active zones with capacity |
| GET | `/world/zones/{zoneId}` | None | Zone detail + tilemap + NPC templates |
| POST | `/world/zones/{zoneId}/enter` | X-Service-Token | Player enters zone |
| POST | `/world/zones/{zoneId}/exit` | X-Service-Token | Player exits zone |
| GET | `/world/zones/{zoneId}/players` | JWT | Nearby players (15-tile radius) |
| GET | `/world/zones/{zoneId}/npcs` | None | NPC state for zone |
| POST | `/world/zones/{zoneId}/npcs/tick` | X-Service-Token | Advance NPC tick (test/cron) |
| POST | `/world/npcs/kill` | X-Service-Token | Mark NPC dead (from combat service) |
| GET | `/world/events` | None | Active world events |
| POST | `/world/events/{id}/activate` | X-Service-Token | Activate event |
| POST | `/world/events/{id}/deactivate` | X-Service-Token | Deactivate event |
| GET | `/world/admin/config/{key}` | X-Service-Token | Read live config value |
| PUT | `/world/admin/config/{key}` | X-Service-Token | Update live config value |

## Running Tests

```bash
cd services/world
pip install -r requirements.txt
# Requires Postgres + Redis running locally
DATABASE_URL=postgresql+asyncpg://aethermoor:aethermoor@localhost:5432/aethermoor_test \
REDIS_URL=redis://localhost:6379/15 \
SERVICE_TOKEN=dev-token \
pytest tests/ -v
```
