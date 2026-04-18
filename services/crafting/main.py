"""AETHERMOOR Crafting Service — recipes, materials, and item crafting."""
import logging
import sys
from contextlib import asynccontextmanager
from pythonjsonlogger import jsonlogger

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response as StarletteResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

from database import AsyncSessionLocal, Base, engine
from routers import crafting
from seed import seed_recipes

# Configure JSON logging for Promtail
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={'asctime': 'time', 'levelname': 'level', 'name': 'logger'},
    static_fields={'service': 'crafting', 'environment': 'docker'}
)

for logger_name in ['', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

logger = logging.getLogger('crafting')


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Crafting service starting up")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed_recipes(db)
    logger.info("Crafting service ready")
    yield
    logger.info("Crafting service shutting down")
    await engine.dispose()
    logger.info("Crafting service stopped")


app = FastAPI(
    title="aethermoor-crafting",
    version="1.0.0",
    description="Recipe management and item crafting for Project AETHERMOOR.",
    docs_url="/crafting/docs",
    redoc_url="/crafting/redoc",
    openapi_url="/crafting/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(crafting.router)

REQUEST_LATENCY = Histogram('crafting_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
REQUEST_COUNT = Counter('crafting_request_count', 'Total request count', ['method', 'endpoint', 'http_status'])
ERROR_COUNT = Counter('crafting_error_count', 'Total error count', ['method', 'endpoint', 'http_status'])
ACTIVE_REQUESTS = Gauge('crafting_active_requests', 'Active requests in progress')


@app.get("/health", tags=["ops"])
async def health() -> dict:
    return {"status": "ok", "service": "crafting"}


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
