"""Admin endpoints for live economy config updates.

All endpoints require a valid X-Service-Token — not exposed to players.
"""
import logging

from fastapi import APIRouter, Depends

import cache
from schemas import ConfigResponse, ConfigUpdateRequest
from zero_trust import require_service_token

logger = logging.getLogger("economy")
router = APIRouter(prefix="/economy/admin", tags=["admin"])


@router.get("/config", response_model=ConfigResponse)
async def get_config(_: None = Depends(require_service_token)) -> ConfigResponse:
    """Retrieve current live economy configuration."""
    config = await cache.get_config()
    return ConfigResponse(**config)


@router.post("/config", response_model=ConfigResponse)
async def update_config(
    body: ConfigUpdateRequest,
    _: None = Depends(require_service_token),
) -> ConfigResponse:
    """Update live economy configuration. Changes take effect immediately — no restart needed."""
    updates = body.model_dump(exclude_none=True)
    if updates:
        await cache.set_config(updates)
        logger.info("Economy config updated: %s", updates)

    config = await cache.get_config()
    return ConfigResponse(**config)
