"""AETHERMOOR Auth Service — JWT + Zero-Trust Inter-Service Authentication."""
import os
import logging
import sys
from contextlib import asynccontextmanager
from pythonjsonlogger import jsonlogger

from fastapi import FastAPI, Request
from starlette.responses import Response as StarletteResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

from cache import close_redis
from database import Base, engine
from routers import internal, users

# Configure JSON logging for Promtail
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={'asctime': 'time', 'levelname': 'level', 'name': 'logger'},
    static_fields={'service': 'auth', 'environment': 'docker'}
)

# Configure root logger and all uvicorn loggers
for logger_name in ['', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

logger = logging.getLogger('auth')

REQUEST_LATENCY = Histogram('auth_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
REQUEST_COUNT = Counter('auth_request_count', 'Total request count', ['method', 'endpoint', 'http_status'])
ERROR_COUNT = Counter('auth_error_count', 'Total error count', ['method', 'endpoint', 'http_status'])
ACTIVE_REQUESTS = Gauge('auth_active_requests', 'Active requests in progress')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Auth service starting up")
    # Create tables if they don't exist (idempotent for first-run convenience).
    # Production migrations should be handled via Alembic — tracked in backlog.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Auth service ready")
    yield
    logger.info("Auth service shutting down")
    await close_redis()
    await engine.dispose()
    logger.info("Auth service stopped")

app = FastAPI(
    title="aethermoor-auth",
    version="1.0.0",
    description="Authentication and authorisation service for Project AETHERMOOR.",
    docs_url="/auth/docs",
    redoc_url="/auth/redoc",
    openapi_url="/auth/openapi.json",
    lifespan=lifespan,
)

# CORS is handled at the gateway; keep this narrow inside the internal network
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],  # No direct browser access expected on internal network
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(internal.router)

@app.get("/metrics")
def metrics():
    return StarletteResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health", tags=["ops"])
async def health() -> dict:
    return {"status": "ok", "service": "auth"}


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
