"""AETHERMOOR Gateway Service — reverse proxy with CORS and rate limiting.

Routes all /api/* client requests to the appropriate internal microservice.
Adds zero-trust X-Service-Token on every upstream request.
Rate limiting uses an in-memory sliding-window counter (no extra deps).
"""
from __future__ import annotations

import asyncio
import os
import time
import logging
import sys
from contextlib import asynccontextmanager
from pythonjsonlogger import jsonlogger

import httpx
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response as StarletteResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

# Configure JSON logging for Promtail
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={'asctime': 'time', 'levelname': 'level', 'name': 'logger'},
    static_fields={'service': 'gateway', 'environment': 'docker'}
)

# Configure root logger and all uvicorn loggers
for logger_name in ['', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

logger = logging.getLogger('gateway')

REQUEST_LATENCY = Histogram('gateway_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
REQUEST_COUNT = Counter('gateway_request_count', 'Total request count', ['method', 'endpoint', 'http_status'])
ERROR_COUNT = Counter('gateway_error_count', 'Total error count', ['method', 'endpoint', 'http_status'])
ACTIVE_REQUESTS = Gauge('gateway_active_requests', 'Active requests in progress')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup/shutdown."""
    global _http_client
    logger.info("Gateway service starting up")
    _http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("Gateway service ready")
    yield
    logger.info("Gateway service shutting down")
    if _http_client:
        await _http_client.aclose()
    logger.info("Gateway service stopped")

app = FastAPI(title="aethermoor-gateway", version="1.0.0", lifespan=lifespan)

# ── CORS ─────────────────────────────────────────────────────────────────────
# In production the nginx frontend proxy handles same-origin; CORS headers
# are only needed for local dev (vite dev server).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import hashlib
import hmac as _hmac

_SERVICE_TOKEN_SECRET: str = os.environ["SERVICE_TOKEN"]


def _make_service_token() -> str:
    """Generate a time-bound HMAC-SHA256 service token (same as zero_trust.py)."""
    ts = int(time.time()) // 60
    digest = _hmac.new(
        _SERVICE_TOKEN_SECRET.encode("utf-8"),
        str(ts).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{ts}:{digest}"

# ── Upstream service map ─────────────────────────────────────────────────────
# Maps URL prefix → (upstream base URL, path prefix to prepend when forwarding)
_UPSTREAMS: dict[str, tuple[str, str]] = {
    "auth": (os.environ.get("AUTH_SERVICE_URL", "http://auth:8001"), "/auth"),
    "players": (os.environ.get("CHARACTER_SERVICE_URL", "http://character:8002"), "/players"),
    "world": (os.environ.get("WORLD_SERVICE_URL", "http://world:8003"), "/world"),
    "combat": (os.environ.get("COMBAT_SERVICE_URL", "http://combat:8004"), "/combat"),
    "crafting": (os.environ.get("CRAFTING_SERVICE_URL", "http://crafting:8013"), "/crafting"),
    "inventory": (os.environ.get("INVENTORY_SERVICE_URL", "http://inventory:8006"), "/inventory"),
}

# ── Rate limiting — in-memory sliding window ─────────────────────────────────
_WINDOW_SECONDS = 60
_DEFAULT_LIMIT = 300            # requests per window per IP (default routes)
_ENDPOINT_LIMITS: dict[str, int] = {
    "/auth/login": 20,
    "/auth/register": 10,
}
# key = "ip:path" → (window_start: float, count: int)
_counters: dict[str, tuple[float, int]] = {}
_counters_lock = asyncio.Lock()


async def _check_rate_limit(ip: str, path: str) -> bool:
    """Return True if within limit, False if exceeded."""
    limit = _ENDPOINT_LIMITS.get(path, _DEFAULT_LIMIT)
    key = f"{ip}:{path}"
    now = time.monotonic()
    async with _counters_lock:
        entry = _counters.get(key)
        if entry is None:
            _counters[key] = (now, 1)
            return True
        window_start, count = entry
        if now - window_start >= _WINDOW_SECONDS:
            _counters[key] = (now, 1)
            return True
        if count >= limit:
            return False
        _counters[key] = (window_start, count + 1)
    return True


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ── Shared HTTP client ────────────────────────────────────────────────────────
_http_client: httpx.AsyncClient | None = None

_HOP_BY_HOP = frozenset({
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
})

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "gateway"}


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


# ── Proxy helper ──────────────────────────────────────────────────────────────
async def _proxy(request: Request, upstream_url: str) -> Response:
    """Forward request to upstream_url and stream response back to client."""
    if _http_client is None:
        raise HTTPException(status_code=503, detail="Gateway not ready")

    ip = _client_ip(request)
    if not await _check_rate_limit(ip, request.url.path):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests — please try again later.",
        )

    # Append query string if present
    target = upstream_url
    if request.url.query:
        target = f"{target}?{request.url.query}"

    # Forward headers: strip hop-by-hop and host; inject zero-trust token
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP and k.lower() != "host"
    }
    headers["x-service-token"] = _make_service_token()
    headers["x-forwarded-for"] = ip

    body = await request.body()

    upstream_resp = await _http_client.request(
        method=request.method,
        url=target,
        headers=headers,
        content=body,
    )

    # Strip hop-by-hop from upstream response
    resp_headers = {
        k: v
        for k, v in upstream_resp.headers.items()
        if k.lower() not in _HOP_BY_HOP
    }

    return Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        headers=resp_headers,
        media_type=upstream_resp.headers.get("content-type"),
    )


# ── Routes ────────────────────────────────────────────────────────────────────
# Nginx frontend proxy strips /api/ prefix before reaching the gateway, so
# the gateway receives bare paths: /auth/*, /players/*, /world/*
# Vite dev proxy must also rewrite /api → "" (see vite.config.ts).

_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]


@app.get("/services/status")
async def services_status() -> dict:
    """Return health status for all backend services. Used by the admin dashboard."""
    if _http_client is None:
        raise HTTPException(status_code=503, detail="Gateway not ready")

    services = [
        ("gateway", "http://localhost:8000", "/health"),
        ("auth", _UPSTREAMS["auth"][0], "/health"),
        ("character", _UPSTREAMS["players"][0], "/health"),
        ("world", _UPSTREAMS["world"][0], "/health"),
    ]

    results = []
    for name, base, path in services:
        try:
            resp = await _http_client.get(f"{base}{path}", timeout=3.0)
            results.append({
                "service": name,
                "status": "ok" if resp.status_code == 200 else "degraded",
                "http_status": resp.status_code,
                "url": f"{base}{path}",
            })
        except Exception as exc:
            results.append({
                "service": name,
                "status": "unreachable",
                "http_status": 0,
                "url": f"{base}{path}",
                "error": str(exc),
            })

    overall = "ok" if all(s["status"] == "ok" for s in results) else "degraded"
    return {"overall": overall, "services": results}


@app.get("/openapi-master.json", include_in_schema=False)
async def master_openapi() -> dict:
    """Aggregate OpenAPI specs from all services into a single combined schema.

    Used by the master Swagger UI at GET /docs-master.
    Only available when running — services must be reachable.
    """
    if _http_client is None:
        raise HTTPException(status_code=503, detail="Gateway not ready")

    service_specs = [
        ("auth", _UPSTREAMS["auth"][0], "/auth/openapi.json"),
        ("character", _UPSTREAMS["players"][0], "/players/openapi.json"),
        ("world", _UPSTREAMS["world"][0], "/world/openapi.json"),
    ]

    combined: dict = {
        "openapi": "3.1.0",
        "info": {"title": "AETHERMOOR — Master API", "version": "1.0.0"},
        "paths": {},
        "components": {"schemas": {}, "securitySchemes": {}},
    }

    for svc_name, base, spec_path in service_specs:
        try:
            resp = await _http_client.get(f"{base}{spec_path}", timeout=5.0)
            if resp.status_code != 200:
                continue
            spec = resp.json()
            # Prefix all paths with /api/{service} to avoid collisions
            for path, path_item in spec.get("paths", {}).items():
                combined["paths"][f"/api{path}"] = path_item
            # Merge schemas with service-namespaced keys
            for schema_name, schema_def in spec.get("components", {}).get("schemas", {}).items():
                combined["components"]["schemas"][f"{svc_name}_{schema_name}"] = schema_def
        except Exception:
            pass

    return combined


@app.get("/docs-master", include_in_schema=False)
async def master_docs() -> Response:
    """Serve a Swagger UI page pointing at the aggregated OpenAPI spec."""
    html = """<!DOCTYPE html>
<html>
<head>
  <title>AETHERMOOR — Master API Docs</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" >
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"> </script>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"> </script>
  <script>
    window.onload = function() {
      const ui = SwaggerUIBundle({
        url: "/openapi-master.json",
        dom_id: '#swagger-ui',
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
        layout: "StandaloneLayout"
      })
    }
  </script>
</body>
</html>"""
    return Response(content=html, media_type="text/html")


@app.api_route("/auth/{path:path}", methods=_METHODS)
async def proxy_auth(path: str, request: Request) -> Response:
    base, prefix = _UPSTREAMS["auth"]
    return await _proxy(request, f"{base}{prefix}/{path}")


@app.api_route("/players/{path:path}", methods=_METHODS)
async def proxy_players(path: str, request: Request) -> Response:
    base, prefix = _UPSTREAMS["players"]
    return await _proxy(request, f"{base}{prefix}/{path}")


@app.api_route("/world/{path:path}", methods=_METHODS)
async def proxy_world(path: str, request: Request) -> Response:
    base, prefix = _UPSTREAMS["world"]
    return await _proxy(request, f"{base}{prefix}/{path}")


@app.api_route("/combat/{path:path}", methods=_METHODS)
async def proxy_combat(path: str, request: Request) -> Response:
    base, prefix = _UPSTREAMS["combat"]
    return await _proxy(request, f"{base}{prefix}/{path}")


@app.api_route("/crafting/{path:path}", methods=_METHODS)
async def proxy_crafting(path: str, request: Request) -> Response:
    base, prefix = _UPSTREAMS["crafting"]
    return await _proxy(request, f"{base}{prefix}/{path}")


@app.api_route("/inventory/{path:path}", methods=_METHODS)
async def proxy_inventory(path: str, request: Request) -> Response:
    base, prefix = _UPSTREAMS["inventory"]
    return await _proxy(request, f"{base}{prefix}/{path}")
