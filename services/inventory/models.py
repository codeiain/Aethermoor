"""SQLAlchemy ORM models for the AETHERMOOR Inventory Service."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ItemType(str, enum.Enum):
    WEAPON = "weapon"
    ARMOUR = "armour"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    MISC = "misc"


class ItemRarity(str, enum.Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class EquipmentSlot(str, enum.Enum):
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    AMULET = "amulet"


class Item(Base):
    """Master item catalogue — defines every item type in the game."""

    __tablename__ = "item_catalogue"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    type: Mapped[ItemType] = mapped_column(
        Enum(ItemType, name="item_type_enum"), nullable=False
    )
    rarity: Mapped[ItemRarity] = mapped_column(
        Enum(ItemRarity, name="item_rarity_enum"),
        nullable=False,
        default=ItemRarity.COMMON,
    )
    stackable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    max_stack: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    stats: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    equippable_slot: Mapped[str | None] = mapped_column(String(32), nullable=True)


class InventoryItem(Base):
    """One stack of items in a character's inventory (backpack or equipped)."""

    __tablename__ = "inventory_items"
    __table_args__ = (
        # At most one item per character per equipment slot.
        # NULL equipped_slot values are always distinct in PG unique constraints.
        UniqueConstraint("character_id", "equipped_slot", name="uq_character_equipped_slot"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    character_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    item_id: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # Backpack slot 0-23. Null when the item is equipped.
    slot_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Equipment slot name. Null when the item is in the backpack.
    equipped_slot: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
