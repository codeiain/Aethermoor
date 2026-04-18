"""World events endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import WorldEvent
from schemas import (
    MessageResponse,
    WorldConfigResponse,
    WorldConfigUpdateRequest,
    WorldEventResponse,
    WorldEventsListResponse,
)
from zero_trust import require_service_token
import cache as redis_cache

router = APIRouter(prefix="/world", tags=["events"])


@router.get("/events", response_model=WorldEventsListResponse)
async def list_active_events(db: AsyncSession = Depends(get_db)) -> WorldEventsListResponse:
    """Return all currently active world events (global + all zones)."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(WorldEvent).where(WorldEvent.is_active.is_(True))
    )
    events = result.scalars().all()

    return WorldEventsListResponse(
        events=[
            WorldEventResponse(
                id=e.id,
                name=e.name,
                description=e.description,
                event_type=e.event_type.value,
                zone_id=e.zone_id,
                start_time=e.start_time,
                end_time=e.end_time,
                is_active=e.is_active,
            )
            for e in events
        ]
    )


# ── Internal admin endpoints (service-to-service, zero-trust protected) ─────

@router.post(
    "/events/{event_id}/activate",
    response_model=MessageResponse,
    dependencies=[Depends(require_service_token)],
)
async def activate_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Activate a world event. Internal: called by scheduler or admin service."""
    event = await db.get(WorldEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    event.is_active = True
    event.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return MessageResponse(message=f"Event '{event.name}' activated")


@router.post(
    "/events/{event_id}/deactivate",
    response_model=MessageResponse,
    dependencies=[Depends(require_service_token)],
)
async def deactivate_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Deactivate a world event."""
    event = await db.get(WorldEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    event.is_active = False
    event.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return MessageResponse(message=f"Event '{event.name}' deactivated")


# ── Live config endpoints ────────────────────────────────────────────────────

@router.get(
    "/admin/config/{key}",
    response_model=WorldConfigResponse,
    dependencies=[Depends(require_service_token)],
)
async def get_config(key: str) -> WorldConfigResponse:
    """Read a live-configurable world setting from Redis."""
    value = await redis_cache.get_config(key)
    return WorldConfigResponse(key=key, value=value)


@router.put(
    "/admin/config/{key}",
    response_model=WorldConfigResponse,
    dependencies=[Depends(require_service_token)],
)
async def update_config(
    key: str,
    body: WorldConfigUpdateRequest,
) -> WorldConfigResponse:
    """Update a live-configurable world setting in Redis (no service restart needed)."""
    await redis_cache.set_config(key, body.value)
    return WorldConfigResponse(key=key, value=body.value)
