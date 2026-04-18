"""Pydantic request/response schemas for the quest service."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from models import QuestStatus


# ── Quest catalogue ────────────────────────────────────────────────────────────

class QuestResponse(BaseModel):
    id: str
    title: str
    npc_giver: str
    briefing_dialogue: str
    objectives_template: list[dict[str, Any]]
    completion_dialogue: str
    xp_reward: int
    gold_reward: int
    item_reward: Optional[str]
    item_reward_qty: int
    prerequisites: list[str]
    is_active: bool


# ── Character quest state ──────────────────────────────────────────────────────

class ObjectiveProgress(BaseModel):
    type: str
    required: int
    current: int
    # Optional target fields depending on type
    target: Optional[str] = None
    item_id: Optional[str] = None
    npc_id: Optional[str] = None
    zone_id: Optional[str] = None
    met: bool


class CharacterQuestResponse(BaseModel):
    id: str
    character_id: str
    quest_id: str
    quest_title: str
    status: QuestStatus
    objectives: list[dict[str, Any]]
    xp_reward: int
    gold_reward: int
    item_reward: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]


class CharacterQuestsResponse(BaseModel):
    character_id: str
    active: list[CharacterQuestResponse]
    completed: list[CharacterQuestResponse]


# ── Progress update (internal) ─────────────────────────────────────────────────

class ProgressUpdate(BaseModel):
    """Progress event fired by world/combat services."""
    type: str = Field(..., description="kill_count | item_gather | interact_npc | explore_location")
    target: Optional[str] = Field(None, description="NPC type for kill_count")
    item_id: Optional[str] = Field(None, description="Item ID for item_gather")
    npc_id: Optional[str] = Field(None, description="NPC ID for interact_npc")
    zone_id: Optional[str] = Field(None, description="Zone ID for explore_location")
    amount: int = Field(1, ge=1)


class ProgressResponse(BaseModel):
    updated_quests: list[str]
    newly_ready: list[str]


# ── Reward result ──────────────────────────────────────────────────────────────

class CompleteQuestResponse(BaseModel):
    quest_id: str
    quest_title: str
    xp_awarded: int
    gold_awarded: int
    item_awarded: Optional[str]
    message: str


# ── NPC dialogue ───────────────────────────────────────────────────────────────

class DialogueOption(BaseModel):
    quest_id: str
    quest_title: str
    type: str  # "offer" | "in_progress" | "ready_to_complete" | "completed"
    dialogue: str


class NpcDialogueResponse(BaseModel):
    npc_id: str
    options: list[DialogueOption]


# ── Generic ────────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
