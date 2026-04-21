"""AETHERMOOR WebSocket Gateway — real-time MMO communication.

Manages WebSocket connections for players, routes messages to channels,
and broadcasts zone/party/guild chat and system notifications.
"""
import os
import time
import json
import logging
import sys
import hashlib
import hmac
from contextlib import asynccontextmanager
from typing import Any
from pythonjsonlogger import jsonlogger

import redis.asyncio as redis
import websockets
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from starlette.responses import Response as StarletteResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={'asctime': 'time', 'levelname': 'level', 'name': 'logger'},
    static_fields={'service': 'websocket-gateway', 'environment': 'docker'}
)

for logger_name in ['', 'uvicorn', 'uvicorn.access', 'uvicorn.error']:
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

logger = logging.getLogger('websocket-gateway')

SERVICE_TOKEN_SECRET = os.environ["SERVICE_TOKEN"]
REDIS_URL = os.environ.get("REDIS_URL", "redis://:@redis:6379/5")
PORT = int(os.environ.get("PORT", 8010))

CONNECTION_COUNT = Gauge('websocket_connections', 'Active WebSocket connections')
MESSAGE_COUNT = Counter('websocket_messages_total', 'Total WebSocket messages', ['type', 'channel'])
BROADCAST_COUNT = Counter('websocket_broadcast_total', 'Total broadcast messages')


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, tuple[WebSocket, str]] = {}
        self.channels: dict[str, set[str]] = {}

    async def connect(self, websocket: WebSocket, player_id: str, channel: str):
        await websocket.accept()
        self.active[player_id] = (websocket, channel)
        if channel not in self.channels:
            self.channels[channel] = set()
        self.channels[channel].add(player_id)
        CONNECTION_COUNT.inc()
        logger.info(f"Player {player_id} connected to channel {channel}")

    async def disconnect(self, player_id: str):
        if player_id in self.active:
            _, channel = self.active.pop(player_id)
            if channel in self.channels:
                self.channels[channel].discard(player_id)
            CONNECTION_COUNT.dec()
            logger.info(f"Player {player_id} disconnected from channel {channel}")

    async def send_to_player(self, player_id: str, message: dict):
        if player_id in self.active:
            websocket, _ = self.active[player_id]
            await websocket.send_json(message)

    async def broadcast_to_channel(self, channel: str, message: dict):
        if channel in self.channels:
            for player_id in self.channels[channel]:
                await self.send_to_player(player_id, message)
            BROADCAST_COUNT.inc(len(self.channels[channel]))


manager = ConnectionManager()
_redis_client: redis.Redis | None = None


def _make_service_token() -> str:
    ts = int(time.time()) // 60
    digest = hmac.new(
        SERVICE_TOKEN_SECRET.encode("utf-8"),
        str(ts).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{ts}:{digest}"


def _verify_service_token(token: str) -> bool:
    if not token:
        return False
    try:
        ts, digest = token.split(":", 1)
        expected = hmac.new(
            SERVICE_TOKEN_SECRET.encode("utf-8"),
            ts.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(digest, expected)
    except ValueError:
        return False


async def verify_player_token(player_id: str, token: str, service_token: str) -> bool:
    if not _verify_service_token(service_token):
        return False
    if not _redis_client:
        return False
    key = f"player:token:{player_id}"
    stored = await _redis_client.get(key)
    return stored and hmac.compare_digest(stored.decode(), token)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _redis_client
    logger.info("WebSocket Gateway starting up")
    _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    logger.info("WebSocket Gateway ready")
    yield
    logger.info("WebSocket Gateway shutting down")
    if _redis_client:
        await _redis_client.close()
    logger.info("WebSocket Gateway stopped")


app = FastAPI(
    title="aethermoor-websocket-gateway",
    version="1.0.0",
    docs_url="/websocket/docs",
    redoc_url="/websocket/redoc",
    openapi_url="/websocket/openapi.json",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "websocket-gateway"}


@app.get("/metrics")
def metrics():
    return StarletteResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/services/status")
async def services_status() -> dict:
    return {
        "overall": "ok",
        "service": "websocket-gateway",
        "active_connections": len(manager.active),
        "channels": {ch: len(pl) for ch, pl in manager.channels.items()},
    }


async def handle_websocket(websocket: WebSocket, player_id: str, token: str):
    service_token = websocket.headers.get("x-service-token", "")
    if not await verify_player_token(player_id, token, service_token):
        await websocket.close(code=4003, reason="Unauthorized")
        return

    channel = f"zone:{player_id}"
    await manager.connect(websocket, player_id, channel)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "unknown")
            MESSAGE_COUNT.labels(msg_type, channel).inc()

            if msg_type == "chat":
                await manager.broadcast_to_channel(channel, {
                    "type": "chat",
                    "from": player_id,
                    "message": data.get("message", ""),
                    "timestamp": time.time(),
                })
            elif msg_type == "heartbeat":
                await websocket.send_json({"type": "heartbeat_ack", "ts": time.time()})
            elif msg_type == "join_channel":
                old_channel = channel
                channel = data.get("channel", old_channel)
                if old_channel != channel:
                    manager.active[player_id] = (websocket, channel)
                    manager.channels[old_channel].discard(player_id)
                    if channel not in manager.channels:
                        manager.channels[channel] = set()
                    manager.channels[channel].add(player_id)
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(player_id)


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str, token: str = ""):
    await handle_websocket(websocket, player_id, token)