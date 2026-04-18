"""AETHERMOOR Quest Service — Quest state, progress, and rewards."""
import logging
import sys
from contextlib import asynccontextmanager
from pythonjsonlogger import jsonlogger

from fastapi import FastAPI, Request
from starlette.responses import Response as StarletteResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={'asctime': 'time', 'levelname': 'level', 'name': 'logger'},
    static_fields={'service': 'quest', 'environment': 'docker'}
)

for logger_name in ['', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
    _l = logging.getLogger(logger_name)
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(formatter)
    _l.handlers = [_h]
    _l.setLevel(logging.INFO)
    _l.propagate = False

logger = logging.getLogger('quest')

REQUEST_LATENCY = Histogram('quest_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
REQUEST_COUNT = Counter('quest_request_count', 'Total request count', ['method', 'endpoint', 'http_status'])
ERROR_COUNT = Counter('quest_error_count', 'Total error count', ['method', 'endpoint', 'http_status'])
ACTIVE_REQUESTS = Gauge('quest_active_requests', 'Active requests in progress')


@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import Base, engine, AsyncSessionLocal
    from seed import seed_quests

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        added = await seed_quests(session)
        if added:
            logger.info("Seeded %d new quests", added)

    logger.info("Quest service started")
    yield
    from database import engine as _engine
    await _engine.dispose()
    logger.info("Quest service stopped")


app = FastAPI(
    title="aethermoor-quest",
    version="1.0.0",
    description="Quest state, progress tracking, and reward distribution for AETHERMOOR.",
    docs_url="/quest/docs",
    redoc_url="/quest/redoc",
    openapi_url="/quest/openapi.json",
    lifespan=lifespan,
)

from routers.quests import router as quests_router  # noqa: E402
from routers.npc import router as npc_router  # noqa: E402

app.include_router(quests_router)
app.include_router(npc_router)


@app.get("/health", tags=["ops"])
async def health() -> dict:
    return {"status": "ok", "service": "quest"}


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
