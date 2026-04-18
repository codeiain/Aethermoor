"""Zone endpoints — public and internal.

Public endpoints require a valid user JWT (verified via Auth Service).
Internal zone entry/exit endpoints require X-Service-Token.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import cache as redis_cache
from auth_client import AuthVerificationError, verify_user_jwt
from database import get_db
from models import NpcTemplate, Zone
from player_client import PlayerServiceError, update_character_position
from schemas import (
    MessageResponse,
    NearbyPlayersResponse,
    NpcStateEntry,
    NpcTemplateSummary,
    PlayerPresenceEntry,
    ZoneDetailResponse,
    ZoneEnterRequest,
    ZoneEnterResponse,
    ZoneExitRequest,
    ZoneNpcsResponse,
    ZoneSummaryResponse,
)
from zero_trust import require_service_token

router = APIRouter(prefix="/world", tags=["zones"])
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


async def _require_active_zone(zone_id: str, db: AsyncSession) -> Zone:
    zone = await db.get(Zone, zone_id)
    if zone is None or not zone.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return zone


# ── Public endpoints ─────────────────────────────────────────────────────────

@router.get("/zones", response_model=list[ZoneSummaryResponse])
async def list_zones(db: AsyncSession = Depends(get_db)) -> list[ZoneSummaryResponse]:
    """List all active zones with current capacity info."""
    result = await db.execute(select(Zone).where(Zone.is_active.is_(True)))
    zones = result.scalars().all()

    responses = []
    for zone in zones:
        current = await redis_cache.get_zone_count(zone.id)
        responses.append(
            ZoneSummaryResponse(
                id=zone.id,
                name=zone.name,
                biome=zone.biome.value,
                level_min=zone.level_min,
                level_max=zone.level_max,
                max_players=zone.max_players,
                current_players=current,
                width=zone.width,
                height=zone.height,
                spawn_x=zone.spawn_x,
                spawn_y=zone.spawn_y,
                is_active=zone.is_active,
            )
        )
    return responses


@router.get("/zones/{zone_id}", response_model=ZoneDetailResponse)
async def get_zone(
    zone_id: str,
    db: AsyncSession = Depends(get_db),
) -> ZoneDetailResponse:
    """Return full zone detail including Phaser.js-compatible tilemap and NPC templates."""
    result = await db.execute(
        select(Zone)
        .options(selectinload(Zone.npc_templates))
        .where(Zone.id == zone_id, Zone.is_active.is_(True))
    )
    zone = result.scalar_one_or_none()
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    current = await redis_cache.get_zone_count(zone.id)
    return ZoneDetailResponse(
        id=zone.id,
        name=zone.name,
        biome=zone.biome.value,
        level_min=zone.level_min,
        level_max=zone.level_max,
        max_players=zone.max_players,
        current_players=current,
        width=zone.width,
        height=zone.height,
        spawn_x=zone.spawn_x,
        spawn_y=zone.spawn_y,
        is_active=zone.is_active,
        tilemap=zone.tilemap,
        npc_templates=[
            NpcTemplateSummary(
                id=t.id,
                npc_type=t.npc_type,
                name=t.name,
                spawn_x=t.spawn_x,
                spawn_y=t.spawn_y,
                patrol_path=t.patrol_path,
                respawn_timer_sec=t.respawn_timer_sec,
            )
            for t in zone.npc_templates
            if t.is_active
        ],
    )


@router.get(
    "/zones/{zone_id}/players",
    response_model=NearbyPlayersResponse,
    dependencies=[Depends(_get_current_user)],
)
async def get_nearby_players(
    zone_id: str,
    x: int = 0,
    y: int = 0,
    db: AsyncSession = Depends(get_db),
) -> NearbyPlayersResponse:
    """Return list of players within 15 tiles of (x, y) in the zone.

    Requires a valid user JWT. Query params: x, y (tile coordinates of the
    requesting character — used as the centre of the proximity search).
    """
    await _require_active_zone(zone_id, db)
    nearby = await redis_cache.get_nearby_players(zone_id, x, y, radius=15)
    return NearbyPlayersResponse(
        zone_id=zone_id,
        players=[
            PlayerPresenceEntry(
                character_id=p["character_id"], x=p["x"], y=p["y"]
            )
            for p in nearby
        ],
        count=len(nearby),
    )


@router.get("/zones/{zone_id}/npcs", response_model=ZoneNpcsResponse)
async def get_zone_npcs(
    zone_id: str,
    db: AsyncSession = Depends(get_db),
) -> ZoneNpcsResponse:
    """Return current NPC state for all active NPCs in the zone."""
    result = await db.execute(
        select(NpcTemplate).where(
            NpcTemplate.zone_id == zone_id,
            NpcTemplate.is_active.is_(True),
        )
    )
    templates = result.scalars().all()

    npc_states = []
    for tmpl in templates:
        state = await redis_cache.get_npc_state(zone_id, tmpl.id)
        if state is None:
            # NPC not yet initialised in Redis — default to spawn point
            npc_state_str = redis_cache.NPC_STATE_ALIVE
            x, y = tmpl.spawn_x, tmpl.spawn_y
        else:
            npc_state_str = state["state"]
            x, y = state["x"], state["y"]

        npc_states.append(
            NpcStateEntry(
                npc_id=tmpl.id,
                npc_type=tmpl.npc_type,
                name=tmpl.name,
                state=npc_state_str,
                x=x,
                y=y,
            )
        )

    return ZoneNpcsResponse(zone_id=zone_id, npcs=npc_states)


# ── Internal endpoints (service-to-service) ──────────────────────────────────

@router.post(
    "/zones/{zone_id}/enter",
    response_model=ZoneEnterResponse,
    dependencies=[Depends(require_service_token)],
)
async def zone_enter(
    zone_id: str,
    body: ZoneEnterRequest,
    db: AsyncSession = Depends(get_db),
) -> ZoneEnterResponse:
    """Record a player entering a zone.

    Internal endpoint called by the gateway after successful authentication.
    - Updates Redis zone count and player position
    - Calls Player Service to persist the new zone/coordinates
    - Returns spawn coordinates and capacity info

    If the zone is full, returns 409 Conflict with zone info so the caller
    can redirect to an overflow shard (sharding TBD; current behaviour: reject).
    """
    result = await db.execute(
        select(Zone).where(Zone.id == zone_id, Zone.is_active.is_(True))
    )
    zone = result.scalar_one_or_none()
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    # Check capacity before incrementing
    current = await redis_cache.get_zone_count(zone.id)
    if current >= zone.max_players:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Zone '{zone_id}' is full ({current}/{zone.max_players} players). "
                   "Shard overflow not yet implemented.",
        )

    # If the character was in another zone, clean up their old position
    if body.from_zone_id and body.from_zone_id != zone_id:
        await redis_cache.remove_player_position(body.from_zone_id, body.character_id)
        await redis_cache.decrement_zone_count(body.from_zone_id)

    # Add to new zone
    new_count = await redis_cache.increment_zone_count(zone.id)
    await redis_cache.set_player_position(
        zone.id, body.character_id, zone.spawn_x, zone.spawn_y
    )

    # Persist position in Player Service (best-effort — log failure, don't reject)
    try:
        await update_character_position(
            character_id=body.character_id,
            zone_id=zone.id,
            x=zone.spawn_x,
            y=zone.spawn_y,
        )
    except PlayerServiceError:
        # Non-fatal: Redis already reflects the new position.
        # Player Service will reconcile on next heartbeat.
        pass

    return ZoneEnterResponse(
        zone_id=zone.id,
        spawn_x=zone.spawn_x,
        spawn_y=zone.spawn_y,
        current_players=new_count,
        max_players=zone.max_players,
        is_full=new_count >= zone.max_players,
    )


@router.post(
    "/zones/{zone_id}/exit",
    response_model=MessageResponse,
    dependencies=[Depends(require_service_token)],
)
async def zone_exit(
    zone_id: str,
    body: ZoneExitRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Record a player exiting a zone. Cleans up Redis presence state."""
    await _require_active_zone(zone_id, db)
    await redis_cache.remove_player_position(zone_id, body.character_id)
    await redis_cache.decrement_zone_count(zone_id)
    return MessageResponse(message=f"Character {body.character_id} exited zone {zone_id}")
