"""AETHERMOOR Player/Character Service — Character data, stats & world position."""
import logging
import sys
from contextlib import asynccontextmanager
from pythonjsonlogger import jsonlogger

from fastapi import FastAPI, Request
from starlette.responses import Response as StarletteResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

from database import Base, engine
from routers import internal, players

# Configure JSON logging for Promtail
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={'asctime': 'time', 'levelname': 'level', 'name': 'logger'},
    static_fields={'service': 'character', 'environment': 'docker'}
)

# Configure root logger and all uvicorn loggers
for logger_name in ['', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

logger = logging.getLogger('character')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Character service starting up")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Character service ready")
    yield
    logger.info("Character service shutting down")
    await engine.dispose()
    logger.info("Character service stopped")

app = FastAPI(
    title="aethermoor-player",
    version="1.0.0",
    description="Player character data, stats, world position, and inventory for Project AETHERMOOR.",
    docs_url="/players/docs",
    redoc_url="/players/redoc",
    openapi_url="/players/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)

app.include_router(players.router)
app.include_router(internal.router)

REQUEST_LATENCY = Histogram('character_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
REQUEST_COUNT = Counter('character_request_count', 'Total request count', ['method', 'endpoint', 'http_status'])
ERROR_COUNT = Counter('character_error_count', 'Total error count', ['method', 'endpoint', 'http_status'])
ACTIVE_REQUESTS = Gauge('character_active_requests', 'Active requests in progress')

@app.get("/health", tags=["ops"])
async def health() -> dict:
    return {"status": "ok", "service": "player"}


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
