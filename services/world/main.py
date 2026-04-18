"""AETHERMOOR World Service — Zone data, tile maps & player presence."""
import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pythonjsonlogger import jsonlogger

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response as StarletteResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import Counter, Histogram, Gauge

# Configure JSON logging for Promtail
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={'asctime': 'time', 'levelname': 'level', 'name': 'logger'},
    static_fields={'service': 'world', 'environment': 'docker'}
)

# Configure root logger and all uvicorn loggers
for logger_name in ['', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

logger = logging.getLogger('world')

REQUEST_LATENCY = Histogram('world_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
REQUEST_COUNT = Counter('world_request_count', 'Total request count', ['method', 'endpoint', 'http_status'])
ERROR_COUNT = Counter('world_error_count', 'Total error count', ['method', 'endpoint', 'http_status'])
ACTIVE_REQUESTS = Gauge('world_active_requests', 'Active requests in progress')

import cache as redis_cache
from database import AsyncSessionLocal, Base, engine
from routers import events, internal, npcs, presence, zones
from seed import seed_zones
from zero_trust import make_service_token

# ── Background NPC tick task ─────────────────────────────────────────────────

_npc_tick_task: asyncio.Task | None = None


async def _npc_tick_loop() -> None:
    """Background task: tick all active zones once per second for NPC movement.

    Runs as a long-lived asyncio task. Each iteration loads active zones and
    fires the internal tick endpoint logic directly (no HTTP round-trip needed).

    Keeps per-tick cost low:
    - Sequential zone processing (not parallel) to avoid Redis contention
    - A* capped at 512 nodes per NPC per tick (see pathfinding.py)
    - Skips zones with no active players (count == 0) to save CPU on idle zones
    """
    import httpx
    from database import AsyncSessionLocal
    from sqlalchemy import select
    from models import Zone, NpcTemplate
    import time
    from pathfinding import CollisionGrid

    while True:
        try:
            await asyncio.sleep(1)

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Zone).where(Zone.is_active.is_(True))
                )
                zones_list = result.scalars().all()

            for zone in zones_list:
                # Skip zones with no players to save CPU
                player_count = await redis_cache.get_zone_count(zone.id)
                if player_count == 0:
                    continue

                # Build grid for this zone
                grid = CollisionGrid.from_tilemap(zone.tilemap, zone.width, zone.height)
                now = int(time.time())

                async with AsyncSessionLocal() as db:
                    npc_result = await db.execute(
                        select(NpcTemplate).where(
                            NpcTemplate.zone_id == zone.id,
                            NpcTemplate.is_active.is_(True),
                        )
                    )
                    templates = npc_result.scalars().all()

                for tmpl in templates:
                    state = await redis_cache.get_npc_state(zone.id, tmpl.id)

                    if state is None:
                        await redis_cache.set_npc_state(
                            zone_id=zone.id,
                            npc_id=tmpl.id,
                            state=redis_cache.NPC_STATE_ALIVE,
                            x=tmpl.spawn_x,
                            y=tmpl.spawn_y,
                        )
                        continue

                    if state["state"] == redis_cache.NPC_STATE_RESPAWNING:
                        if now >= state["respawn_at"]:
                            await redis_cache.set_npc_state(
                                zone_id=zone.id,
                                npc_id=tmpl.id,
                                state=redis_cache.NPC_STATE_ALIVE,
                                x=tmpl.spawn_x,
                                y=tmpl.spawn_y,
                            )
                        continue

                    if state["state"] != redis_cache.NPC_STATE_ALIVE or not tmpl.patrol_path:
                        continue

                    cx, cy = state["x"], state["y"]
                    tx, ty = state["target_x"], state["target_y"]

                    if cx == tx and cy == ty:
                        current_wp_idx = 0
                        for i, wp in enumerate(tmpl.patrol_path):
                            if wp["x"] == tx and wp["y"] == ty:
                                current_wp_idx = i
                                break
                        next_wp = tmpl.patrol_path[
                            (current_wp_idx + 1) % len(tmpl.patrol_path)
                        ]
                        tx, ty = next_wp["x"], next_wp["y"]

                    next_step = grid.next_step(cx, cy, tx, ty)
                    if next_step:
                        nx, ny = next_step
                        await redis_cache.set_npc_state(
                            zone_id=zone.id,
                            npc_id=tmpl.id,
                            state=redis_cache.NPC_STATE_ALIVE,
                            x=nx,
                            y=ny,
                            target_x=tx,
                            target_y=ty,
                        )

        except asyncio.CancelledError:
            break
        except Exception as exc:  # noqa: BLE001
            logger.exception("NPC tick error: %s", exc)
            await asyncio.sleep(5)  # Back off on unexpected error


# ── Lifespan event handler ──────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _npc_tick_task
    logger.info("World service starting up")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed initial zones
    async with AsyncSessionLocal() as db:
        added = await seed_zones(db)
        if added:
            logger.info("Seeded %d new zones", added)

    # Start background NPC tick
    _npc_tick_task = asyncio.create_task(_npc_tick_loop())
    logger.info("NPC tick background task started")
    logger.info("World service ready")
    
    yield
    
    logger.info("World service shutting down")
    if _npc_tick_task is not None:
        _npc_tick_task.cancel()
        try:
            await _npc_tick_task
        except asyncio.CancelledError:
            pass

    await redis_cache.close_redis()
    await engine.dispose()
    logger.info("World service stopped")


app = FastAPI(
    title="aethermoor-world",
    version="1.0.0",
    description="Game world service: zones, tile maps, player presence, NPCs, and world events.",
    docs_url="/world/docs",
    redoc_url="/world/redoc",
    openapi_url="/world/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    # Allow browser connections for WebSocket presence endpoint.
    # In production, Nginx handles TLS and same-origin; these origins cover
    # local dev (Vite) and the Docker frontend container.
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["*"],
)

app.include_router(zones.router)
app.include_router(events.router)
app.include_router(internal.router)
app.include_router(presence.router)
app.include_router(npcs.router)


@app.get("/health", tags=["ops"])
async def health() -> dict:
    return {"status": "ok", "service": "world"}


@app.get("/metrics")
def metrics():
    return StarletteResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.middleware('http')
async def prometheus_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    ACTIVE_REQUESTS.inc()
    with REQUEST_LATENCY.labels(method, endpoint).time():
        try:
            response = await call_next(request)
            REQUEST_COUNT.labels(method, endpoint, response.status_code).inc()
            if response.status_code >= 500:
                ERROR_COUNT.labels(method, endpoint, response.status_code).inc()
            return response
        finally:
            ACTIVE_REQUESTS.dec()
