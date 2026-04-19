"""SQLAlchemy ORM models for the player/character service."""
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
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class CharacterClass(str, enum.Enum):
    FIGHTER = "Fighter"
    WIZARD = "Wizard"
    ROGUE = "Rogue"
    CLERIC = "Cleric"
    RANGER = "Ranger"
    PALADIN = "Paladin"


class EquipmentSlotName(str, enum.Enum):
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    AMULET = "amulet"


class Character(Base):
    __tablename__ = "characters"
    __table_args__ = (
        UniqueConstraint("user_id", "slot", name="uq_character_user_slot"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # user_id references the auth service's users.id — no DB-level FK (cross-service)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    slot: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1–3
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    character_class: Mapped[CharacterClass] = mapped_column(
        Enum(CharacterClass, name="character_class_enum"), nullable=False
    )
    # D&D ability scores
    strength: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dexterity: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    constitution: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    intelligence: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    wisdom: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    charisma: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    # HP
    max_hp: Mapped[int] = mapped_column(Integer, nullable=False)
    current_hp: Mapped[int] = mapped_column(Integer, nullable=False)
    # Progression
    xp: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    # Economy
    gold: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    # Tutorial progress: NULL = not started, 0-4 = last completed step index, -1 = skipped/done
    tutorial_step: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, default=None)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    position: Mapped["CharacterPosition"] = relationship(
        back_populates="character", uselist=False, cascade="all, delete-orphan"
    )
    equipment: Mapped[list["EquipmentSlot"]] = relationship(
        back_populates="character", cascade="all, delete-orphan"
    )
    backpack: Mapped[list["BackpackItem"]] = relationship(
        back_populates="character", cascade="all, delete-orphan"
    )
    player_skills: Mapped["PlayerSkills"] = relationship(
        back_populates="character", uselist=False, cascade="all, delete-orphan"
    )


class CharacterPosition(Base):
    __tablename__ = "character_positions"

    character_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True
    )
    zone_id: Mapped[str] = mapped_column(String(64), nullable=False, default="starter_town")
    x: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    y: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    respawn_zone_id: Mapped[str] = mapped_column(
        String(64), nullable=False, default="starter_town"
    )
    respawn_x: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    respawn_y: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    character: Mapped["Character"] = relationship(back_populates="position")


class EquipmentSlot(Base):
    __tablename__ = "equipment_slots"
    __table_args__ = (
        UniqueConstraint("character_id", "slot_name", name="uq_equipment_char_slot"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    character_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slot_name: Mapped[EquipmentSlotName] = mapped_column(
        Enum(EquipmentSlotName, name="equipment_slot_enum"), nullable=False
    )
    # item_id references item registry (future service) — stored as opaque string for now
    item_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    character: Mapped["Character"] = relationship(back_populates="equipment")


class BackpackItem(Base):
    __tablename__ = "backpack_items"
    __table_args__ = (
        UniqueConstraint("character_id", "slot_index", name="uq_backpack_char_slot"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    character_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slot_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0–23
    item_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    character: Mapped["Character"] = relationship(back_populates="backpack")


class PlayerSkills(Base):
    """Tracks per-character skill tree state: which skills are unlocked and TP spent."""

    __tablename__ = "player_skills"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    character_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    # JSON-encoded list of unlocked skill IDs, e.g. '["taunt","shield_mastery"]'
    unlocked_skills_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    talent_points_spent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_respec_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    character: Mapped["Character"] = relationship(back_populates="player_skills")
