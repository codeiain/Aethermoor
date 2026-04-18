"""Combat service HTTP endpoints for AETHERMOOR."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth_client import AuthVerificationError, verify_user_jwt
from combat_engine import process_player_action, start_combat
from database import get_db
from models import CombatActionLog, CombatLog, CombatOutcome
from redis_state import delete_combat_state, load_combat_state, refresh_combat_ttl, save_combat_state
from schemas import (
    ActionResponse,
    ActionType,
    CombatState,
    CombatStateResponse,
    CombatStatus,
    StartCombatRequest,
    StartCombatResponse,
    SubmitActionRequest,
)
from zero_trust import require_service_token

logger = logging.getLogger("combat")

router = APIRouter(prefix="/combat", tags=["combat"])


# ── Helpers ──────────────────────────────────────────────────────────────────

def _state_to_response(state: CombatState, message: str = "") -> CombatStateResponse:
    current_id = (
        state.turn_order[state.current_turn_index % len(state.turn_order)]
        if state.turn_order else None
    )
    return CombatStateResponse(
        combat_id=state.id,
        status=state.status,
        round=state.round,
        turn_order=state.turn_order,
        current_turn_id=current_id,
        combatants=state.combatants,
        last_actions=state.action_log[-10:],  # Last 10 actions
        xp_awarded=state.xp_awarded,
        gold_awarded=state.gold_awarded,
        message=message,
    )


async def _persist_combat(state: CombatState, db: AsyncSession) -> None:
    """Write the completed combat to PostgreSQL and remove from Redis."""
    outcome_map = {
        CombatStatus.PLAYER_WON: CombatOutcome.PLAYER_WON,
        CombatStatus.PLAYER_FLED: CombatOutcome.PLAYER_FLED,
        CombatStatus.PLAYER_DIED: CombatOutcome.PLAYER_DIED,
    }
    outcome = outcome_map.get(state.status)
    if outcome is None:
        return  # Still active — don't persist

    combat_log = CombatLog(
        id=state.id,
        player_character_id=state.player_character_id,
        npc_template_id=state.npc_template_id,
        zone_id=state.zone_id,
        outcome=outcome,
        rounds=state.round,
        xp_awarded=state.xp_awarded,
        gold_awarded=state.gold_awarded,
        npc_cr=next(
            (c.cr for c in state.combatants.values() if not c.is_player), 1.0
        ),
        ended_at=datetime.now(timezone.utc),
    )
    db.add(combat_log)

    for action in state.action_log:
        damage = 0
        if action.roll_result and "damage" in action.roll_result:
            damage = action.roll_result["damage"]
        db.add(CombatActionLog(
            combat_id=state.id,
            round_number=action.round,
            acting_entity=action.acting_id,
            action_type=action.action_type,
            target_entity=action.target_id,
            description=action.description,
            damage_dealt=damage,
        ))

    await db.commit()
    await delete_combat_state(state.id)
    logger.info("combat_persisted", extra={"combat_id": state.id, "outcome": outcome})


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/start",
    response_model=StartCombatResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_service_token)],
)
async def start_combat_endpoint(req: StartCombatRequest) -> StartCombatResponse:
    """Initiate a new combat encounter.

    Called by the world service or client when a player engages an NPC.
    Rolls initiative, establishes turn order, and saves state to Redis.
    """
    state = start_combat(req)
    await save_combat_state(state.id, state.model_dump(mode="json"))
    logger.info("combat_started", extra={"combat_id": state.id, "zone_id": req.zone_id})

    current_id = state.turn_order[0] if state.turn_order else None
    return StartCombatResponse(
        combat_id=state.id,
        status=state.status,
        round=state.round,
        turn_order=state.turn_order,
        current_turn_id=current_id,
        combatants=state.combatants,
        initiative_rolls=state.initiative_rolls,
        message=f"Combat begins! Initiative order: {', '.join(state.turn_order)}",
    )


@router.get(
    "/{combat_id}",
    response_model=CombatStateResponse,
    dependencies=[Depends(require_service_token)],
)
async def get_combat_state_endpoint(combat_id: str) -> CombatStateResponse:
    """Return the current combat state."""
    raw = await load_combat_state(combat_id)
    if raw is None:
        raise HTTPException(status_code=404, detail="Combat not found or expired")
    state = CombatState.model_validate(raw)
    return _state_to_response(state)


@router.post(
    "/{combat_id}/action",
    response_model=ActionResponse,
    dependencies=[Depends(require_service_token)],
)
async def submit_action_endpoint(
    combat_id: str,
    req: SubmitActionRequest,
    db: AsyncSession = Depends(get_db),
) -> ActionResponse:
    """Submit a player combat action.

    Resolves the player's action, then runs the NPC turn.
    Returns updated state including both actions.
    """
    raw = await load_combat_state(combat_id)
    if raw is None:
        raise HTTPException(status_code=404, detail="Combat not found or expired")

    state = CombatState.model_validate(raw)

    if state.status != CombatStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"Combat is not active (status={state.status})",
        )

    # Verify the player character is the active player in this combat
    if req.character_id != state.player_character_id:
        raise HTTPException(status_code=403, detail="Not your combat")

    try:
        state, player_action, npc_action = process_player_action(
            state,
            action_type=req.action_type,
            target_id=req.target_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Persist to DB if combat ended, otherwise refresh Redis TTL
    if state.status != CombatStatus.ACTIVE:
        await save_combat_state(state.id, state.model_dump(mode="json"))
        await _persist_combat(state, db)
    else:
        await save_combat_state(state.id, state.model_dump(mode="json"))
        await refresh_combat_ttl(combat_id)

    logger.info(
        "combat_action",
        extra={
            "combat_id": combat_id,
            "action_type": req.action_type,
            "status": state.status,
        },
    )

    current_id = (
        state.turn_order[state.current_turn_index % len(state.turn_order)]
        if state.turn_order and state.status == CombatStatus.ACTIVE else None
    )

    # Build outcome message
    if state.status == CombatStatus.PLAYER_WON:
        message = f"Victory! You defeated the enemy. +{state.xp_awarded} XP, +{state.gold_awarded} gold."
    elif state.status == CombatStatus.PLAYER_DIED:
        message = "You have been defeated. Respawning at nearest town..."
    elif state.status == CombatStatus.PLAYER_FLED:
        message = "You successfully fled combat!"
    else:
        message = ""

    return ActionResponse(
        combat_id=state.id,
        status=state.status,
        round=state.round,
        current_turn_id=current_id,
        combatants=state.combatants,
        action_result=player_action,
        npc_action=npc_action,
        message=message,
        xp_awarded=state.xp_awarded,
        gold_awarded=state.gold_awarded,
    )


@router.get(
    "/{combat_id}/history",
    response_model=list[dict],
    dependencies=[Depends(require_service_token)],
)
async def get_combat_history(combat_id: str) -> list[dict]:
    """Return the full action log for the combat session."""
    raw = await load_combat_state(combat_id)
    if raw is None:
        raise HTTPException(status_code=404, detail="Combat not found or expired")
    state = CombatState.model_validate(raw)
    return [a.model_dump(mode="json") for a in state.action_log]
