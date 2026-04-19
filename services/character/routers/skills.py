"""Skill tree endpoints for the character service.

All endpoints require a valid user JWT. All unlock validation is server-side only.
"""
import json
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_client import AuthVerificationError, verify_user_jwt
from database import get_db
from models import Character, PlayerSkills
from schemas import (
    RespecResponse,
    SkillTreeResponse,
    UnlockSkillRequest,
    UnlockSkillResponse,
)
from skill_data import get_tree, get_skill

router = APIRouter(prefix="/players", tags=["skills"])
_bearer = HTTPBearer()

RESPEC_GOLD_MULTIPLIER = 50   # 50g × level
RESPEC_COOLDOWN_DAYS = 7


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


async def _get_own_character(character_id: str, user: dict, db: AsyncSession) -> Character:
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.is_deleted.is_(False),
        )
    )
    char = result.scalar_one_or_none()
    if char is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if char.user_id != user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return char


async def _get_or_create_skills(character_id: str, db: AsyncSession) -> PlayerSkills:
    """Fetch PlayerSkills row, creating it lazily if it doesn't exist yet."""
    result = await db.execute(
        select(PlayerSkills).where(PlayerSkills.character_id == character_id)
    )
    ps = result.scalar_one_or_none()
    if ps is None:
        ps = PlayerSkills(character_id=character_id)
        db.add(ps)
        await db.flush()
    return ps


def _unlocked_list(ps: PlayerSkills) -> list[str]:
    return json.loads(ps.unlocked_skills_json)


def _build_tree_response(char: Character, ps: PlayerSkills) -> SkillTreeResponse:
    tree = get_tree(char.character_class.value)
    if tree is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill tree not available for class '{char.character_class.value}' yet",
        )

    unlocked = _unlocked_list(ps)
    talent_total = char.level  # 1 TP per level, first at level 1

    return SkillTreeResponse(
        class_id=tree["class_id"],
        display_name=tree["display_name"],
        class_passive=tree["class_passive"],
        branches=tree["branches"],
        talent_points_total=talent_total,
        talent_points_spent=ps.talent_points_spent,
        unlocked_skills=unlocked,
    )


@router.get("/{character_id}/skill-tree", response_model=SkillTreeResponse)
async def get_skill_tree(
    character_id: str,
    user: dict = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SkillTreeResponse:
    """Return the skill tree for the character's class plus their current unlock state."""
    char = await _get_own_character(character_id, user, db)
    ps = await _get_or_create_skills(character_id, db)
    await db.commit()
    return _build_tree_response(char, ps)


@router.post("/{character_id}/skills/unlock", response_model=UnlockSkillResponse)
async def unlock_skill(
    character_id: str,
    body: UnlockSkillRequest,
    user: dict = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UnlockSkillResponse:
    """Spend talent points to unlock a skill. All gating rules enforced server-side."""
    char = await _get_own_character(character_id, user, db)
    ps = await _get_or_create_skills(character_id, db)

    skill = get_skill(char.character_class.value, body.skill_id)
    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{body.skill_id}' not found for class '{char.character_class.value}'",
        )

    unlocked = _unlocked_list(ps)

    if body.skill_id in unlocked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Skill already unlocked",
        )

    # Level gate
    if char.level < skill["level_requirement"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requires character level {skill['level_requirement']} (you are level {char.level})",
        )

    # Prerequisite check
    missing = [p for p in skill["prerequisites"] if p not in unlocked]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing prerequisites: {', '.join(missing)}",
        )

    # TP budget check
    talent_total = char.level
    new_spent = ps.talent_points_spent + skill["tp_cost"]
    if new_spent > talent_total:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Not enough talent points: need {skill['tp_cost']}, "
                f"have {talent_total - ps.talent_points_spent} remaining"
            ),
        )

    # Commit unlock
    unlocked.append(body.skill_id)
    ps.unlocked_skills_json = json.dumps(unlocked)
    ps.talent_points_spent = new_spent
    await db.commit()

    return UnlockSkillResponse(
        skill_id=body.skill_id,
        talent_points_total=talent_total,
        talent_points_spent=new_spent,
        unlocked_skills=unlocked,
    )


@router.post("/{character_id}/skills/respec", response_model=RespecResponse)
async def respec_skills(
    character_id: str,
    user: dict = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RespecResponse:
    """Reset all skill unlocks. Costs 50g × character level; once per 7 days."""
    char = await _get_own_character(character_id, user, db)
    ps = await _get_or_create_skills(character_id, db)

    # Cooldown check
    if ps.last_respec_at is not None:
        next_allowed = ps.last_respec_at + timedelta(days=RESPEC_COOLDOWN_DAYS)
        if datetime.now(timezone.utc) < next_allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Respec available again after {next_allowed.isoformat()}",
            )

    gold_cost = RESPEC_GOLD_MULTIPLIER * char.level
    if char.gold < gold_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient gold: respec costs {gold_cost}g (you have {char.gold}g)",
        )

    # Atomic deduct + reset
    char.gold -= gold_cost
    ps.unlocked_skills_json = "[]"
    ps.talent_points_spent = 0
    ps.last_respec_at = datetime.now(timezone.utc)
    await db.commit()

    return RespecResponse(
        gold_cost=gold_cost,
        talent_points_total=char.level,
        talent_points_spent=0,
        unlocked_skills=[],
    )
