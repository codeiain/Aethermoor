"""NPC dialogue endpoint — context-aware quest dialogue based on character state."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth_client import AuthVerificationError, verify_user_jwt
from database import get_db
from models import CharacterQuest, Quest, QuestStatus
from schemas import DialogueOption, NpcDialogueResponse

logger = logging.getLogger("quest")
router = APIRouter(prefix="/quests/npc", tags=["npc"])
_bearer = HTTPBearer()


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


@router.get("/{npc_id}/dialogue", response_model=NpcDialogueResponse)
async def get_npc_dialogue(
    npc_id: str,
    character_id: str,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> NpcDialogueResponse:
    """Return context-aware dialogue options for an NPC.

    For each quest this NPC gives:
    - not started + prerequisites met → "offer" with briefing_dialogue
    - in_progress → progress reminder dialogue
    - ready_to_complete → turn-in prompt
    - completed → farewell
    """
    # Load all active quests for this NPC
    quests_result = await db.execute(
        select(Quest).where(
            Quest.npc_giver == npc_id,
            Quest.is_active.is_(True),
        ).order_by(Quest.sort_order)
    )
    quests = quests_result.scalars().all()

    if not quests:
        raise HTTPException(status_code=404, detail=f"No quests found for NPC '{npc_id}'")

    quest_ids = [q.id for q in quests]

    # Load this character's state for these quests
    cq_result = await db.execute(
        select(CharacterQuest)
        .options(selectinload(CharacterQuest.quest))
        .where(
            CharacterQuest.character_id == character_id,
            CharacterQuest.quest_id.in_(quest_ids),
        )
    )
    cq_map: dict[str, CharacterQuest] = {cq.quest_id: cq for cq in cq_result.scalars().all()}

    # Get character's completed quests to check prerequisites
    completed_result = await db.execute(
        select(CharacterQuest.quest_id).where(
            CharacterQuest.character_id == character_id,
            CharacterQuest.status == QuestStatus.COMPLETED,
        )
    )
    completed_ids: set[str] = {row for row in completed_result.scalars().all()}

    options: list[DialogueOption] = []

    for quest in quests:
        cq = cq_map.get(quest.id)

        if cq is None:
            # Quest not yet accepted — check prerequisites
            prereqs_met = all(p in completed_ids for p in quest.prerequisites)
            if not prereqs_met:
                continue  # NPC doesn't mention quests the player isn't ready for
            options.append(DialogueOption(
                quest_id=quest.id,
                quest_title=quest.title,
                type="offer",
                dialogue=quest.briefing_dialogue,
            ))

        elif cq.status == QuestStatus.IN_PROGRESS:
            completed_count = sum(
                obj.get("current", 0) for obj in cq.objectives
            )
            required_count = sum(obj["required"] for obj in cq.objectives)
            options.append(DialogueOption(
                quest_id=quest.id,
                quest_title=quest.title,
                type="in_progress",
                dialogue=(
                    f"You're making progress on '{quest.title}' — keep it up! "
                    f"({completed_count}/{required_count} objectives done)"
                ),
            ))

        elif cq.status == QuestStatus.READY_TO_COMPLETE:
            options.append(DialogueOption(
                quest_id=quest.id,
                quest_title=quest.title,
                type="ready_to_complete",
                dialogue=(
                    f"You've done it! Come, claim your reward for '{quest.title}'."
                ),
            ))

        elif cq.status == QuestStatus.COMPLETED:
            options.append(DialogueOption(
                quest_id=quest.id,
                quest_title=quest.title,
                type="completed",
                dialogue=quest.completion_dialogue,
            ))

    return NpcDialogueResponse(npc_id=npc_id, options=options)
