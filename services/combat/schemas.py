"""Pydantic request/response schemas for the AETHERMOOR Combat Service."""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────

class ActionType(str, Enum):
    ATTACK = "attack"
    FLEE = "flee"
    ITEM = "item"       # Reserved — Phase 2
    SPELL = "spell"     # Reserved — Phase 2


class CombatStatus(str, Enum):
    ACTIVE = "active"
    PLAYER_WON = "player_won"
    PLAYER_FLED = "player_fled"
    PLAYER_DIED = "player_died"


# ── Combatant schemas ────────────────────────────────────────────────────────

class CombatantStats(BaseModel):
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10


class Combatant(BaseModel):
    id: str
    name: str
    is_player: bool
    character_class: str = "Fighter"
    level: int = 1
    hp: int
    max_hp: int
    ac: int
    weapon: str = "longsword"
    stats: CombatantStats = Field(default_factory=CombatantStats)
    conditions: list[dict[str, Any]] = Field(default_factory=list)
    # NPC-specific
    cr: float = 1.0
    gold_drop_min: int = 0
    gold_drop_max: int = 0


class InitiativeEntry(BaseModel):
    combatant_id: str
    initiative: int
    raw_roll: int


# ── Combat state (stored in Redis) ───────────────────────────────────────────

class CombatAction(BaseModel):
    round: int
    acting_id: str
    action_type: str
    target_id: str | None = None
    roll_result: dict[str, Any] | None = None
    description: str = ""


class CombatState(BaseModel):
    id: str
    zone_id: str
    status: CombatStatus = CombatStatus.ACTIVE
    round: int = 1
    turn_order: list[str] = Field(default_factory=list)
    current_turn_index: int = 0
    combatants: dict[str, Combatant] = Field(default_factory=dict)
    initiative_rolls: dict[str, InitiativeEntry] = Field(default_factory=dict)
    action_log: list[CombatAction] = Field(default_factory=list)
    xp_awarded: int = 0
    gold_awarded: int = 0
    # IDs for database logging
    player_character_id: str = ""
    npc_template_id: str = ""


# ── Request schemas ──────────────────────────────────────────────────────────

class StartCombatRequest(BaseModel):
    """Called by world service or client to initiate combat."""
    character_id: str
    character_name: str
    character_class: str
    character_level: int
    character_hp: int
    character_max_hp: int
    character_ac: int
    character_weapon: str = "longsword"
    character_stats: CombatantStats = Field(default_factory=CombatantStats)
    npc_template_id: str
    npc_name: str
    npc_hp: int
    npc_max_hp: int
    npc_ac: int
    npc_weapon: str = "claws"
    npc_cr: float = 1.0
    npc_stats: CombatantStats = Field(default_factory=CombatantStats)
    npc_gold_drop_min: int = 0
    npc_gold_drop_max: int = 10
    zone_id: str


class SubmitActionRequest(BaseModel):
    character_id: str
    action_type: ActionType = ActionType.ATTACK
    target_id: str | None = None  # defaults to the NPC


# ── Response schemas ─────────────────────────────────────────────────────────

class CombatStateResponse(BaseModel):
    combat_id: str
    status: CombatStatus
    round: int
    turn_order: list[str]
    current_turn_id: str | None
    combatants: dict[str, Combatant]
    last_actions: list[CombatAction]
    xp_awarded: int
    gold_awarded: int
    message: str = ""


class StartCombatResponse(BaseModel):
    combat_id: str
    status: CombatStatus
    round: int
    turn_order: list[str]
    current_turn_id: str | None
    combatants: dict[str, Combatant]
    initiative_rolls: dict[str, InitiativeEntry]
    message: str = ""


class ActionResponse(BaseModel):
    combat_id: str
    status: CombatStatus
    round: int
    current_turn_id: str | None
    combatants: dict[str, Combatant]
    action_result: CombatAction
    npc_action: CombatAction | None = None
    message: str = ""
    xp_awarded: int = 0
    gold_awarded: int = 0
