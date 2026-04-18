"""Inventory service HTTP endpoints for AETHERMOOR."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth_client import AuthVerificationError, verify_user_jwt
from database import get_db
from models import EquipmentSlot, InventoryItem, Item, ItemType
from schemas import (
    ALL_EQUIPMENT_SLOTS,
    BACKPACK_SIZE,
    DropRequest,
    EquipRequest,
    InventoryItemResponse,
    InventoryResponse,
    ItemResponse,
    LootRequest,
    LootResponse,
    MessageResponse,
    UnequipRequest,
    UseRequest,
    UseResponse,
)
from zero_trust import require_service_token

logger = logging.getLogger("inventory")
router = APIRouter(prefix="/inventory", tags=["inventory"])
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

def _item_to_response(item: Item) -> ItemResponse:
    return ItemResponse(
        id=item.id,
        name=item.name,
        type=item.type,
        rarity=item.rarity,
        stackable=item.stackable,
        max_stack=item.max_stack,
        stats=item.stats,
        description=item.description,
        equippable_slot=item.equippable_slot,
    )


def _inv_item_to_response(inv: InventoryItem, item: Item) -> InventoryItemResponse:
    return InventoryItemResponse(
        id=inv.id,
        item_id=inv.item_id,
        quantity=inv.quantity,
        slot_index=inv.slot_index,
        equipped_slot=inv.equipped_slot,
        item=_item_to_response(item),
    )


async def _load_catalogue(db: AsyncSession, item_ids: set[str]) -> dict[str, Item]:
    if not item_ids:
        return {}
    result = await db.execute(select(Item).where(Item.id.in_(item_ids)))
    return {row.id: row for row in result.scalars().all()}


def _compute_equipped_stats(
    equipped: dict[str, Optional[InventoryItemResponse]],
) -> dict[str, int | float]:
    totals: dict[str, int | float] = {}
    for inv_item in equipped.values():
        if inv_item is None:
            continue
        for stat, val in inv_item.item.stats.items():
            if isinstance(val, (int, float)):
                totals[stat] = totals.get(stat, 0) + val
    return totals


def _find_free_backpack_slot(used_slots: set[int]) -> Optional[int]:
    for i in range(BACKPACK_SIZE):
        if i not in used_slots:
            return i
    return None


async def _get_char_inventory(
    db: AsyncSession, character_id: str
) -> tuple[list[InventoryItem], dict[str, Item]]:
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.character_id == character_id)
    )
    inv_items = result.scalars().all()
    catalogue = await _load_catalogue(db, {i.item_id for i in inv_items})
    return list(inv_items), catalogue


def _build_inventory_response(
    character_id: str,
    inv_items: list[InventoryItem],
    catalogue: dict[str, Item],
) -> InventoryResponse:
    backpack: list[Optional[InventoryItemResponse]] = [None] * BACKPACK_SIZE
    equipment: dict[str, Optional[InventoryItemResponse]] = {s: None for s in ALL_EQUIPMENT_SLOTS}

    for inv in inv_items:
        item = catalogue.get(inv.item_id)
        if item is None:
            continue
        resp = _inv_item_to_response(inv, item)
        if inv.equipped_slot is not None:
            equipment[inv.equipped_slot] = resp
        elif inv.slot_index is not None and 0 <= inv.slot_index < BACKPACK_SIZE:
            backpack[inv.slot_index] = resp

    equipped_stats = _compute_equipped_stats(equipment)
    return InventoryResponse(
        character_id=character_id,
        backpack=backpack,
        equipment=equipment,
        equipped_stats=equipped_stats,
    )


# ── Item catalogue endpoint ────────────────────────────────────────────────────

@router.get("/items", response_model=list[ItemResponse])
async def list_items(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_service_token),
) -> list[ItemResponse]:
    """Return the full item catalogue. Requires service token."""
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return [_item_to_response(i) for i in items]


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(_current_user),
) -> ItemResponse:
    """Get a single item from the catalogue."""
    item = await db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item '{item_id}' not found")
    return _item_to_response(item)


# ── Player inventory ───────────────────────────────────────────────────────────

@router.get("/{character_id}", response_model=InventoryResponse)
async def get_inventory(
    character_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(_current_user),
) -> InventoryResponse:
    """Return the full inventory for a character (backpack + equipment)."""
    inv_items, catalogue = await _get_char_inventory(db, character_id)
    return _build_inventory_response(character_id, inv_items, catalogue)


@router.post("/{character_id}/equip", response_model=InventoryResponse)
async def equip_item(
    character_id: str,
    body: EquipRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(_current_user),
) -> InventoryResponse:
    """Equip a backpack item to an equipment slot. Swaps if slot is occupied."""
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.id == body.inventory_item_id,
            InventoryItem.character_id == character_id,
        )
    )
    inv = result.scalar_one_or_none()
    if inv is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    if inv.equipped_slot is not None:
        raise HTTPException(status_code=400, detail="Item is already equipped")

    item = await db.get(Item, inv.item_id)
    if item is None:
        raise HTTPException(status_code=500, detail="Item catalogue entry missing")

    target_slot = body.slot.value
    if item.equippable_slot != target_slot:
        raise HTTPException(
            status_code=400,
            detail=f"Item goes in '{item.equippable_slot}', not '{target_slot}'",
        )

    result2 = await db.execute(
        select(InventoryItem).where(
            InventoryItem.character_id == character_id,
            InventoryItem.equipped_slot == target_slot,
        )
    )
    existing_equipped = result2.scalar_one_or_none()

    if existing_equipped is not None:
        # Swap: move existing item back to the slot being vacated
        existing_equipped.equipped_slot = None
        existing_equipped.slot_index = inv.slot_index

    inv.slot_index = None
    inv.equipped_slot = target_slot
    await db.commit()

    inv_items, catalogue = await _get_char_inventory(db, character_id)
    return _build_inventory_response(character_id, inv_items, catalogue)


@router.post("/{character_id}/unequip", response_model=InventoryResponse)
async def unequip_item(
    character_id: str,
    body: UnequipRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(_current_user),
) -> InventoryResponse:
    """Move an equipped item back to the backpack."""
    slot_name = body.slot.value
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.character_id == character_id,
            InventoryItem.equipped_slot == slot_name,
        )
    )
    inv = result.scalar_one_or_none()
    if inv is None:
        raise HTTPException(status_code=404, detail=f"Nothing equipped in slot '{slot_name}'")

    result2 = await db.execute(
        select(InventoryItem).where(
            InventoryItem.character_id == character_id,
            InventoryItem.slot_index.is_not(None),
        )
    )
    backpack_items = result2.scalars().all()
    used_slots = {i.slot_index for i in backpack_items if i.slot_index is not None}
    free_slot = _find_free_backpack_slot(used_slots)

    if free_slot is None:
        raise HTTPException(status_code=400, detail="Backpack is full")

    inv.equipped_slot = None
    inv.slot_index = free_slot
    await db.commit()

    inv_items, catalogue = await _get_char_inventory(db, character_id)
    return _build_inventory_response(character_id, inv_items, catalogue)


@router.post("/{character_id}/drop", response_model=MessageResponse)
async def drop_item(
    character_id: str,
    body: DropRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(_current_user),
) -> MessageResponse:
    """Drop (destroy) some or all of an inventory item stack."""
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.id == body.inventory_item_id,
            InventoryItem.character_id == character_id,
        )
    )
    inv = result.scalar_one_or_none()
    if inv is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if body.quantity >= inv.quantity:
        await db.delete(inv)
    else:
        inv.quantity -= body.quantity
    await db.commit()
    return MessageResponse(message=f"Dropped {body.quantity}x {inv.item_id}")


@router.post("/{character_id}/use", response_model=UseResponse)
async def use_item(
    character_id: str,
    body: UseRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(_current_user),
) -> UseResponse:
    """Use a consumable item. Decrements the stack; returns the item's effects."""
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.id == body.inventory_item_id,
            InventoryItem.character_id == character_id,
        )
    )
    inv = result.scalar_one_or_none()
    if inv is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    item = await db.get(Item, inv.item_id)
    if item is None:
        raise HTTPException(status_code=500, detail="Item catalogue entry missing")

    if item.type != ItemType.CONSUMABLE:
        raise HTTPException(status_code=400, detail=f"'{item.name}' is not a consumable")

    remaining = inv.quantity - 1
    if remaining <= 0:
        await db.delete(inv)
        remaining = 0
    else:
        inv.quantity = remaining
    await db.commit()

    return UseResponse(
        inventory_item_id=body.inventory_item_id,
        item_id=inv.item_id,
        quantity_remaining=remaining,
        effects=item.stats,
    )


# ── Loot (service-to-service) ─────────────────────────────────────────────────

@router.post("/loot", response_model=LootResponse)
async def award_loot(
    body: LootRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_service_token),
) -> LootResponse:
    """Award an item to a character. Called by combat/quest services.

    Priority: stack onto existing backpack stack → auto-equip empty slot → backpack → reject.
    """
    item = await db.get(Item, body.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item '{body.item_id}' not found in catalogue")

    # Load current inventory
    inv_result = await db.execute(
        select(InventoryItem).where(InventoryItem.character_id == body.character_id)
    )
    inv_items = inv_result.scalars().all()

    equipped_slots_used = {i.equipped_slot for i in inv_items if i.equipped_slot is not None}
    backpack_slots_used = {i.slot_index for i in inv_items if i.slot_index is not None}

    # 1. Stackable: try to merge onto existing backpack stack
    if item.stackable:
        for inv in inv_items:
            if inv.item_id == body.item_id and inv.slot_index is not None:
                space = item.max_stack - inv.quantity
                if space > 0:
                    add = min(body.quantity, space)
                    inv.quantity += add
                    await db.commit()
                    return LootResponse(
                        character_id=body.character_id,
                        item_id=body.item_id,
                        quantity=add,
                        result="stacked",
                        inventory_item_id=inv.id,
                        slot_type="backpack",
                        slot_value=inv.slot_index,
                    )

    # 2. Non-stackable or no existing stack: auto-equip if slot empty
    if item.equippable_slot and item.equippable_slot not in equipped_slots_used:
        new_inv = InventoryItem(
            character_id=body.character_id,
            item_id=body.item_id,
            quantity=1,
            equipped_slot=item.equippable_slot,
            slot_index=None,
        )
        db.add(new_inv)
        await db.commit()
        await db.refresh(new_inv)
        return LootResponse(
            character_id=body.character_id,
            item_id=body.item_id,
            quantity=1,
            result="equipped",
            inventory_item_id=new_inv.id,
            slot_type="equipped",
            slot_value=item.equippable_slot,
        )

    # 3. Place in backpack
    free_slot = _find_free_backpack_slot(backpack_slots_used)
    if free_slot is None:
        return LootResponse(
            character_id=body.character_id,
            item_id=body.item_id,
            quantity=body.quantity,
            result="rejected",
            inventory_item_id=None,
            slot_type=None,
            slot_value=None,
        )

    new_inv = InventoryItem(
        character_id=body.character_id,
        item_id=body.item_id,
        quantity=body.quantity,
        slot_index=free_slot,
        equipped_slot=None,
    )
    db.add(new_inv)
    await db.commit()
    await db.refresh(new_inv)
    return LootResponse(
        character_id=body.character_id,
        item_id=body.item_id,
        quantity=body.quantity,
        result="backpack",
        inventory_item_id=new_inv.id,
        slot_type="backpack",
        slot_value=free_slot,
    )
