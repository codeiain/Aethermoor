"""WebSocket presence endpoint for real-time multiplayer visibility.

Protocol (JSON messages):

  Client → Server (after connect):
    {"type": "auth", "token": "<jwt>", "character_id": "<id>",
     "name": "<display_name>", "level": <int>}

  Server → Client (on successful auth):
    {"type": "welcome", "players": [
       {"id": "...", "name": "...", "level": 1, "x": 5, "y": 10}, ...
    ]}

  Client → Server (position update, max 20/sec enforced server-side):
    {"type": "move", "x": <int>, "y": <int>}

  Server → all clients in zone:
    {"type": "player_join",  "id": "...", "name": "...", "level": 1, "x": 5, "y": 10}
    {"type": "player_move",  "id": "...", "x": 5, "y": 10}
    {"type": "player_leave", "id": "..."}

  Server → client (on error):
    {"type": "error", "message": "..."}

Architecture notes:
  - In-memory ConnectionManager (per-process). Acceptable for single-Pi deployment.
    Multi-process / multi-node would require Redis Pub/Sub fan-out (future work).
  - JWT passed in first message (browser WS API has no custom-header support).
  - Rate limit: 20 position updates/second per connection.
  - Position written to Redis on every accepted move so REST presence queries
    (GET /world/zones/{id}/players) stay consistent.
"""
from __future__ import annotations

import json
import logging
import time
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import cache as redis_cache
from auth_client import AuthVerificationError, verify_user_jwt

logger = logging.getLogger("world.presence")

router = APIRouter()

# ── Connection Manager ───────────────────────────────────────────────────────

class _PlayerConn:
    __slots__ = ("ws", "char_id", "name", "level", "x", "y", "last_move_ts")

    def __init__(
        self,
        ws: WebSocket,
        char_id: str,
        name: str,
        level: int,
        x: int,
        y: int,
    ) -> None:
        self.ws = ws
        self.char_id = char_id
        self.name = name
        self.level = level
        self.x = x
        self.y = y
        self.last_move_ts: float = 0.0

    def as_player_dict(self) -> dict[str, Any]:
        return {
            "id": self.char_id,
            "name": self.name,
            "level": self.level,
            "x": self.x,
            "y": self.y,
        }


class ConnectionManager:
    """Tracks all active WebSocket presence connections, keyed by zone."""

    def __init__(self) -> None:
        # zone_id → {char_id: _PlayerConn}
        self._zones: dict[str, dict[str, _PlayerConn]] = defaultdict(dict)

    def register(self, zone_id: str, conn: _PlayerConn) -> None:
        self._zones[zone_id][conn.char_id] = conn

    def unregister(self, zone_id: str, char_id: str) -> None:
        self._zones[zone_id].pop(char_id, None)
        if not self._zones[zone_id]:
            del self._zones[zone_id]

    def get_players(self, zone_id: str) -> list[dict[str, Any]]:
        return [c.as_player_dict() for c in self._zones.get(zone_id, {}).values()]

    async def broadcast_except(
        self, zone_id: str, exclude_char_id: str, message: dict[str, Any]
    ) -> None:
        """Send a message to all connections in zone except the sender."""
        text = json.dumps(message)
        dead: list[str] = []
        for char_id, conn in list(self._zones.get(zone_id, {}).items()):
            if char_id == exclude_char_id:
                continue
            try:
                await conn.ws.send_text(text)
            except Exception:  # noqa: BLE001
                dead.append(char_id)
        for char_id in dead:
            self.unregister(zone_id, char_id)


# Singleton — one per uvicorn worker process
_manager = ConnectionManager()

# ── Rate limit constant ──────────────────────────────────────────────────────

_MIN_MOVE_INTERVAL = 1.0 / 20  # 20 updates/second max


# ── WebSocket endpoint ───────────────────────────────────────────────────────

@router.websocket("/world/zones/{zone_id}/ws")
async def presence_ws(ws: WebSocket, zone_id: str) -> None:
    await ws.accept()

    conn: _PlayerConn | None = None

    try:
        # ── Step 1: auth handshake ──────────────────────────────────────────
        try:
            raw = await ws.receive_text()
            msg = json.loads(raw)
        except (json.JSONDecodeError, RuntimeError):
            await ws.send_text(json.dumps({"type": "error", "message": "bad auth frame"}))
            await ws.close(code=4000)
            return

        if msg.get("type") != "auth":
            await ws.send_text(json.dumps({"type": "error", "message": "expected auth frame"}))
            await ws.close(code=4001)
            return

        token = msg.get("token", "")
        char_id = msg.get("character_id", "")
        name = str(msg.get("name", "Unknown"))[:32]
        level = int(msg.get("level", 1))

        try:
            await verify_user_jwt(token)
        except AuthVerificationError as exc:
            await ws.send_text(json.dumps({"type": "error", "message": str(exc)}))
            await ws.close(code=4003)
            return

        # Read starting position from Redis (set by zone-enter REST call)
        all_pos = await redis_cache.get_all_player_positions(zone_id)
        start = all_pos.get(char_id, (0, 0))
        conn = _PlayerConn(ws=ws, char_id=char_id, name=name, level=level, x=start[0], y=start[1])

        _manager.register(zone_id, conn)

        # Send welcome with current player list
        await ws.send_text(json.dumps({
            "type": "welcome",
            "players": _manager.get_players(zone_id),
        }))

        # Broadcast join to others
        await _manager.broadcast_except(zone_id, char_id, {
            "type": "player_join",
            **conn.as_player_dict(),
        })

        logger.info("presence_join zone=%s char=%s name=%s", zone_id, char_id, name)

        # ── Step 2: message loop ────────────────────────────────────────────
        while True:
            try:
                raw = await ws.receive_text()
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if msg.get("type") != "move":
                continue

            # Rate limit
            now = time.monotonic()
            if now - conn.last_move_ts < _MIN_MOVE_INTERVAL:
                continue
            conn.last_move_ts = now

            try:
                nx = int(msg["x"])
                ny = int(msg["y"])
            except (KeyError, ValueError):
                continue

            conn.x = nx
            conn.y = ny

            # Update Redis so REST queries stay consistent
            await redis_cache.set_player_position(zone_id, char_id, nx, ny)

            # Broadcast to zone
            await _manager.broadcast_except(zone_id, char_id, {
                "type": "player_move",
                "id": char_id,
                "x": nx,
                "y": ny,
            })

    except WebSocketDisconnect:
        pass
    except Exception:  # noqa: BLE001
        logger.exception("presence_ws unhandled error zone=%s", zone_id)
    finally:
        if conn is not None:
            _manager.unregister(zone_id, conn.char_id)
            # Remove from Redis presence
            await redis_cache.remove_player_position(zone_id, conn.char_id)
            # Broadcast leave to remaining clients
            await _manager.broadcast_except(zone_id, conn.char_id, {
                "type": "player_leave",
                "id": conn.char_id,
            })
            logger.info("presence_leave zone=%s char=%s", zone_id, conn.char_id)
