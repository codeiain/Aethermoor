"""AETHERMOOR Party Service — MMO group gameplay management."""
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
    static_fields={'service': 'party', 'environment': 'docker'}
)

for logger_name in ['', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

logger = logging.getLogger('party')

SERVICE_TOKEN_SECRET = os.environ["SERVICE_TOKEN"]
REDIS_URL = os.environ.get("REDIS_URL", "redis://:@redis:6379/6")
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth:8001")
PORT = int(os.environ.get("PORT", 8011))

MAX_PARTY_SIZE = 5
PARTY_TTL_SECONDS = 7200
INVITE_TTL_SECONDS = 30
PARTY_DB = 5

REQUEST_LATENCY = Histogram('party_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
REQUEST_COUNT = Counter('party_request_count', 'Total request count', ['method', 'endpoint', 'http_status'])
ERROR_COUNT = Counter('party_error_count', 'Total error count', ['method', 'endpoint', 'http_status'])
ACTIVE_REQUESTS = Gauge('party_active_requests', 'Active requests in progress')
PARTY_COUNT = Gauge('party_parties', 'Active parties')
PARTY_MEMBERS = Gauge('party_members', 'Total party members')


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


class ServiceTokenError(Exception):
    pass


def require_service_token(x_service_token: str | None = Header(default=None)) -> None:
    if not _verify_service_token(x_service_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing service token")


def xp_multiplier(party_size: int) -> float:
    bonuses = {1: 1.0, 2: 1.10, 3: 1.12, 4: 1.15, 5: 1.18}
    return bonuses.get(party_size, 1.0)


class PartyService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def create_party(self, leader_id: str, leader_name: str) -> dict[str, Any]:
        party_id = str(uuid.uuid4())
        party_data = {
            "leader_id": leader_id,
            "leader_name": leader_name,
            "loot_mode": "free_for_all",
            "created_at": str(time.time()),
        }
        await self.redis.hset(f"party:{party_id}", mapping=party_data)
        await self.redis.expire(f"party:{party_id}", PARTY_TTL_SECONDS)
        
        await self.redis.sadd(f"party:{party_id}:members", leader_id)
        await self.redis.expire(f"party:{party_id}:members", PARTY_TTL_SECONDS)
        
        await self.redis.set(f"party:player:{leader_id}", party_id, ex=PARTY_TTL_SECONDS)
        
        PARTY_COUNT.inc()
        PARTY_MEMBERS.inc()
        
        return {
            "party_id": party_id,
            "leader_id": leader_id,
            "members": [leader_id],
            "loot_mode": "free_for_all",
        }

    async def get_party(self, character_id: str) -> dict[str, Any] | None:
        party_id = await self.redis.get(f"party:player:{character_id}")
        if not party_id:
            return None
        
        party_data = await self.redis.hgetall(f"party:{party_id}")
        if not party_data:
            return None
        
        members = list(await self.redis.smembers(f"party:{party_id}:members"))
        
        return {
            "party_id": party_id,
            "leader_id": party_data.get("leader_id"),
            "leader_name": party_data.get("leader_name"),
            "members": members,
            "loot_mode": party_data.get("loot_mode", "free_for_all"),
            "member_count": len(members),
            "xp_multiplier": xp_multiplier(len(members)),
        }

    async def send_invite(self, from_id: str, from_name: str, to_id: str) -> dict[str, Any]:
        existing_party = await self.get_party(from_id)
        if not existing_party:
            raise HTTPException(status_code=400, detail="You are not in a party")
        
        if existing_party["member_count"] >= MAX_PARTY_SIZE:
            raise HTTPException(status_code=400, detail="Party is full")
        
        existing_to_party = await self.get_party(to_id)
        if existing_to_party:
            raise HTTPException(status_code=400, detail="Target player is already in a party")
        
        invite_key = f"party:invite:{from_id}:{to_id}"
        invite_data = json.dumps({
            "party_id": existing_party["party_id"],
            "from_id": from_id,
            "from_name": from_name,
            "to_id": to_id,
            "timestamp": time.time(),
        })
        
        await self.redis.set(invite_key, invite_data, ex=INVITE_TTL_SECONDS)
        
        return {
            "invite_id": f"{from_id}:{to_id}",
            "from_id": from_id,
            "from_name": from_name,
            "to_id": to_id,
            "expires_in": INVITE_TTL_SECONDS,
        }

    async def accept_invite(self, invite_id: str) -> dict[str, Any]:
        parts = invite_id.split(":")
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid invite ID format")
        
        from_id, to_id = parts[0], parts[1]
        
        invite_key = f"party:invite:{from_id}:{to_id}"
        invite_data = await self.redis.get(invite_key)
        
        if not invite_data:
            raise HTTPException(status_code=404, detail="Invite not found or expired")
        
        invite = json.loads(invite_data)
        party_id = invite["party_id"]
        
        members = list(await self.redis.smembers(f"party:{party_id}:members"))
        if len(members) >= MAX_PARTY_SIZE:
            raise HTTPException(status_code=400, detail="Party is now full")
        
        await self.redis.sadd(f"party:{party_id}:members", to_id)
        
        await self.redis.delete(invite_key)
        
        await self.redis.set(f"party:player:{to_id}", party_id, ex=PARTY_TTL_SECONDS)
        
        PARTY_MEMBERS.inc()
        
        party_data = await self.redis.hgetall(f"party:{party_id}")
        
        return {
            "party_id": party_id,
            "leader_id": party_data.get("leader_id"),
            "members": list(await self.redis.smembers(f"party:{party_id}:members")),
            "loot_mode": party_data.get("loot_mode", "free_for_all"),
        }

    async def decline_invite(self, invite_id: str) -> bool:
        parts = invite_id.split(":")
        if len(parts) != 2:
            return False
        
        from_id, to_id = parts[0], parts[1]
        invite_key = f"party:invite:{from_id}:{to_id}"
        
        deleted = await self.redis.delete(invite_key)
        return deleted > 0

    async def leave_party(self, character_id: str) -> bool:
        party_info = await self.get_party(character_id)
        if not party_info:
            return False
        
        party_id = party_info["party_id"]
        
        if party_info["leader_id"] == character_id:
            await self._disband_party(party_id, "leader_left")
            return True
        
        await self.redis.srem(f"party:{party_id}:members", character_id)
        await self.redis.delete(f"party:player:{character_id}")
        
        PARTY_MEMBERS.dec()
        
        return True

    async def kick_member(self, leader_id: str, member_id: str) -> bool:
        party_info = await self.get_party(leader_id)
        if not party_info:
            raise HTTPException(status_code=404, detail="You are not in a party")
        
        if party_info["leader_id"] != leader_id:
            raise HTTPException(status_code=403, detail="Only the party leader can kick members")
        
        party_id = party_info["party_id"]
        member_party = await self.get_party(member_id)
        if not member_party or member_party["party_id"] != party_id:
            raise HTTPException(status_code=400, detail="Player is not in your party")
        
        if member_id == leader_id:
            raise HTTPException(status_code=400, detail="Cannot kick yourself")
        
        await self.redis.srem(f"party:{party_id}:members", member_id)
        await self.redis.delete(f"party:player:{member_id}")
        
        PARTY_MEMBERS.dec()
        
        return True

    async def promote_leader(self, current_leader_id: str, new_leader_id: str) -> dict[str, Any]:
        party_info = await self.get_party(current_leader_id)
        if not party_info:
            raise HTTPException(status_code=404, detail="You are not in a party")
        
        if party_info["leader_id"] != current_leader_id:
            raise HTTPException(status_code=403, detail="Only the party leader can promote")
        
        party_id = party_info["party_id"]
        member_party = await self.get_party(new_leader_id)
        if not member_party or member_party["party_id"] != party_id:
            raise HTTPException(status_code=400, detail="Player is not in your party")
        
        await self.redis.hset(f"party:{party_id}", "leader_id", new_leader_id)
        
        return await self.get_party(current_leader_id)

    async def set_loot_mode(self, leader_id: str, loot_mode: str) -> dict[str, Any]:
        valid_modes = ["free_for_all", "round_robin", "need_before_greed"]
        if loot_mode not in valid_modes:
            raise HTTPException(status_code=400, detail=f"Invalid loot mode. Must be one of: {valid_modes}")
        
        party_info = await self.get_party(leader_id)
        if not party_info:
            raise HTTPException(status_code=404, detail="You are not in a party")
        
        if party_info["leader_id"] != leader_id:
            raise HTTPException(status_code=403, detail="Only the party leader can change loot mode")
        
        party_id = party_info["party_id"]
        await self.redis.hset(f"party:{party_id}", "loot_mode", loot_mode)
        
        return await self.get_party(leader_id)

    async def _disband_party(self, party_id: str, reason: str) -> None:
        members = list(await self.redis.smembers(f"party:{party_id}:members"))
        
        for member_id in members:
            await self.redis.delete(f"party:player:{member_id}")
            PARTY_MEMBERS.dec()
        
        await self.redis.delete(f"party:{party_id}")
        await self.redis.delete(f"party:{party_id}:members")
        
        PARTY_COUNT.dec()


_redis_client: redis.Redis | None = None
_party_service: PartyService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _redis_client, _party_service
    logger.info("Party service starting up")
    _redis_client = redis.from_url(REDIS_URL, db=PARTY_DB, decode_responses=True)
    _party_service = PartyService(_redis_client)
    logger.info("Party service ready")
    yield
    logger.info("Party service shutting down")
    if _redis_client:
        await _redis_client.close()
    logger.info("Party service stopped")


app = FastAPI(
    title="aethermoor-party",
    version="1.0.0",
    description="Party service for MMO group gameplay",
    docs_url="/party/docs",
    redoc_url="/party/redoc",
    openapi_url="/party/openapi.json",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "party"}


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


# ── API Endpoints ───────────────────────────────────────────────────────────────


@app.post("/party/create")
async def create_party(
    leader_id: str,
    leader_name: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _party_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _party_service.create_party(leader_id, leader_name)


@app.get("/party/{character_id}")
async def get_party(
    character_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _party_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    party = await _party_service.get_party(character_id)
    if not party:
        raise HTTPException(status_code=404, detail="Player not in a party")
    
    return party


@app.post("/party/invite")
async def send_invite(
    from_id: str,
    from_name: str,
    to_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _party_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _party_service.send_invite(from_id, from_name, to_id)


@app.post("/party/invite/{invite_id}/accept")
async def accept_invite(
    invite_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _party_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return await _party_service.accept_invite(invite_id)


@app.post("/party/invite/{invite_id}/decline")
async def decline_invite(
    invite_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _party_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    deleted = await _party_service.decline_invite(invite_id)
    return {"success": deleted}


@app.post("/party/{party_id}/leave")
async def leave_party(
    character_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _party_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    success = await _party_service.leave_party(character_id)
    if not success:
        raise HTTPException(status_code=404, detail="Player not in a party")
    
    return {"success": True, "message": "Left party successfully"}


@app.post("/party/{party_id}/kick/{member_id}")
async def kick_member(
    party_id: str,
    member_id: str,
    leader_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _party_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    success = await _party_service.kick_member(leader_id, member_id)
    return {"success": success, "message": "Member kicked"}


@app.post("/party/{party_id}/promote/{new_leader_id}")
async def promote_leader(
    party_id: str,
    new_leader_id: str,
    current_leader_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _party_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return await _party_service.promote_leader(current_leader_id, new_leader_id)


@app.post("/party/{party_id}/loot-mode")
async def set_loot_mode(
    party_id: str,
    leader_id: str,
    loot_mode: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _party_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return await _party_service.set_loot_mode(leader_id, loot_mode)


@app.get("/party/{party_id}/xp-multiplier")
async def get_xp_multiplier(
    party_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    if not _party_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    party = await _party_service.get_party(party_id.split(":")[-1] if ":" in party_id else party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    
    return {
        "party_id": party["party_id"],
        "member_count": party["member_count"],
        "xp_multiplier": party["xp_multiplier"],
    }