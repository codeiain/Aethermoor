"""Quest endpoints — accept, progress, complete, and list quests."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth_client import AuthVerificationError, verify_user_jwt
from character_client import CharacterClientError, award_xp_and_gold
from database import get_db
from inventory_client import InventoryClientError, award_item
from models import CharacterQuest, Quest, QuestStatus
from schemas import (
    CharacterQuestResponse,
    CharacterQuestsResponse,
    CompleteQuestResponse,
    MessageResponse,
    ProgressResponse,
    ProgressUpdate,
)
from zero_trust import require_service_token

logger = logging.getLogger("quest")
router = APIRouter(prefix="/quests", tags=["quests"])
_bearer = HTTPBearer()


# ── Auth dependency ────────────────────────────────────────────────────────────

async def _current_user(
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


# ── Helpers ────────────────────────────────────────────────────────────────────

def _all_objectives_met(objectives: list[dict]) -> bool:
    return all(obj.get("current", 0) >= obj["required"] for obj in objectives)


def _build_cq_response(cq: CharacterQuest) -> CharacterQuestResponse:
    return CharacterQuestResponse(
        id=cq.id,
        character_id=cq.character_id,
        quest_id=cq.quest_id,
        quest_title=cq.quest.title,
        status=cq.status,
        objectives=cq.objectives,
        xp_reward=cq.quest.xp_reward,
        gold_reward=cq.quest.gold_reward,
        item_reward=cq.quest.item_reward,
        started_at=cq.started_at,
        completed_at=cq.completed_at,
    )


async def _get_completed_quest_ids(db: AsyncSession, character_id: str) -> set[str]:
    result = await db.execute(
        select(CharacterQuest.quest_id).where(
            CharacterQuest.character_id == character_id,
            CharacterQuest.status == QuestStatus.COMPLETED,
        )
    )
    return {row for row in result.scalars().all()}


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post(
    "/{character_id}/accept/{quest_id}",
    response_model=CharacterQuestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def accept_quest(
    character_id: str,
    quest_id: str,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> CharacterQuestResponse:
    """Accept a quest. Validates prerequisites and creates the CharacterQuest row."""
    quest = await db.get(Quest, quest_id)
    if quest is None or not quest.is_active:
        raise HTTPException(status_code=404, detail=f"Quest '{quest_id}' not found")

    # Idempotency: already accepted?
    existing = await db.execute(
        select(CharacterQuest)
        .options(selectinload(CharacterQuest.quest))
        .where(
            CharacterQuest.character_id == character_id,
            CharacterQuest.quest_id == quest_id,
        )
    )
    cq_existing = existing.scalar_one_or_none()
    if cq_existing is not None:
        if cq_existing.status == QuestStatus.COMPLETED:
            raise HTTPException(status_code=409, detail="Quest already completed")
        return _build_cq_response(cq_existing)

    # Check prerequisites
    if quest.prerequisites:
        completed_ids = await _get_completed_quest_ids(db, character_id)
        missing = [p for p in quest.prerequisites if p not in completed_ids]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"Prerequisites not met: {missing}",
            )

    # Initialise objectives with current=0
    objectives = [
        {**obj, "current": 0} for obj in quest.objectives_template
    ]

    cq = CharacterQuest(
        character_id=character_id,
        quest_id=quest_id,
        status=QuestStatus.IN_PROGRESS,
        objectives=objectives,
    )
    db.add(cq)
    await db.commit()
    await db.refresh(cq)

    # Load relationship for response
    result = await db.execute(
        select(CharacterQuest)
        .options(selectinload(CharacterQuest.quest))
        .where(CharacterQuest.id == cq.id)
    )
    cq = result.scalar_one()
    logger.info("character=%s accepted quest=%s", character_id, quest_id)
    return _build_cq_response(cq)


@router.get("/{character_id}", response_model=CharacterQuestsResponse)
async def list_quests(
    character_id: str,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> CharacterQuestsResponse:
    """List active and completed quests for a character."""
    result = await db.execute(
        select(CharacterQuest)
        .options(selectinload(CharacterQuest.quest))
        .where(CharacterQuest.character_id == character_id)
        .order_by(CharacterQuest.started_at)
    )
    all_cqs = result.scalars().all()

    active = [cq for cq in all_cqs if cq.status != QuestStatus.COMPLETED]
    completed = [cq for cq in all_cqs if cq.status == QuestStatus.COMPLETED]

    return CharacterQuestsResponse(
        character_id=character_id,
        active=[_build_cq_response(cq) for cq in active],
        completed=[_build_cq_response(cq) for cq in completed],
    )


@router.post(
    "/{character_id}/progress",
    response_model=ProgressResponse,
    dependencies=[Depends(require_service_token)],
)
async def update_progress(
    character_id: str,
    body: ProgressUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProgressResponse:
    """Update quest progress for a character. Called internally by world/combat services.

    Iterates over all in_progress quests, applies matching objective increments,
    and advances status to ready_to_complete when all objectives are met.
    """
    result = await db.execute(
        select(CharacterQuest)
        .options(selectinload(CharacterQuest.quest))
        .where(
            CharacterQuest.character_id == character_id,
            CharacterQuest.status == QuestStatus.IN_PROGRESS,
        )
    )
    in_progress = result.scalars().all()

    updated_quests: list[str] = []
    newly_ready: list[str] = []

    for cq in in_progress:
        changed = False
        objectives = list(cq.objectives)  # mutable copy

        for obj in objectives:
            if obj["type"] != body.type:
                continue

            # Match by the relevant target field
            match = False
            if body.type == "kill_count" and body.target and obj.get("target") == body.target:
                match = True
            elif body.type == "item_gather" and body.item_id and obj.get("item_id") == body.item_id:
                match = True
            elif body.type == "interact_npc" and body.npc_id and obj.get("npc_id") == body.npc_id:
                match = True
            elif body.type == "explore_location" and body.zone_id and obj.get("zone_id") == body.zone_id:
                match = True

            if match and obj["current"] < obj["required"]:
                obj["current"] = min(obj["current"] + body.amount, obj["required"])
                changed = True

        if not changed:
            continue

        # SQLAlchemy JSONB mutation tracking requires reassignment
        cq.objectives = objectives
        updated_quests.append(cq.quest_id)

        if _all_objectives_met(objectives):
            cq.status = QuestStatus.READY_TO_COMPLETE
            newly_ready.append(cq.quest_id)
            logger.info("character=%s quest=%s ready_to_complete", character_id, cq.quest_id)

    if updated_quests:
        await db.commit()

    return ProgressResponse(updated_quests=updated_quests, newly_ready=newly_ready)


@router.post(
    "/{character_id}/complete/{quest_id}",
    response_model=CompleteQuestResponse,
)
async def complete_quest(
    character_id: str,
    quest_id: str,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> CompleteQuestResponse:
    """Complete a quest and distribute rewards atomically.

    The quest is only marked completed if ALL reward service calls succeed.
    On partial failure the quest remains in ready_to_complete so the player
    can retry — no double-rewarding possible since we commit only on full success.
    """
    result = await db.execute(
        select(CharacterQuest)
        .options(selectinload(CharacterQuest.quest))
        .where(
            CharacterQuest.character_id == character_id,
            CharacterQuest.quest_id == quest_id,
        )
    )
    cq = result.scalar_one_or_none()

    if cq is None:
        raise HTTPException(status_code=404, detail="Quest not accepted by this character")
    if cq.status == QuestStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="Quest already completed")
    if cq.status == QuestStatus.IN_PROGRESS:
        raise HTTPException(status_code=422, detail="Quest objectives not yet complete")

    quest = cq.quest

    # Distribute rewards — all must succeed before we commit
    try:
        await award_xp_and_gold(character_id, quest.xp_reward, quest.gold_reward)
    except CharacterClientError as exc:
        logger.error("Failed to award XP/gold for quest=%s char=%s: %s", quest_id, character_id, exc)
        raise HTTPException(
            status_code=502,
            detail="Failed to award XP/gold — please try again",
        ) from exc

    item_awarded: str | None = None
    if quest.item_reward:
        try:
            await award_item(character_id, quest.item_reward, quest.item_reward_qty)
            item_awarded = quest.item_reward
        except InventoryClientError as exc:
            logger.error(
                "Failed to award item %s for quest=%s char=%s: %s",
                quest.item_reward, quest_id, character_id, exc,
            )
            raise HTTPException(
                status_code=502,
                detail=f"Failed to award item reward — {exc}",
            ) from exc

    # All reward calls succeeded — commit quest completion
    cq.status = QuestStatus.COMPLETED
    cq.completed_at = datetime.now(timezone.utc)
    await db.commit()

    logger.info(
        "character=%s completed quest=%s xp=%d gold=%d item=%s",
        character_id, quest_id, quest.xp_reward, quest.gold_reward, item_awarded,
    )

    return CompleteQuestResponse(
        quest_id=quest_id,
        quest_title=quest.title,
        xp_awarded=quest.xp_reward,
        gold_awarded=quest.gold_reward,
        item_awarded=item_awarded,
        message=quest.completion_dialogue,
    )
