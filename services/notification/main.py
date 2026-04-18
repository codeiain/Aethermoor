"""AETHERMOOR Notification Service — stub only, no business logic."""
import os
import logging
import sys
from contextlib import asynccontextmanager
from pythonjsonlogger import jsonlogger

from fastapi import FastAPI, Request
from starlette.responses import Response as StarletteResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

# Configure JSON logging for Promtail
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={'asctime': 'time', 'levelname': 'level', 'name': 'logger'},
    static_fields={'service': 'notification', 'environment': 'docker'}
)

# Configure root logger and all uvicorn loggers
for logger_name in ['', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

logger = logging.getLogger('notification')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Notification service started")
    yield
    logger.info("Notification service stopped")

app = FastAPI(title="aethermoor-notification", version="0.1.0", lifespan=lifespan)

SERVICE_TOKEN = os.environ["SERVICE_TOKEN"]

REQUEST_LATENCY = Histogram('notification_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
REQUEST_COUNT = Counter('notification_request_count', 'Total request count', ['method', 'endpoint', 'http_status'])
ERROR_COUNT = Counter('notification_error_count', 'Total error count', ['method', 'endpoint', 'http_status'])
ACTIVE_REQUESTS = Gauge('notification_active_requests', 'Active requests in progress')

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "notification"}


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
