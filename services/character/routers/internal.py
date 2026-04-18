"""Internal service-to-service endpoints (zero-trust protected).

Called by game world service, combat service, crafting service, etc. via X-Service-Token.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from dnd import xp_to_level
from models import BackpackItem, Character, CharacterPosition
from schemas import (
    AbilityScores,
    ApplyCraftRequest,
    BackpackItemQuantity,
    BackpackItemResponse,
    BackpackResponse,
    CharacterDetailResponse,
    CombatStatsResponse,
    MessageResponse,
    UpdatePositionRequest,
    UpdateStatsRequest,
)
from zero_trust import require_service_token

router = APIRouter(prefix="/players", tags=["internal"])


@router.patch(
    "/{character_id}/position",
    response_model=MessageResponse,
    dependencies=[Depends(require_service_token)],
)
async def update_position(
    character_id: str,
    body: UpdatePositionRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Update world position for a character. Internal: called by world service."""
    result = await db.execute(
        select(Character)
        .options(selectinload(Character.position))
        .where(Character.id == character_id, Character.is_deleted.is_(False))
    )
    char = result.scalar_one_or_none()
    if char is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    if char.position is None:
        pos = CharacterPosition(character_id=character_id)
        db.add(pos)
        char.position = pos
    else:
        pos = char.position

    pos.zone_id = body.zone_id
    pos.x = body.x
    pos.y = body.y
    pos.last_seen = datetime.now(timezone.utc)

    if body.respawn_zone_id is not None:
        pos.respawn_zone_id = body.respawn_zone_id
    if body.respawn_x is not None:
        pos.respawn_x = body.respawn_x
    if body.respawn_y is not None:
        pos.respawn_y = body.respawn_y

    await db.commit()
    return MessageResponse(message="Position updated")


@router.patch(
    "/{character_id}/stats",
    response_model=MessageResponse,
    dependencies=[Depends(require_service_token)],
)
async def update_stats(
    character_id: str,
    body: UpdateStatsRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Update character stats after combat. Internal: called by combat service."""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.is_deleted.is_(False),
        )
    )
    char = result.scalar_one_or_none()
    if char is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    if body.current_hp is not None:
        char.current_hp = max(0, body.current_hp)
    if body.max_hp is not None:
        char.max_hp = max(1, body.max_hp)
    if body.xp is not None:
        char.xp = max(0, body.xp)
        char.level = xp_to_level(char.xp)
    if body.gold is not None:
        char.gold = max(0, body.gold)
    if body.xp_delta is not None:
        char.xp = max(0, char.xp + body.xp_delta)
        char.level = xp_to_level(char.xp)
    if body.gold_delta is not None:
        char.gold = max(0, char.gold + body.gold_delta)

    await db.commit()
    return MessageResponse(message="Stats updated")


@router.get(
    "/{character_id}/backpack",
    response_model=BackpackResponse,
    dependencies=[Depends(require_service_token)],
)
async def get_backpack(
    character_id: str,
    db: AsyncSession = Depends(get_db),
) -> BackpackResponse:
    """Return all backpack items for a character. Internal: called by crafting service."""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.is_deleted.is_(False),
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    items_result = await db.execute(
        select(BackpackItem).where(BackpackItem.character_id == character_id)
    )
    items = items_result.scalars().all()
    return BackpackResponse(
        items=[
            BackpackItemResponse(
                slot_index=item.slot_index,
                item_id=item.item_id,
                quantity=item.quantity,
            )
            for item in items
        ]
    )


@router.post(
    "/{character_id}/backpack/apply-craft",
    response_model=MessageResponse,
    dependencies=[Depends(require_service_token)],
)
async def apply_craft(
    character_id: str,
    body: ApplyCraftRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Atomically deduct crafting materials and add crafted result.

    Internal: called exclusively by the crafting service after recipe validation.
    All mutations occur inside a single transaction — partial states are impossible.
    """
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.is_deleted.is_(False),
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    items_result = await db.execute(
        select(BackpackItem).where(BackpackItem.character_id == character_id)
    )
    backpack: list[BackpackItem] = list(items_result.scalars().all())

    # Build mutable inventory map: item_id → total quantity across all slots
    inventory: dict[str, int] = {}
    for item in backpack:
        if item.item_id:
            inventory[item.item_id] = inventory.get(item.item_id, 0) + item.quantity

    # Validate all required materials are present before mutating anything
    for req in body.items_to_remove:
        if inventory.get(req.item_id, 0) < req.quantity:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Insufficient {req.item_id}: need {req.quantity}, have {inventory.get(req.item_id, 0)}",
            )

    # Deduct materials — consume from lowest-index slots first
    for req in body.items_to_remove:
        remaining = req.quantity
        for item in sorted(backpack, key=lambda i: i.slot_index):
            if item.item_id != req.item_id or remaining <= 0:
                continue
            if item.quantity <= remaining:
                remaining -= item.quantity
                item.quantity = 0
            else:
                item.quantity -= remaining
                remaining = 0

    # Remove emptied slots from DB
    for item in backpack:
        if item.quantity <= 0:
            await db.delete(item)

    # Add crafted result — stack onto existing slot or use first free slot
    used_slots = {item.slot_index for item in backpack if item.quantity > 0}
    for add in body.items_to_add:
        # Try to stack onto an existing slot with the same item
        stacked = False
        for item in backpack:
            if item.item_id == add.item_id and item.quantity > 0:
                item.quantity += add.quantity
                stacked = True
                break
        if not stacked:
            # Find the first free slot (0–23)
            free_slot = next((s for s in range(24) if s not in used_slots), None)
            if free_slot is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Backpack is full — no free slot for crafted item",
                )
            new_item = BackpackItem(
                character_id=character_id,
                slot_index=free_slot,
                item_id=add.item_id,
                quantity=add.quantity,
            )
            db.add(new_item)
            used_slots.add(free_slot)

    await db.commit()
    return MessageResponse(message="Craft applied")


# ── Weapon derivation helper ─────────────────────────────────────────────────

_ITEM_TO_WEAPON: dict[str, str] = {
    "basic_sword": "longsword",
    "iron_sword": "longsword",
    "greatsword": "greatsword",
    "dagger": "dagger",
    "iron_dagger": "dagger",
    "handaxe": "handaxe",
    "greataxe": "greataxe",
    "shortbow": "shortbow",
    "longbow": "longbow",
    "hand_crossbow": "hand_crossbow",
    "quarterstaff": "quarterstaff",
    "iron_staff": "quarterstaff",
    "arcane_staff": "arcane_staff",
    "shortsword": "shortsword",
}


def _item_id_to_weapon(item_id: str | None) -> str:
    if item_id is None:
        return "longsword"
    weapon = _ITEM_TO_WEAPON.get(item_id)
    if weapon:
        return weapon
    lower = item_id.lower()
    for key, wtype in _ITEM_TO_WEAPON.items():
        if key in lower:
            return wtype
    return "longsword"


@router.get(
    "/{character_id}/combat-stats",
    response_model=CombatStatsResponse,
    dependencies=[Depends(require_service_token)],
)
async def get_combat_stats(
    character_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> CombatStatsResponse:
    """Return a character's combat stats for initiating a battle.

    Internal: called by the world service when a player engages an NPC.
    Validates that character_id belongs to user_id (ownership check).
    AC = 10 + DEX modifier. Weapon derived from main_hand equipment slot.
    """
    result = await db.execute(
        select(Character)
        .options(selectinload(Character.equipment))
        .where(Character.id == character_id, Character.is_deleted.is_(False))
    )
    char = result.scalar_one_or_none()
    if char is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if char.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    dex_mod = (char.dexterity - 10) // 2
    ac = 10 + dex_mod

    main_hand_item: str | None = None
    for slot in char.equipment:
        if slot.slot_name.value == "main_hand":
            main_hand_item = slot.item_id
            break
    weapon = _item_id_to_weapon(main_hand_item)

    return CombatStatsResponse(
        character_id=char.id,
        name=char.name,
        character_class=char.character_class.value,
        level=char.level,
        current_hp=char.current_hp,
        max_hp=char.max_hp,
        ac=ac,
        weapon=weapon,
        stats=AbilityScores(
            strength=char.strength,
            dexterity=char.dexterity,
            constitution=char.constitution,
            intelligence=char.intelligence,
            wisdom=char.wisdom,
            charisma=char.charisma,
        ),
    )
