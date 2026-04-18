"""AETHERMOOR Inventory Service — item storage, equipment, and loot."""
import logging
import os
import sys
from contextlib import asynccontextmanager

from pythonjsonlogger import jsonlogger

from fastapi import FastAPI, Request
from starlette.responses import Response as StarletteResponse
from prometheus_client import Counter, Gauge, Histogram, CONTENT_TYPE_LATEST, generate_latest

formatter = jsonlogger.JsonFormatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s",
    rename_fields={"asctime": "time", "levelname": "level", "name": "logger"},
    static_fields={"service": "inventory", "environment": "docker"},
)

for logger_name in ["", "uvicorn", "uvicorn.access", "uvicorn.error"]:
    _l = logging.getLogger(logger_name)
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(formatter)
    _l.handlers = [_h]
    _l.setLevel(logging.INFO)
    _l.propagate = False

logger = logging.getLogger("inventory")

REQUEST_LATENCY = Histogram(
    "inventory_request_latency_seconds", "Request latency", ["method", "endpoint"]
)
REQUEST_COUNT = Counter(
    "inventory_request_count", "Total request count", ["method", "endpoint", "http_status"]
)
ERROR_COUNT = Counter(
    "inventory_error_count", "Total error count", ["method", "endpoint", "http_status"]
)
ACTIVE_REQUESTS = Gauge("inventory_active_requests", "Active requests in progress")


async def _seed_items(db_session) -> None:
    """Insert starter items into item_catalogue if they don't already exist."""
    from sqlalchemy import select
    from models import Item
    from seed import SEED_ITEMS

    for data in SEED_ITEMS:
        existing = await db_session.get(Item, data["id"])
        if existing is None:
            db_session.add(Item(**data))
    await db_session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import Base, engine, AsyncSessionLocal

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await _seed_items(session)

    logger.info("Inventory service started — DB tables verified, items seeded")
    yield
    from database import engine as _engine
    await _engine.dispose()
    logger.info("Inventory service stopped")


app = FastAPI(
    title="aethermoor-inventory",
    version="0.2.0",
    description="Item storage, equipment, and loot for AETHERMOOR",
    lifespan=lifespan,
)

from routers.inventory import router as inventory_router  # noqa: E402

app.include_router(inventory_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "inventory"}


@app.get("/metrics")
def metrics() -> StarletteResponse:
    return StarletteResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


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
