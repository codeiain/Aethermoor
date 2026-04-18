"""Player-facing API endpoints for the character service.

All endpoints require a valid user JWT (verified via Auth Service).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth_client import AuthVerificationError, verify_user_jwt
from database import get_db
from dnd import generate_ability_scores, max_hp_at_level_1
from models import (
    BackpackItem,
    Character,
    CharacterPosition,
    EquipmentSlot,
    EquipmentSlotName,
)
from schemas import (
    AbilityScores,
    BackpackItemResponse,
    CharacterDetailResponse,
    CharacterSummaryResponse,
    CreateCharacterRequest,
    EquipmentSlotResponse,
    MessageResponse,
    PositionResponse,
    TutorialStateResponse,
)

router = APIRouter(prefix="/players", tags=["players"])
_bearer = HTTPBearer()

MAX_CHARACTERS_PER_USER = 3
BACKPACK_SLOTS = 24


async def _get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    """FastAPI dependency: verify JWT via Auth Service, return {user_id, username}."""
    try:
        return await verify_user_jwt(credentials.credentials)
    except AuthVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def _build_detail_response(char: Character) -> CharacterDetailResponse:
    pos = char.position
    return CharacterDetailResponse(
        id=char.id,
        user_id=char.user_id,
        slot=char.slot,
        name=char.name,
        character_class=char.character_class,
        ability_scores=AbilityScores(
            strength=char.strength,
            dexterity=char.dexterity,
            constitution=char.constitution,
            intelligence=char.intelligence,
            wisdom=char.wisdom,
            charisma=char.charisma,
        ),
        level=char.level,
        xp=char.xp,
        current_hp=char.current_hp,
        max_hp=char.max_hp,
        gold=char.gold,
        position=PositionResponse(
            zone_id=pos.zone_id,
            x=pos.x,
            y=pos.y,
            respawn_zone_id=pos.respawn_zone_id,
            respawn_x=pos.respawn_x,
            respawn_y=pos.respawn_y,
            last_seen=pos.last_seen,
        ) if pos else None,
        equipment=[
            EquipmentSlotResponse(slot_name=e.slot_name, item_id=e.item_id)
            for e in char.equipment
        ],
        backpack=[
            BackpackItemResponse(
                slot_index=b.slot_index, item_id=b.item_id, quantity=b.quantity
            )
            for b in char.backpack
        ],
        created_at=char.created_at,
        updated_at=char.updated_at,
    )


@router.post(
    "/create",
    response_model=CharacterDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_character(
    body: CreateCharacterRequest,
    user: dict = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CharacterDetailResponse:
    """Create a new character for the authenticated user."""
    user_id = user["user_id"]

    # Check character count
    count_result = await db.execute(
        select(Character).where(
            Character.user_id == user_id,
            Character.is_deleted.is_(False),
        )
    )
    existing = count_result.scalars().all()
    if len(existing) >= MAX_CHARACTERS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_CHARACTERS_PER_USER} characters per account",
        )

    # Check slot availability
    slot_taken = any(c.slot == body.slot for c in existing)
    if slot_taken:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slot {body.slot} is already occupied",
        )

    # Generate D&D ability scores
    scores = generate_ability_scores()
    hp = max_hp_at_level_1(body.character_class.value, scores["constitution"])

    char = Character(
        user_id=user_id,
        slot=body.slot,
        name=body.name,
        character_class=body.character_class,
        strength=scores["strength"],
        dexterity=scores["dexterity"],
        constitution=scores["constitution"],
        intelligence=scores["intelligence"],
        wisdom=scores["wisdom"],
        charisma=scores["charisma"],
        max_hp=hp,
        current_hp=hp,
        xp=0,
        level=1,
        gold=0,
    )
    db.add(char)
    await db.flush()  # get char.id

    # Initialise world position at starter town
    pos = CharacterPosition(character_id=char.id)
    db.add(pos)

    # Pre-populate empty equipment slots
    for slot_name in EquipmentSlotName:
        db.add(EquipmentSlot(character_id=char.id, slot_name=slot_name, item_id=None))

    await db.commit()

    # Reload with relationships
    result = await db.execute(
        select(Character)
        .options(
            selectinload(Character.position),
            selectinload(Character.equipment),
            selectinload(Character.backpack),
        )
        .where(Character.id == char.id)
    )
    char = result.scalar_one()
    return _build_detail_response(char)


@router.get("/me", response_model=list[CharacterSummaryResponse])
async def list_my_characters(
    user: dict = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CharacterSummaryResponse]:
    """Return summary of all characters for the authenticated user."""
    result = await db.execute(
        select(Character).where(
            Character.user_id == user["user_id"],
            Character.is_deleted.is_(False),
        )
    )
    chars = result.scalars().all()
    return [
        CharacterSummaryResponse(
            id=c.id,
            slot=c.slot,
            name=c.name,
            character_class=c.character_class,
            level=c.level,
            xp=c.xp,
            current_hp=c.current_hp,
            max_hp=c.max_hp,
            gold=c.gold,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in chars
    ]


@router.get("/{character_id}", response_model=CharacterDetailResponse)
async def get_character(
    character_id: str,
    user: dict = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CharacterDetailResponse:
    """Get full character details. Only the owning user may access their character."""
    result = await db.execute(
        select(Character)
        .options(
            selectinload(Character.position),
            selectinload(Character.equipment),
            selectinload(Character.backpack),
        )
        .where(
            Character.id == character_id,
            Character.is_deleted.is_(False),
        )
    )
    char = result.scalar_one_or_none()
    if char is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if char.user_id != user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return _build_detail_response(char)


@router.delete("/{character_id}", response_model=MessageResponse)
async def delete_character(
    character_id: str,
    user: dict = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Soft-delete a character. Only the owning user may delete their own character."""
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

    char.is_deleted = True
    await db.commit()
    return MessageResponse(message=f"Character '{char.name}' deleted")

TUTORIAL_STEPS = 5  # steps 0–4


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


@router.get("/{character_id}/tutorial-state", response_model=TutorialStateResponse)
async def get_tutorial_state(
    character_id: str,
    user: dict = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TutorialStateResponse:
    """Return the tutorial step for the character.

    None = not started (show tutorial from step 0).
    0–4  = last completed step index.
    -1   = tutorial completed or skipped.
    """
    char = await _get_own_character(character_id, user, db)
    return TutorialStateResponse(tutorial_step=char.tutorial_step)


@router.post("/{character_id}/tutorial-step/{step}", response_model=TutorialStateResponse)
async def advance_tutorial_step(
    character_id: str,
    step: int,
    user: dict = Depends(_get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TutorialStateResponse:
    """Mark a tutorial step as complete or skip the tutorial entirely (-1).

    Accepts step 0–4 (mark that step done) or -1 (skip/complete).
    Only advances — cannot regress the tutorial state.
    """
    if step not in range(TUTORIAL_STEPS) and step != -1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"step must be 0–{TUTORIAL_STEPS - 1} or -1 (skip)",
        )
    char = await _get_own_character(character_id, user, db)

    current = char.tutorial_step
    if current == -1:
        # Already done/skipped — idempotent
        return TutorialStateResponse(tutorial_step=current)

    # Only advance (or allow skip at any time)
    if step == -1 or current is None or step > current:
        char.tutorial_step = step
        await db.commit()

    return TutorialStateResponse(tutorial_step=char.tutorial_step)
