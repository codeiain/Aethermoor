"""AETHERMOOR Social Service — Friends, block list, and online status."""
import os
import time
import json
import logging
import sys
import hashlib
import hmac
import uuid
from contextlib import asynccontextmanager
from typing import Any
from pythonjsonlogger import jsonlogger

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Header, Request, status
from starlette.responses import Response as StarletteResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={'asctime': 'time', 'levelname': 'level', 'name': 'logger'},
    static_fields={'service': 'social', 'environment': 'docker'}
)

for logger_name in ['', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

logger = logging.getLogger('social')

SERVICE_TOKEN_SECRET = os.environ["SERVICE_TOKEN"]
REDIS_URL = os.environ.get("REDIS_URL", "redis://:@redis:6379/7")
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth:8001")
PORT = int(os.environ.get("PORT", 8012))

SOCIAL_DB = 7
FRIEND_TTL_SECONDS = 86400 * 90
STATUS_TTL_SECONDS = 300
REQUEST_TTL_SECONDS = 60

REQUEST_LATENCY = Histogram('social_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
REQUEST_COUNT = Counter('social_request_count', 'Total request count', ['method', 'endpoint', 'http_status'])
ERROR_COUNT = Counter('social_error_count', 'Total error count', ['method', 'endpoint', 'http_status'])
ACTIVE_REQUESTS = Gauge('social_active_requests', 'Active requests in progress')
ONLINE_PLAYERS = Gauge('social_online_players', 'Players with online status')


def _make_service_token() -> str:
    ts = int(time.time()) // 60
    digest = hmac.new(
        SERVICE_TOKEN_SECRET.encode("utf-8"),
        str(ts).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{ts}:{digest}"


def _verify_service_token(token: str | None) -> bool:
    if not token:
        return False
    try:
        ts, digest = token.split(":", 1)
        now_bucket = int(time.time()) // 60
        ts_int = int(ts)
        if ts_int not in (now_bucket, now_bucket - 1):
            return False
        expected = hmac.new(
            SERVICE_TOKEN_SECRET.encode("utf-8"),
            ts.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(digest, expected)
    except (ValueError, AttributeError):
        return False


def require_service_token(x_service_token: str | None = Header(default=None)) -> None:
    if not _verify_service_token(x_service_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing service token")


class SocialService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def set_online_status(self, character_id: str, character_name: str) -> dict[str, Any]:
        status_key = f"social:status:{character_id}"
        status_data = json.dumps({"name": character_name, "last_seen": time.time()})
        await self.redis.set(status_key, status_data, ex=STATUS_TTL_SECONDS)
        await self.redis.sadd("social:online", character_id)
        ONLINE_PLAYERS.inc()
        return {"character_id": character_id, "online": True}

    async def set_offline_status(self, character_id: str) -> dict[str, Any]:
        status_key = f"social:status:{character_id}"
        await self.redis.delete(status_key)
        removed = await self.redis.srem("social:online", character_id)
        if removed:
            ONLINE_PLAYERS.dec()
        return {"character_id": character_id, "online": False}

    async def get_online_status(self, character_id: str) -> dict[str, Any]:
        is_online = await self.redis.sismember("social:online", character_id)
        status_key = f"social:status:{character_id}"
        status_data = await self.redis.get(status_key)
        if status_data:
            data = json.loads(status_data)
            return {"character_id": character_id, "online": bool(is_online), "last_seen": data.get("last_seen")}
        return {"character_id": character_id, "online": bool(is_online)}

    async def get_online_players(self) -> list[dict[str, Any]]:
        online_ids = await self.redis.smembers("social:online")
        result = []
        for char_id in online_ids:
            status_key = f"social:status:{char_id}"
            status_data = await self.redis.get(status_key)
            if status_data:
                data = json.loads(status_data)
                result.append({"character_id": char_id, "name": data.get("name"), "online": True})
        return result

    async def send_friend_request(self, from_id: str, from_name: str, to_name: str) -> dict[str, Any]:
        to_key = f"social:name:{to_name.lower()}"
        to_id = await self.redis.get(to_key)
        if not to_id:
            raise HTTPException(status_code=404, detail="Player not found")
        
        is_blocked = await self.redis.sismember(f"social:blocked:{to_id}", from_id)
        if is_blocked:
            raise HTTPException(status_code=403, detail="You are blocked by this player")
        
        existing = await self.redis.sismember(f"social:friends:{from_id}", to_id)
        if existing:
            raise HTTPException(status_code=400, detail="Already friends")
        
        request_key = f"social:request:{from_id}:{to_id}"
        request_data = json.dumps({"from_id": from_id, "from_name": from_name, "to_id": to_id, "timestamp": time.time()})
        await self.redis.set(request_key, request_data, ex=REQUEST_TTL_SECONDS)
        
        return {"request_id": f"{from_id}:{to_id}", "from_id": from_id, "to_id": to_id}

    async def accept_friend_request(self, request_id: str) -> dict[str, Any]:
        parts = request_id.split(":")
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid request ID")
        
        from_id, to_id = parts[0], parts[1]
        request_key = f"social:request:{from_id}:{to_id}"
        
        request_data = await self.redis.get(request_key)
        if not request_data:
            raise HTTPException(status_code=404, detail="Request not found or expired")
        
        await self.redis.sadd(f"social:friends:{from_id}", to_id)
        await self.redis.sadd(f"social:friends:{to_id}", from_id)
        
        await self.redis.delete(request_key)
        
        return {"success": True, "friend_id": to_id}

    async def decline_friend_request(self, request_id: str) -> bool:
        parts = request_id.split(":")
        if len(parts) != 2:
            return False
        from_id, to_id = parts[0], parts[1]
        request_key = f"social:request:{from_id}:{to_id}"
        return await self.redis.delete(request_key) > 0

    async def remove_friend(self, character_id: str, friend_id: str) -> bool:
        await self.redis.srem(f"social:friends:{character_id}", friend_id)
        await self.redis.srem(f"social:friends:{friend_id}", character_id)
        return True

    async def get_friends(self, character_id: str) -> list[dict[str, Any]]:
        friend_ids = await self.redis.smembers(f"social:friends:{character_id}")
        result = []
        for friend_id in friend_ids:
            is_online = await self.redis.sismember("social:online", friend_id)
            status_key = f"social:status:{friend_id}"
            status_data = await self.redis.get(status_key)
            name = "Unknown"
            if status_data:
                data = json.loads(status_data)
                name = data.get("name", "Unknown")
            result.append({"character_id": friend_id, "name": name, "online": bool(is_online)})
        return result

    async def block_player(self, blocker_id: str, blocked_name: str) -> dict[str, Any]:
        blocked_key = f"social:name:{blocked_name.lower()}"
        blocked_id = await self.redis.get(blocked_key)
        if not blocked_id:
            raise HTTPException(status_code=404, detail="Player not found")
        
        if blocker_id == blocked_id:
            raise HTTPException(status_code=400, detail="Cannot block yourself")
        
        await self.redis.sadd(f"social:blocked:{blocker_id}", blocked_id)
        
        return {"success": True, "blocked_id": blocked_id}

    async def unblock_player(self, blocker_id: str, blocked_id: str) -> bool:
        await self.redis.srem(f"social:blocked:{blocker_id}", blocked_id)
        return True

    async def get_blocked(self, character_id: str) -> list[dict[str, Any]]:
        blocked_ids = await self.redis.smembers(f"social:blocked:{character_id}")
        result = []
        for blocked_id in blocked_ids:
            status_key = f"social:status:{blocked_id}"
            status_data = await self.redis.get(status_key)
            name = "Unknown"
            if status_data:
                data = json.loads(status_data)
                name = data.get("name", "Unknown")
            result.append({"character_id": blocked_id, "name": name})
        return result

    async def is_blocked(self, character_id: str, other_id: str) -> bool:
        return await self.redis.sismember(f"social:blocked:{character_id}", other_id)


_redis_client: redis.Redis | None = None
_social_service: SocialService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _redis_client, _social_service
    logger.info("Social service starting up")
    _redis_client = redis.from_url(REDIS_URL, db=SOCIAL_DB, decode_responses=True)
    _social_service = SocialService(_redis_client)
    logger.info("Social service ready")
    yield
    logger.info("Social service shutting down")
    if _redis_client:
        await _redis_client.close()
    logger.info("Social service stopped")


app = FastAPI(
    title="aethermoor-social",
    version="1.0.0",
    description="Social service for friends, block list, and online status",
    docs_url="/social/docs",
    redoc_url="/social/redoc",
    openapi_url="/social/openapi.json",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "social"}


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


@app.post("/status/online")
async def set_online(
    character_id: str,
    character_name: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _social_service.set_online_status(character_id, character_name)


@app.post("/status/offline")
async def set_offline(
    character_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _social_service.set_offline_status(character_id)


@app.get("/status/{character_id}")
async def get_status(
    character_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _social_service.get_online_status(character_id)


@app.get("/status/online/list")
async def get_online(
    _: None = Header(None, alias="x-service-token"),
) -> list[dict[str, Any]]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _social_service.get_online_players()


@app.post("/friends/request")
async def send_friend_request(
    from_id: str,
    from_name: str,
    to_name: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _social_service.send_friend_request(from_id, from_name, to_name)


@app.post("/friends/request/{request_id}/accept")
async def accept_friend_request(
    request_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _social_service.accept_friend_request(request_id)


@app.post("/friends/request/{request_id}/decline")
async def decline_friend_request(
    request_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    deleted = await _social_service.decline_friend_request(request_id)
    return {"success": deleted}


@app.get("/friends/{character_id}")
async def get_friends(
    character_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> list[dict[str, Any]]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _social_service.get_friends(character_id)


@app.delete("/friends/{character_id}/{friend_id}")
async def remove_friend(
    character_id: str,
    friend_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    await _social_service.remove_friend(character_id, friend_id)
    return {"success": True}


@app.post("/block")
async def block_player(
    blocker_id: str,
    blocked_name: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _social_service.block_player(blocker_id, blocked_name)


@app.delete("/block/{blocker_id}/{blocked_id}")
async def unblock_player(
    blocker_id: str,
    blocked_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    await _social_service.unblock_player(blocker_id, blocked_id)
    return {"success": True}


@app.get("/block/{character_id}")
async def get_blocked(
    character_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> list[dict[str, Any]]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _social_service.get_blocked(character_id)


@app.get("/block/{character_id}/check/{other_id}")
async def check_blocked(
    character_id: str,
    other_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _social_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    is_blocked = await _social_service.is_blocked(character_id, other_id)
    return {"blocked": is_blocked}