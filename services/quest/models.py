"""SQLAlchemy ORM models for the quest service."""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class QuestType(str, enum.Enum):
    KILL_COUNT = "kill_count"
    ITEM_GATHER = "item_gather"
    INTERACT_NPC = "interact_npc"
    EXPLORE_LOCATION = "explore_location"


class QuestStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    READY_TO_COMPLETE = "ready_to_complete"
    COMPLETED = "completed"


class Quest(Base):
    """Master quest catalogue. Each row is a quest definition."""

    __tablename__ = "quests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    npc_giver: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    briefing_dialogue: Mapped[str] = mapped_column(Text, nullable=False)
    # objectives_template: list of objective dicts defining the quest goals.
    # Each dict: {"type": QuestType, "target"/"item_id"/"npc_id"/"zone_id": str, "required": int}
    objectives_template: Mapped[list] = mapped_column(JSONB, nullable=False)
    completion_dialogue: Mapped[str] = mapped_column(Text, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gold_reward: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Optional single item reward — item_id from inventory catalogue
    item_reward: Mapped[str | None] = mapped_column(String(64), nullable=True)
    item_reward_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # Ordered list of quest IDs that must be completed before this quest is available
    prerequisites: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    character_quests: Mapped[list["CharacterQuest"]] = relationship(
        back_populates="quest", cascade="all, delete-orphan"
    )


class CharacterQuest(Base):
    """Per-character quest state. One row per (character, quest) pair once accepted."""

    __tablename__ = "character_quests"
    __table_args__ = (
        UniqueConstraint("character_id", "quest_id", name="uq_char_quest"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    character_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    quest_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("quests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[QuestStatus] = mapped_column(
        Enum(QuestStatus, name="quest_status_enum"), nullable=False, default=QuestStatus.IN_PROGRESS
    )
    # Runtime copy of objectives_template with current progress added.
    # Each dict: {...template fields..., "current": int}
    objectives: Mapped[list] = mapped_column(JSONB, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    quest: Mapped["Quest"] = relationship(back_populates="character_quests")
