"""Internal service-to-service endpoints for NPC state management and NPC ticks.

All endpoints require X-Service-Token. Called by combat service (kill/respawn)
and by the world service's own background NPC tick task.
"""
import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import cache as redis_cache
from database import get_db
from models import NpcTemplate
from pathfinding import CollisionGrid
from schemas import MessageResponse, NpcKillRequest
from zero_trust import require_service_token

router = APIRouter(prefix="/world", tags=["internal"])


@router.post(
    "/npcs/kill",
    response_model=MessageResponse,
    dependencies=[Depends(require_service_token)],
)
async def kill_npc(
    body: NpcKillRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Mark an NPC as dead and schedule its respawn.

    Called by the combat service when a player kills an NPC.
    The NPC will transition to 'respawning' state with a respawn_at timestamp.
    The NPC tick task will revive it when respawn_at is reached.
    """
    tmpl = await db.get(NpcTemplate, body.npc_id)
    if tmpl is None or not tmpl.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NPC not found")
    if tmpl.zone_id != body.zone_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NPC does not belong to the specified zone",
        )

    respawn_at = int(time.time()) + tmpl.respawn_timer_sec
    await redis_cache.set_npc_state(
        zone_id=body.zone_id,
        npc_id=body.npc_id,
        state=redis_cache.NPC_STATE_RESPAWNING,
        x=tmpl.spawn_x,
        y=tmpl.spawn_y,
        respawn_at=respawn_at,
    )
    return MessageResponse(
        message=f"NPC {body.npc_id} killed; respawns at epoch {respawn_at}"
    )


@router.post(
    "/zones/{zone_id}/npcs/tick",
    response_model=MessageResponse,
    dependencies=[Depends(require_service_token)],
)
async def npc_tick(
    zone_id: str,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Advance NPC patrol movement and handle respawns for a zone.

    Designed to be called once per second per zone (e.g. by the background task
    in main.py, or externally by a cron job for development/testing).

    Each call:
    1. Revives any NPCs whose respawn_at has passed.
    2. Moves alive NPCs one step along their patrol path via A*.
    """
    # Load zone for tilemap (needed by A*)
    from models import Zone as ZoneModel

    zone = await db.get(ZoneModel, zone_id)
    if zone is None or not zone.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    result = await db.execute(
        select(NpcTemplate).where(
            NpcTemplate.zone_id == zone_id,
            NpcTemplate.is_active.is_(True),
        )
    )
    templates = result.scalars().all()
    if not templates:
        return MessageResponse(message="No active NPCs in zone")

    grid = CollisionGrid.from_tilemap(zone.tilemap, zone.width, zone.height)
    now = int(time.time())
    moved = 0
    revived = 0

    for tmpl in templates:
        state = await redis_cache.get_npc_state(zone_id, tmpl.id)

        if state is None:
            # First tick: initialise NPC at spawn point
            await redis_cache.set_npc_state(
                zone_id=zone_id,
                npc_id=tmpl.id,
                state=redis_cache.NPC_STATE_ALIVE,
                x=tmpl.spawn_x,
                y=tmpl.spawn_y,
            )
            continue

        # Handle respawn
        if state["state"] == redis_cache.NPC_STATE_RESPAWNING:
            if now >= state["respawn_at"]:
                await redis_cache.set_npc_state(
                    zone_id=zone_id,
                    npc_id=tmpl.id,
                    state=redis_cache.NPC_STATE_ALIVE,
                    x=tmpl.spawn_x,
                    y=tmpl.spawn_y,
                )
                revived += 1
            continue

        if state["state"] != redis_cache.NPC_STATE_ALIVE:
            continue

        # Patrol movement (stationary NPCs have empty patrol_path)
        if not tmpl.patrol_path:
            continue

        # Determine next patrol waypoint (cycle through path)
        cx, cy = state["x"], state["y"]
        tx, ty = state["target_x"], state["target_y"]

        # If at target, advance to next waypoint
        if cx == tx and cy == ty:
            # Find the current waypoint index and move to next
            current_wp_idx = 0
            for i, wp in enumerate(tmpl.patrol_path):
                if wp["x"] == tx and wp["y"] == ty:
                    current_wp_idx = i
                    break
            next_wp_idx = (current_wp_idx + 1) % len(tmpl.patrol_path)
            next_wp = tmpl.patrol_path[next_wp_idx]
            tx, ty = next_wp["x"], next_wp["y"]

        next_step = grid.next_step(cx, cy, tx, ty)
        if next_step:
            nx, ny = next_step
            await redis_cache.set_npc_state(
                zone_id=zone_id,
                npc_id=tmpl.id,
                state=redis_cache.NPC_STATE_ALIVE,
                x=nx,
                y=ny,
                target_x=tx,
                target_y=ty,
            )
            moved += 1

    return MessageResponse(
        message=f"NPC tick complete: {moved} moved, {revived} revived"
    )
