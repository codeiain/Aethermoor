"""AETHERMOOR Guild Service — create, join, and manage player guilds."""
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
from pydantic import BaseModel, Field
from starlette.responses import Response as StarletteResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={'asctime': 'time', 'levelname': 'level', 'name': 'logger'},
    static_fields={'service': 'guild', 'environment': 'docker'}
)

for logger_name in ['', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
    _log = logging.getLogger(logger_name)
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(formatter)
    _log.handlers = [_handler]
    _log.setLevel(logging.INFO)
    _log.propagate = False

logger = logging.getLogger('guild')

SERVICE_TOKEN_SECRET = os.environ["SERVICE_TOKEN"]
REDIS_URL = os.environ.get("REDIS_URL", "redis://:@redis:6379/9")
PORT = int(os.environ.get("PORT", 8014))

GUILD_DB = 9
INVITE_TTL_SECONDS = 120
MAX_GUILD_NAME_LEN = 32
MAX_TAG_LEN = 4
CHAT_MESSAGE_LIMIT = 200  # ring-buffer depth per guild

ROLES = ("member", "officer", "leader")

REQUEST_LATENCY = Histogram('guild_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
REQUEST_COUNT = Counter('guild_request_count', 'Total request count', ['method', 'endpoint', 'http_status'])
ERROR_COUNT = Counter('guild_error_count', 'Total error count', ['method', 'endpoint', 'http_status'])
ACTIVE_REQUESTS = Gauge('guild_active_requests', 'Active requests in progress')
GUILD_COUNT = Gauge('guild_guilds', 'Active guilds')
GUILD_MEMBERS_TOTAL = Gauge('guild_members_total', 'Total guild members across all guilds')


# ── Auth helpers ────────────────────────────────────────────────────────────────

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


# ── Pydantic models ─────────────────────────────────────────────────────────────

class CreateGuildRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=MAX_GUILD_NAME_LEN)
    tag: str = Field(..., min_length=2, max_length=MAX_TAG_LEN)
    leader_id: str
    leader_name: str


class RenameGuildRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=MAX_GUILD_NAME_LEN)
    requester_id: str


class MotdRequest(BaseModel):
    motd: str = Field(..., max_length=256)
    requester_id: str


class InviteRequest(BaseModel):
    inviter_id: str
    inviter_name: str
    target_id: str


class LeaveRequest(BaseModel):
    character_id: str


class KickRequest(BaseModel):
    requester_id: str
    target_id: str


class PromoteRequest(BaseModel):
    requester_id: str
    target_id: str
    role: str  # "officer" or "leader"


class DemoteRequest(BaseModel):
    requester_id: str
    target_id: str


class ChatMessageRequest(BaseModel):
    author_id: str
    author_name: str
    message: str = Field(..., min_length=1, max_length=512)


# ── Core service ────────────────────────────────────────────────────────────────

class GuildService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    # ── Internal helpers ──────────────────────────────────────────────────────

    async def _get_guild_raw(self, guild_id: str) -> dict[str, Any]:
        data = await self.redis.hgetall(f"guild:{guild_id}")
        if not data:
            raise HTTPException(status_code=404, detail="Guild not found")
        return data

    async def _get_member_role(self, guild_id: str, character_id: str) -> str | None:
        raw = await self.redis.hget(f"guild:{guild_id}:members", character_id)
        if not raw:
            return None
        return json.loads(raw).get("role")

    async def _require_role(self, guild_id: str, character_id: str, min_role: str) -> str:
        role = await self._get_member_role(guild_id, character_id)
        if role is None:
            raise HTTPException(status_code=403, detail="Not a guild member")
        if ROLES.index(role) < ROLES.index(min_role):
            raise HTTPException(status_code=403, detail=f"Requires at least {min_role} role")
        return role

    async def _get_member_list(self, guild_id: str) -> list[dict[str, Any]]:
        raw_map = await self.redis.hgetall(f"guild:{guild_id}:members")
        members = []
        for char_id, raw in raw_map.items():
            entry = json.loads(raw)
            entry["character_id"] = char_id
            members.append(entry)
        return members

    # ── CRUD ──────────────────────────────────────────────────────────────────

    async def create_guild(self, req: CreateGuildRequest) -> dict[str, Any]:
        name_key = f"guild:name:{req.name.lower()}"
        tag_key = f"guild:tag:{req.tag.upper()}"

        existing_name = await self.redis.get(name_key)
        if existing_name:
            raise HTTPException(status_code=409, detail="Guild name already taken")

        existing_tag = await self.redis.get(tag_key)
        if existing_tag:
            raise HTTPException(status_code=409, detail="Guild tag already taken")

        existing_guild = await self.redis.get(f"guild:member:{req.leader_id}")
        if existing_guild:
            raise HTTPException(status_code=400, detail="Already in a guild")

        guild_id = str(uuid.uuid4())
        now = time.time()

        guild_data = {
            "name": req.name,
            "tag": req.tag.upper(),
            "leader_id": req.leader_id,
            "motd": "",
            "created_at": str(now),
        }
        await self.redis.hset(f"guild:{guild_id}", mapping=guild_data)
        await self.redis.set(name_key, guild_id)
        await self.redis.set(tag_key, guild_id)

        member_entry = json.dumps({"role": "leader", "joined_at": now, "name": req.leader_name})
        await self.redis.hset(f"guild:{guild_id}:members", req.leader_id, member_entry)
        await self.redis.set(f"guild:member:{req.leader_id}", guild_id)

        GUILD_COUNT.inc()
        GUILD_MEMBERS_TOTAL.inc()
        logger.info("guild_created", extra={"guild_id": guild_id, "name": req.name})

        return {
            "guild_id": guild_id,
            "name": req.name,
            "tag": req.tag.upper(),
            "leader_id": req.leader_id,
            "motd": "",
            "created_at": now,
            "member_count": 1,
        }

    async def get_guild(self, guild_id: str) -> dict[str, Any]:
        data = await self._get_guild_raw(guild_id)
        members = await self._get_member_list(guild_id)
        return {
            "guild_id": guild_id,
            "name": data["name"],
            "tag": data["tag"],
            "leader_id": data["leader_id"],
            "motd": data.get("motd", ""),
            "created_at": float(data.get("created_at", 0)),
            "members": members,
            "member_count": len(members),
        }

    async def get_guild_by_name(self, name: str) -> dict[str, Any]:
        guild_id = await self.redis.get(f"guild:name:{name.lower()}")
        if not guild_id:
            raise HTTPException(status_code=404, detail="Guild not found")
        return await self.get_guild(guild_id)

    async def get_guild_for_character(self, character_id: str) -> dict[str, Any]:
        guild_id = await self.redis.get(f"guild:member:{character_id}")
        if not guild_id:
            raise HTTPException(status_code=404, detail="Character is not in a guild")
        return await self.get_guild(guild_id)

    async def rename_guild(self, guild_id: str, req: RenameGuildRequest) -> dict[str, Any]:
        data = await self._get_guild_raw(guild_id)
        await self._require_role(guild_id, req.requester_id, "leader")

        new_name_key = f"guild:name:{req.name.lower()}"
        existing = await self.redis.get(new_name_key)
        if existing and existing != guild_id:
            raise HTTPException(status_code=409, detail="Guild name already taken")

        old_name_key = f"guild:name:{data['name'].lower()}"
        await self.redis.delete(old_name_key)
        await self.redis.set(new_name_key, guild_id)
        await self.redis.hset(f"guild:{guild_id}", "name", req.name)

        return await self.get_guild(guild_id)

    async def set_motd(self, guild_id: str, req: MotdRequest) -> dict[str, Any]:
        await self._get_guild_raw(guild_id)
        await self._require_role(guild_id, req.requester_id, "officer")
        await self.redis.hset(f"guild:{guild_id}", "motd", req.motd)
        return await self.get_guild(guild_id)

    async def disband_guild(self, guild_id: str, requester_id: str) -> bool:
        data = await self._get_guild_raw(guild_id)
        await self._require_role(guild_id, requester_id, "leader")

        members = await self._get_member_list(guild_id)
        for m in members:
            await self.redis.delete(f"guild:member:{m['character_id']}")
            GUILD_MEMBERS_TOTAL.dec()

        await self.redis.delete(f"guild:name:{data['name'].lower()}")
        await self.redis.delete(f"guild:tag:{data['tag'].upper()}")
        await self.redis.delete(f"guild:{guild_id}:members")
        await self.redis.delete(f"guild:{guild_id}")
        await self.redis.delete(f"guild:{guild_id}:chat")

        GUILD_COUNT.dec()
        logger.info("guild_disbanded", extra={"guild_id": guild_id})
        return True

    # ── Membership ────────────────────────────────────────────────────────────

    async def send_invite(self, guild_id: str, req: InviteRequest) -> dict[str, Any]:
        data = await self._get_guild_raw(guild_id)
        await self._require_role(guild_id, req.inviter_id, "officer")

        already_in = await self.redis.get(f"guild:member:{req.target_id}")
        if already_in:
            raise HTTPException(status_code=400, detail="Target is already in a guild")

        invite_key = f"guild:invite:{guild_id}:{req.target_id}"
        invite_data = json.dumps({
            "guild_id": guild_id,
            "guild_name": data["name"],
            "guild_tag": data["tag"],
            "inviter_id": req.inviter_id,
            "inviter_name": req.inviter_name,
            "target_id": req.target_id,
            "timestamp": time.time(),
        })
        await self.redis.set(invite_key, invite_data, ex=INVITE_TTL_SECONDS)

        return {
            "invite_id": f"{guild_id}:{req.target_id}",
            "guild_id": guild_id,
            "guild_name": data["name"],
            "inviter_id": req.inviter_id,
            "target_id": req.target_id,
            "expires_in": INVITE_TTL_SECONDS,
        }

    async def accept_invite(self, invite_id: str, character_id: str, character_name: str) -> dict[str, Any]:
        parts = invite_id.split(":", 1)
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid invite ID")
        guild_id, target_id = parts

        if target_id != character_id:
            raise HTTPException(status_code=403, detail="Invite is not for this character")

        invite_key = f"guild:invite:{guild_id}:{target_id}"
        raw = await self.redis.get(invite_key)
        if not raw:
            raise HTTPException(status_code=404, detail="Invite not found or expired")

        already_in = await self.redis.get(f"guild:member:{character_id}")
        if already_in:
            raise HTTPException(status_code=400, detail="Already in a guild")

        await self._get_guild_raw(guild_id)

        member_entry = json.dumps({"role": "member", "joined_at": time.time(), "name": character_name})
        await self.redis.hset(f"guild:{guild_id}:members", character_id, member_entry)
        await self.redis.set(f"guild:member:{character_id}", guild_id)
        await self.redis.delete(invite_key)

        GUILD_MEMBERS_TOTAL.inc()
        logger.info("guild_member_joined", extra={"guild_id": guild_id, "character_id": character_id})

        return await self.get_guild(guild_id)

    async def decline_invite(self, invite_id: str, character_id: str) -> bool:
        parts = invite_id.split(":", 1)
        if len(parts) != 2:
            return False
        guild_id, target_id = parts
        if target_id != character_id:
            raise HTTPException(status_code=403, detail="Invite is not for this character")
        invite_key = f"guild:invite:{guild_id}:{target_id}"
        deleted = await self.redis.delete(invite_key)
        return deleted > 0

    async def leave_guild(self, guild_id: str, character_id: str) -> bool:
        await self._get_guild_raw(guild_id)
        role = await self._get_member_role(guild_id, character_id)
        if role is None:
            raise HTTPException(status_code=400, detail="Not a guild member")

        if role == "leader":
            members = await self._get_member_list(guild_id)
            if len(members) > 1:
                raise HTTPException(
                    status_code=400,
                    detail="Leader must promote another member to leader before leaving, or disband the guild",
                )
            # last member leaving — auto-disband
            return await self.disband_guild(guild_id, character_id)

        await self.redis.hdel(f"guild:{guild_id}:members", character_id)
        await self.redis.delete(f"guild:member:{character_id}")
        GUILD_MEMBERS_TOTAL.dec()
        return True

    async def kick_member(self, guild_id: str, req: KickRequest) -> bool:
        await self._get_guild_raw(guild_id)
        requester_role = await self._require_role(guild_id, req.requester_id, "officer")

        target_role = await self._get_member_role(guild_id, req.target_id)
        if target_role is None:
            raise HTTPException(status_code=404, detail="Target is not a guild member")

        if req.target_id == req.requester_id:
            raise HTTPException(status_code=400, detail="Cannot kick yourself")

        # Officers cannot kick other officers or the leader
        if requester_role == "officer" and ROLES.index(target_role) >= ROLES.index("officer"):
            raise HTTPException(status_code=403, detail="Officers can only kick regular members")

        await self.redis.hdel(f"guild:{guild_id}:members", req.target_id)
        await self.redis.delete(f"guild:member:{req.target_id}")
        GUILD_MEMBERS_TOTAL.dec()
        return True

    async def promote_member(self, guild_id: str, req: PromoteRequest) -> dict[str, Any]:
        await self._get_guild_raw(guild_id)
        if req.role not in ("officer", "leader"):
            raise HTTPException(status_code=400, detail="Role must be 'officer' or 'leader'")

        await self._require_role(guild_id, req.requester_id, "leader")

        target_role = await self._get_member_role(guild_id, req.target_id)
        if target_role is None:
            raise HTTPException(status_code=404, detail="Target is not a guild member")

        if req.target_id == req.requester_id:
            raise HTTPException(status_code=400, detail="Cannot promote yourself")

        if req.role == "leader":
            # Transfer leadership: demote current leader to officer
            current_raw = await self.redis.hget(f"guild:{guild_id}:members", req.requester_id)
            current_entry = json.loads(current_raw)
            current_entry["role"] = "officer"
            await self.redis.hset(f"guild:{guild_id}:members", req.requester_id, json.dumps(current_entry))
            await self.redis.hset(f"guild:{guild_id}", "leader_id", req.target_id)

        target_raw = await self.redis.hget(f"guild:{guild_id}:members", req.target_id)
        target_entry = json.loads(target_raw)
        target_entry["role"] = req.role
        await self.redis.hset(f"guild:{guild_id}:members", req.target_id, json.dumps(target_entry))

        return await self.get_guild(guild_id)

    async def demote_member(self, guild_id: str, req: DemoteRequest) -> dict[str, Any]:
        await self._get_guild_raw(guild_id)
        await self._require_role(guild_id, req.requester_id, "leader")

        target_role = await self._get_member_role(guild_id, req.target_id)
        if target_role is None:
            raise HTTPException(status_code=404, detail="Target is not a guild member")
        if target_role == "leader":
            raise HTTPException(status_code=400, detail="Cannot demote the guild leader")
        if target_role == "member":
            raise HTTPException(status_code=400, detail="Member is already at the lowest rank")

        target_raw = await self.redis.hget(f"guild:{guild_id}:members", req.target_id)
        target_entry = json.loads(target_raw)
        target_entry["role"] = "member"
        await self.redis.hset(f"guild:{guild_id}:members", req.target_id, json.dumps(target_entry))

        return await self.get_guild(guild_id)

    # ── Guild chat ────────────────────────────────────────────────────────────

    async def post_chat_message(self, guild_id: str, req: ChatMessageRequest) -> dict[str, Any]:
        await self._get_guild_raw(guild_id)
        role = await self._get_member_role(guild_id, req.author_id)
        if role is None:
            raise HTTPException(status_code=403, detail="Not a guild member")

        msg = {
            "id": str(uuid.uuid4()),
            "author_id": req.author_id,
            "author_name": req.author_name,
            "message": req.message,
            "timestamp": time.time(),
        }
        chat_key = f"guild:{guild_id}:chat"
        await self.redis.lpush(chat_key, json.dumps(msg))
        await self.redis.ltrim(chat_key, 0, CHAT_MESSAGE_LIMIT - 1)

        return msg

    async def get_chat_history(self, guild_id: str, character_id: str, limit: int = 50) -> list[dict[str, Any]]:
        await self._get_guild_raw(guild_id)
        role = await self._get_member_role(guild_id, character_id)
        if role is None:
            raise HTTPException(status_code=403, detail="Not a guild member")

        limit = min(limit, CHAT_MESSAGE_LIMIT)
        raw_msgs = await self.redis.lrange(f"guild:{guild_id}:chat", 0, limit - 1)
        # lrange returns newest first (lpush) — reverse for chronological order
        return [json.loads(m) for m in reversed(raw_msgs)]

    # ── Roster with online status ─────────────────────────────────────────────

    async def get_roster(self, guild_id: str) -> dict[str, Any]:
        """Returns roster enriched with online status from social service Redis DB."""
        data = await self._get_guild_raw(guild_id)
        members = await self._get_member_list(guild_id)
        return {
            "guild_id": guild_id,
            "name": data["name"],
            "tag": data["tag"],
            "leader_id": data["leader_id"],
            "motd": data.get("motd", ""),
            "members": members,
            "member_count": len(members),
        }


# ── App lifecycle ───────────────────────────────────────────────────────────────

_redis_client: redis.Redis | None = None
_guild_service: GuildService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _redis_client, _guild_service
    logger.info("Guild service starting up")
    _redis_client = redis.from_url(REDIS_URL, db=GUILD_DB, decode_responses=True)
    _guild_service = GuildService(_redis_client)
    logger.info("Guild service ready")
    yield
    logger.info("Guild service shutting down")
    if _redis_client:
        await _redis_client.close()
    logger.info("Guild service stopped")


app = FastAPI(
    title="aethermoor-guild",
    version="1.0.0",
    description="Guild service — create, join, and manage player guilds",
    docs_url="/guild/docs",
    redoc_url="/guild/redoc",
    openapi_url="/guild/openapi.json",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "guild"}


@app.get("/metrics")
def metrics():
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


def _svc() -> GuildService:
    if not _guild_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    return _guild_service


# ── CRUD endpoints ──────────────────────────────────────────────────────────────

@app.post("/guild/create", status_code=status.HTTP_201_CREATED)
async def create_guild(
    body: CreateGuildRequest,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().create_guild(body)


@app.get("/guild/{guild_id}")
async def get_guild(
    guild_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().get_guild(guild_id)


@app.get("/guild/by-name/{name}")
async def get_guild_by_name(
    name: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().get_guild_by_name(name)


@app.get("/guild/character/{character_id}")
async def get_guild_for_character(
    character_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().get_guild_for_character(character_id)


@app.patch("/guild/{guild_id}/rename")
async def rename_guild(
    guild_id: str,
    body: RenameGuildRequest,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().rename_guild(guild_id, body)


@app.patch("/guild/{guild_id}/motd")
async def set_motd(
    guild_id: str,
    body: MotdRequest,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().set_motd(guild_id, body)


@app.delete("/guild/{guild_id}")
async def disband_guild(
    guild_id: str,
    requester_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    await _svc().disband_guild(guild_id, requester_id)
    return {"success": True, "message": "Guild disbanded"}


# ── Roster endpoint ─────────────────────────────────────────────────────────────

@app.get("/guild/{guild_id}/roster")
async def get_roster(
    guild_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().get_roster(guild_id)


# ── Invite endpoints ────────────────────────────────────────────────────────────

@app.post("/guild/{guild_id}/invite")
async def send_invite(
    guild_id: str,
    body: InviteRequest,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().send_invite(guild_id, body)


@app.post("/guild/invite/{invite_id}/accept")
async def accept_invite(
    invite_id: str,
    character_id: str,
    character_name: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().accept_invite(invite_id, character_id, character_name)


@app.post("/guild/invite/{invite_id}/decline")
async def decline_invite(
    invite_id: str,
    character_id: str,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    declined = await _svc().decline_invite(invite_id, character_id)
    return {"success": declined}


# ── Membership management ───────────────────────────────────────────────────────

@app.post("/guild/{guild_id}/leave")
async def leave_guild(
    guild_id: str,
    body: LeaveRequest,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    await _svc().leave_guild(guild_id, body.character_id)
    return {"success": True}


@app.post("/guild/{guild_id}/kick")
async def kick_member(
    guild_id: str,
    body: KickRequest,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    await _svc().kick_member(guild_id, body)
    return {"success": True}


@app.post("/guild/{guild_id}/promote")
async def promote_member(
    guild_id: str,
    body: PromoteRequest,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().promote_member(guild_id, body)


@app.post("/guild/{guild_id}/demote")
async def demote_member(
    guild_id: str,
    body: DemoteRequest,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().demote_member(guild_id, body)


# ── Guild chat ──────────────────────────────────────────────────────────────────

@app.post("/guild/{guild_id}/chat")
async def post_chat(
    guild_id: str,
    body: ChatMessageRequest,
    _: None = Header(None, alias="x-service-token"),
) -> dict[str, Any]:
    require_service_token(_)
    return await _svc().post_chat_message(guild_id, body)


@app.get("/guild/{guild_id}/chat")
async def get_chat(
    guild_id: str,
    character_id: str,
    limit: int = 50,
    _: None = Header(None, alias="x-service-token"),
) -> list[dict[str, Any]]:
    require_service_token(_)
    return await _svc().get_chat_history(guild_id, character_id, limit)
