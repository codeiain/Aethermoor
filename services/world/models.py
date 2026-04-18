"""SQLAlchemy ORM models for the world service.

Postgres is the source of truth for zone definitions, NPC templates, and world
events. Redis holds ephemeral real-time state (player positions, NPC runtime
state, zone counts) — see cache.py.
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Biome(str, enum.Enum):
    FOREST = "forest"
    DUNGEON = "dungeon"
    TOWN = "town"
    COAST = "coast"
    MOUNTAIN = "mountain"
    SWAMP = "swamp"
    DESERT = "desert"


class EventType(str, enum.Enum):
    SCHEDULED = "scheduled"
    TRIGGERED = "triggered"


class Zone(Base):
    """A discrete area of the game world (overworld zone, dungeon floor, town, etc.)."""

    __tablename__ = "zones"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # slug e.g. "starter_town"
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    biome: Mapped[Biome] = mapped_column(Enum(Biome, name="biome_enum"), nullable=False)
    level_min: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    level_max: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=99)
    max_players: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    # Tile dimensions
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    # Default spawn coordinates for players entering this zone
    spawn_x: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    spawn_y: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Phaser.js / Tiled JSON tilemap stored as JSONB for efficient querying
    tilemap: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    npc_templates: Mapped[list["NpcTemplate"]] = relationship(
        back_populates="zone", cascade="all, delete-orphan"
    )
    events: Mapped[list["WorldEvent"]] = relationship(
        back_populates="zone", cascade="all, delete-orphan"
    )


class NpcTemplate(Base):
    """Persistent definition of an NPC in a zone.

    Runtime state (position, alive/dead/respawning) lives in Redis.
    This record defines the NPC's identity, combat stats, patrol route, and respawn config.
    """

    __tablename__ = "npc_templates"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    zone_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    npc_type: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. "guard", "merchant"
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    spawn_x: Mapped[int] = mapped_column(Integer, nullable=False)
    spawn_y: Mapped[int] = mapped_column(Integer, nullable=False)
    # Ordered list of (x, y) patrol waypoints as JSON: [{"x": 5, "y": 3}, ...]
    patrol_path: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    respawn_timer_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ── Combat stats ──────────────────────────────────────────────────────────
    # HP resets to max_hp at each respawn; combat service owns HP during a fight.
    hp: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    max_hp: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    ac: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    # D&D challenge rating (0.125, 0.25, 0.5, 1, 2, …)
    cr: Mapped[float] = mapped_column(Float, nullable=False, default=0.25)
    # Weapon type string matching combat service WeaponType enum
    weapon: Mapped[str] = mapped_column(String(32), nullable=False, default="claws")
    # D&D ability scores: {"strength": 10, "dexterity": 10, ...}
    npc_stats: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    gold_drop_min: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gold_drop_max: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    # False for friendly NPCs (merchants, guards); True for monsters
    is_hostile: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Optional dialogue tree: {"greeting": "...", "farewell": "...", "quest_giver_id": "..."}
    dialogue: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)

    zone: Mapped["Zone"] = relationship(back_populates="npc_templates")


class WorldEvent(Base):
    """A world event: either scheduled (time-based) or triggered (manual/condition).

    Examples: "Dragon Siege on Starter Town", "Double XP Weekend".
    """

    __tablename__ = "world_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # None means global (all zones); set to a zone_id for zone-scoped events
    zone_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("zones.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type_enum"), nullable=False
    )
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    zone: Mapped["Zone | None"] = relationship(back_populates="events")
