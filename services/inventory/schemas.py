"""Pydantic request/response schemas for the inventory service."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from models import EquipmentSlot, ItemRarity, ItemType

BACKPACK_SIZE = 24
ALL_EQUIPMENT_SLOTS = [s.value for s in EquipmentSlot]


# ── Item catalogue ────────────────────────────────────────────────────────────

class ItemResponse(BaseModel):
    id: str
    name: str
    type: ItemType
    rarity: ItemRarity
    stackable: bool
    max_stack: int
    stats: dict[str, Any]
    description: str
    equippable_slot: Optional[str]


# ── Inventory items ───────────────────────────────────────────────────────────

class InventoryItemResponse(BaseModel):
    id: str
    item_id: str
    quantity: int
    slot_index: Optional[int]
    equipped_slot: Optional[str]
    item: ItemResponse


# ── Full inventory view ───────────────────────────────────────────────────────

class InventoryResponse(BaseModel):
    character_id: str
    # Backpack: list of 24 slots, None = empty slot
    backpack: list[Optional[InventoryItemResponse]]
    # Equipment: slot name → item (None = empty)
    equipment: dict[str, Optional[InventoryItemResponse]]
    # Sum of all equipped item stats
    equipped_stats: dict[str, Any]


# ── Action requests ───────────────────────────────────────────────────────────

class EquipRequest(BaseModel):
    inventory_item_id: str
    slot: EquipmentSlot


class UnequipRequest(BaseModel):
    slot: EquipmentSlot


class DropRequest(BaseModel):
    inventory_item_id: str
    quantity: int = Field(ge=1, default=1)


class UseRequest(BaseModel):
    inventory_item_id: str


# ── Loot ─────────────────────────────────────────────────────────────────────

class LootRequest(BaseModel):
    character_id: str
    item_id: str
    quantity: int = Field(ge=1, default=1)


class LootResponse(BaseModel):
    character_id: str
    item_id: str
    quantity: int
    result: str  # "equipped" | "backpack" | "stacked" | "rejected"
    inventory_item_id: Optional[str]
    slot_type: Optional[str]  # "equipped" | "backpack"
    slot_value: Optional[str | int]  # slot name or slot index


# ── Use consumable response ───────────────────────────────────────────────────

class UseResponse(BaseModel):
    inventory_item_id: str
    item_id: str
    quantity_remaining: int
    effects: dict[str, Any]


# ── Generic ───────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
