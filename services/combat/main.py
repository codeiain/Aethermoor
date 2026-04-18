"""AETHERMOOR Combat Service — D&D turn-based combat engine."""
import logging
import os
import sys
from contextlib import asynccontextmanager

from pythonjsonlogger import jsonlogger

from fastapi import FastAPI, Request
from starlette.responses import Response as StarletteResponse
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    CONTENT_TYPE_LATEST,
    generate_latest,
)

# Configure JSON logging for Promtail
formatter = jsonlogger.JsonFormatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s",
    rename_fields={"asctime": "time", "levelname": "level", "name": "logger"},
    static_fields={"service": "combat", "environment": "docker"},
)

for logger_name in ["", "uvicorn", "uvicorn.access", "uvicorn.error"]:
    _l = logging.getLogger(logger_name)
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(formatter)
    _l.handlers = [_h]
    _l.setLevel(logging.INFO)
    _l.propagate = False

logger = logging.getLogger("combat")

REQUEST_LATENCY = Histogram(
    "combat_request_latency_seconds", "Request latency", ["method", "endpoint"]
)
REQUEST_COUNT = Counter(
    "combat_request_count", "Total request count", ["method", "endpoint", "http_status"]
)
ERROR_COUNT = Counter(
    "combat_error_count", "Total error count", ["method", "endpoint", "http_status"]
)
ACTIVE_REQUESTS = Gauge("combat_active_requests", "Active requests in progress")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure DB tables exist
    from database import Base, engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Combat service started — DB tables verified")

    yield

    # Shutdown
    from redis_state import close_redis
    await close_redis()
    await engine.dispose()
    logger.info("Combat service stopped")


app = FastAPI(
    title="aethermoor-combat",
    version="0.2.0",
    description="D&D turn-based combat engine for Project AETHERMOOR",
    lifespan=lifespan,
)

# ── Routers ──────────────────────────────────────────────────────────────────

from routers.combat import router as combat_router  # noqa: E402

app.include_router(combat_router)


# ── Operations endpoints ─────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "combat"}


@app.get("/metrics")
def metrics() -> StarletteResponse:
    return StarletteResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ── Prometheus middleware ─────────────────────────────────────────────────────

@app.middleware("http")
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
