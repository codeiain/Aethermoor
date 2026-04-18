"""Pydantic request/response schemas for the world service."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Zone schemas ─────────────────────────────────────────────────────────────

class ZoneSummaryResponse(BaseModel):
    id: str
    name: str
    biome: str
    level_min: int
    level_max: int
    max_players: int
    current_players: int
    width: int
    height: int
    spawn_x: int
    spawn_y: int
    is_active: bool


class NpcTemplateSummary(BaseModel):
    id: str
    npc_type: str
    name: str
    spawn_x: int
    spawn_y: int
    patrol_path: list[dict[str, int]]
    respawn_timer_sec: int


class ZoneDetailResponse(ZoneSummaryResponse):
    """Full zone detail including tilemap (Phaser.js Tiled JSON format)."""
    tilemap: dict[str, Any]
    npc_templates: list[NpcTemplateSummary]


# ── Player presence schemas ──────────────────────────────────────────────────

class PlayerPresenceEntry(BaseModel):
    character_id: str
    x: int
    y: int


class NearbyPlayersResponse(BaseModel):
    zone_id: str
    players: list[PlayerPresenceEntry]
    count: int


# ── NPC state schemas ────────────────────────────────────────────────────────

class NpcStateEntry(BaseModel):
    npc_id: str
    npc_type: str
    name: str
    state: str  # alive | dead | respawning
    x: int
    y: int


class ZoneNpcsResponse(BaseModel):
    zone_id: str
    npcs: list[NpcStateEntry]


# ── Zone entry / exit schemas ────────────────────────────────────────────────

class ZoneEnterRequest(BaseModel):
    character_id: str
    from_zone_id: str | None = None


class ZoneEnterResponse(BaseModel):
    zone_id: str
    spawn_x: int
    spawn_y: int
    current_players: int
    max_players: int
    is_full: bool = False


class ZoneExitRequest(BaseModel):
    character_id: str


# ── World event schemas ──────────────────────────────────────────────────────

class WorldEventResponse(BaseModel):
    id: str
    name: str
    description: str
    event_type: str
    zone_id: str | None
    start_time: datetime | None
    end_time: datetime | None
    is_active: bool


class WorldEventsListResponse(BaseModel):
    events: list[WorldEventResponse]


# ── Internal schemas (service-to-service) ───────────────────────────────────

class NpcKillRequest(BaseModel):
    """Sent by the combat service when an NPC is killed."""
    npc_id: str
    zone_id: str


class WorldConfigUpdateRequest(BaseModel):
    value: str = Field(..., min_length=1, max_length=256)


class WorldConfigResponse(BaseModel):
    key: str
    value: str


# ── NPC management schemas ───────────────────────────────────────────────────

class NpcTemplateDetail(BaseModel):
    """Full NPC template including combat stats. Returned by internal endpoint."""
    id: str
    zone_id: str
    npc_type: str
    name: str
    spawn_x: int
    spawn_y: int
    patrol_path: list[dict[str, int]]
    respawn_timer_sec: int
    hp: int
    max_hp: int
    ac: int
    cr: float
    weapon: str
    npc_stats: dict[str, int]
    gold_drop_min: int
    gold_drop_max: int
    is_hostile: bool
    dialogue: dict | None = None


class NpcEngageRequest(BaseModel):
    """Player request to engage an NPC in combat."""
    character_id: str


class NpcEngageResponse(BaseModel):
    """Returned when a combat session is successfully started."""
    combat_id: str
    npc_id: str
    npc_name: str
    zone_id: str


class NpcInteractResponse(BaseModel):
    """Returned when a player talks to a friendly NPC."""
    npc_id: str
    npc_name: str
    npc_type: str
    zone_id: str
    dialogue: dict


# ── Utility ──────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
