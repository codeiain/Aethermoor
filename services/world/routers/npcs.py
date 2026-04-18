"""NPC endpoints — public player-facing and internal service-to-service.

Public endpoints (user JWT required):
  POST /world/zones/{zone_id}/npcs/{npc_id}/engage   — initiate combat
  POST /world/zones/{zone_id}/npcs/{npc_id}/interact — dialogue / quest hand-off

Internal endpoint (X-Service-Token required):
  GET /world/npcs/{npc_id} — full NPC template including combat stats
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

import cache as redis_cache
import character_client as char_client
import combat_client as cbt_client
from auth_client import AuthVerificationError, verify_user_jwt
from database import get_db
from models import NpcTemplate
from schemas import (
    NpcEngageRequest,
    NpcEngageResponse,
    NpcInteractResponse,
    NpcTemplateDetail,
)
from zero_trust import require_service_token

logger = logging.getLogger("world")

router = APIRouter(prefix="/world", tags=["npcs"])
_bearer = HTTPBearer()


async def _get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    try:
        return await verify_user_jwt(credentials.credentials)
    except AuthVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def _load_active_npc(npc_id: str, zone_id: str, db: AsyncSession) -> NpcTemplate:
    tmpl = await db.get(NpcTemplate, npc_id)
    if tmpl is None or not tmpl.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NPC not found")
    if tmpl.zone_id != zone_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NPC does not belong to the specified zone",
        )
    return tmpl


# ── Internal ─────────────────────────────────────────────────────────────────

@router.get(
    "/npcs/{npc_id}",
    response_model=NpcTemplateDetail,
    dependencies=[Depends(require_service_token)],
    tags=["internal"],
)
async def get_npc_template(
    npc_id: str,
    db: AsyncSession = Depends(get_db),
) -> NpcTemplateDetail:
    """Internal: return full NPC template including combat stats.

    Called by the combat service to look up NPC data when a fight starts.
    """
    tmpl = await db.get(NpcTemplate, npc_id)
    if tmpl is None or not tmpl.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NPC not found")

    return NpcTemplateDetail(
        id=tmpl.id,
        zone_id=tmpl.zone_id,
        npc_type=tmpl.npc_type,
        name=tmpl.name,
        spawn_x=tmpl.spawn_x,
        spawn_y=tmpl.spawn_y,
        patrol_path=tmpl.patrol_path,
        respawn_timer_sec=tmpl.respawn_timer_sec,
        hp=tmpl.hp,
        max_hp=tmpl.max_hp,
        ac=tmpl.ac,
        cr=tmpl.cr,
        weapon=tmpl.weapon,
        npc_stats=tmpl.npc_stats,
        gold_drop_min=tmpl.gold_drop_min,
        gold_drop_max=tmpl.gold_drop_max,
        is_hostile=tmpl.is_hostile,
        dialogue=tmpl.dialogue,
    )


# ── Public ────────────────────────────────────────────────────────────────────

@router.post(
    "/zones/{zone_id}/npcs/{npc_id}/engage",
    response_model=NpcEngageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def engage_npc(
    zone_id: str,
    npc_id: str,
    body: NpcEngageRequest,
    user: dict = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NpcEngageResponse:
    """Initiate combat with a hostile NPC.

    Orchestrates: NPC state check → character stat fetch → combat service start.
    The NPC must be hostile and in the alive state. Returns a combat_id the client
    uses to submit actions via the combat service.
    """
    tmpl = await _load_active_npc(npc_id, zone_id, db)

    if not tmpl.is_hostile:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{tmpl.name} is not hostile. Use /interact to talk to this NPC.",
        )

    npc_state = await redis_cache.get_npc_state(zone_id, npc_id)
    if npc_state and npc_state["state"] != redis_cache.NPC_STATE_ALIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{tmpl.name} is not available for combat right now.",
        )

    # Fetch character combat stats from character service
    try:
        char_stats = await char_client.get_combat_stats(
            character_id=body.character_id,
            user_id=user["user_id"],
        )
    except char_client.CharacterClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    if char_stats.get("current_hp", 0) <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Your character is dead and cannot engage in combat.",
        )

    # Start combat session
    try:
        combat_id = await cbt_client.start_combat(
            character_id=body.character_id,
            character_name=char_stats["name"],
            character_class=char_stats["character_class"],
            character_level=char_stats["level"],
            character_hp=char_stats["current_hp"],
            character_max_hp=char_stats["max_hp"],
            character_ac=char_stats["ac"],
            character_weapon=char_stats["weapon"],
            character_stats=char_stats["stats"],
            npc_template_id=npc_id,
            npc_name=tmpl.name,
            npc_hp=tmpl.max_hp,
            npc_max_hp=tmpl.max_hp,
            npc_ac=tmpl.ac,
            npc_weapon=tmpl.weapon,
            npc_cr=tmpl.cr,
            npc_stats=tmpl.npc_stats,
            npc_gold_drop_min=tmpl.gold_drop_min,
            npc_gold_drop_max=tmpl.gold_drop_max,
            zone_id=zone_id,
        )
    except cbt_client.CombatClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    logger.info(
        "npc_combat_started",
        extra={
            "combat_id": combat_id,
            "npc_id": npc_id,
            "character_id": body.character_id,
            "zone_id": zone_id,
        },
    )
    return NpcEngageResponse(
        combat_id=combat_id,
        npc_id=npc_id,
        npc_name=tmpl.name,
        zone_id=zone_id,
    )


@router.post(
    "/zones/{zone_id}/npcs/{npc_id}/interact",
    response_model=NpcInteractResponse,
)
async def interact_npc(
    zone_id: str,
    npc_id: str,
    user: dict = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NpcInteractResponse:
    """Interact with a friendly NPC — returns dialogue lines.

    For hostile NPCs use /engage instead. Merchants, quest givers, and guards
    have dialogue defined in their template. Returns the NPC's dialogue dict
    including any quest_giver_id the client can use to trigger quest accept.
    """
    tmpl = await _load_active_npc(npc_id, zone_id, db)

    if tmpl.is_hostile:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{tmpl.name} is hostile. Use /engage to start combat.",
        )

    dialogue = tmpl.dialogue or {
        "greeting": f"{tmpl.name} looks at you in silence.",
        "farewell": "",
    }

    return NpcInteractResponse(
        npc_id=npc_id,
        npc_name=tmpl.name,
        npc_type=tmpl.npc_type,
        zone_id=zone_id,
        dialogue=dialogue,
    )
