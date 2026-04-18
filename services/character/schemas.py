"""Pydantic request and response schemas for the player/character service."""
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from models import CharacterClass, EquipmentSlotName

_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9 '-]{1,62}[a-zA-Z0-9]$")


# ── Requests ──────────────────────────────────────────────────────────────────

class CreateCharacterRequest(BaseModel):
    name: str
    character_class: CharacterClass
    slot: int  # 1–3

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not (3 <= len(v) <= 64):
            raise ValueError("Character name must be 3–64 characters")
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9 '\-]*$", v):
            raise ValueError("Character name must start with a letter and contain only letters, digits, spaces, apostrophes, or hyphens")
        return v

    @field_validator("slot")
    @classmethod
    def validate_slot(cls, v: int) -> int:
        if v not in (1, 2, 3):
            raise ValueError("Character slot must be 1, 2, or 3")
        return v


class UpdatePositionRequest(BaseModel):
    zone_id: str
    x: int
    y: int
    respawn_zone_id: Optional[str] = None
    respawn_x: Optional[int] = None
    respawn_y: Optional[int] = None


class UpdateStatsRequest(BaseModel):
    current_hp: Optional[int] = None
    max_hp: Optional[int] = None
    xp: Optional[int] = None
    gold: Optional[int] = None
    # Delta fields: applied as additions to current values (used by quest service)
    xp_delta: Optional[int] = None
    gold_delta: Optional[int] = None


# ── Responses ─────────────────────────────────────────────────────────────────

class AbilityScores(BaseModel):
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int


class PositionResponse(BaseModel):
    zone_id: str
    x: int
    y: int
    respawn_zone_id: str
    respawn_x: int
    respawn_y: int
    last_seen: datetime


class EquipmentSlotResponse(BaseModel):
    slot_name: EquipmentSlotName
    item_id: Optional[str]


class BackpackItemResponse(BaseModel):
    slot_index: int
    item_id: Optional[str]
    quantity: int


class CharacterSummaryResponse(BaseModel):
    id: str
    slot: int
    name: str
    character_class: CharacterClass
    level: int
    xp: int
    current_hp: int
    max_hp: int
    gold: int
    created_at: datetime
    updated_at: datetime


class CharacterDetailResponse(BaseModel):
    id: str
    user_id: str
    slot: int
    name: str
    character_class: CharacterClass
    ability_scores: AbilityScores
    level: int
    xp: int
    current_hp: int
    max_hp: int
    gold: int
    position: Optional[PositionResponse]
    equipment: list[EquipmentSlotResponse]
    backpack: list[BackpackItemResponse]
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    message: str


class TutorialStateResponse(BaseModel):
    """Current tutorial progress for a character."""
    tutorial_step: Optional[int]  # None = not started, 0-4 = last completed step, -1 = done/skipped


# ── Crafting (internal use) ───────────────────────────────────────────────────

class BackpackItemQuantity(BaseModel):
    """Item + quantity pair used in craft apply requests."""
    item_id: str
    quantity: int


class ApplyCraftRequest(BaseModel):
    """Atomically deduct materials and add crafted result. Called by crafting service."""
    items_to_remove: list[BackpackItemQuantity]
    items_to_add: list[BackpackItemQuantity]


class BackpackResponse(BaseModel):
    items: list[BackpackItemResponse]


class CombatStatsResponse(BaseModel):
    """Character stats needed to start a combat session. Internal use only."""
    character_id: str
    name: str
    character_class: str
    level: int
    current_hp: int
    max_hp: int
    ac: int       # 10 + DEX modifier (unarmored base)
    weapon: str   # derived from main_hand equipment slot item_id
    stats: AbilityScores
