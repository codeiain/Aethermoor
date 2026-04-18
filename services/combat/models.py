"""SQLAlchemy ORM models for the AETHERMOOR Combat Service."""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class CombatOutcome(str, enum.Enum):
    PLAYER_WON = "player_won"
    PLAYER_FLED = "player_fled"
    PLAYER_DIED = "player_died"


class CombatLog(Base):
    """Persisted record of a completed combat encounter."""

    __tablename__ = "combat_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Cross-service references — no DB-level FK (cross-service ownership)
    player_character_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    npc_template_id: Mapped[str] = mapped_column(String(128), nullable=False)
    zone_id: Mapped[str] = mapped_column(String(36), nullable=False)
    outcome: Mapped[CombatOutcome] = mapped_column(
        Enum(CombatOutcome, name="combat_outcome_enum"), nullable=False
    )
    rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    xp_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gold_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    npc_cr: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class CombatActionLog(Base):
    """Persisted record of an individual action within a combat."""

    __tablename__ = "combat_action_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    combat_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    acting_entity: Mapped[str] = mapped_column(String(36), nullable=False)
    action_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target_entity: Mapped[str | None] = mapped_column(String(36), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    damage_dealt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
