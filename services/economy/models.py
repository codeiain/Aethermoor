"""SQLAlchemy ORM models for the economy service."""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class CharacterGold(Base):
    """Tracks each character's current gold balance."""
    __tablename__ = "character_gold"

    character_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    balance: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ListingStatus(str, enum.Enum):
    ACTIVE = "active"
    SOLD = "sold"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ListingCategory(str, enum.Enum):
    WEAPON = "weapon"
    ARMOUR = "armour"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    MISC = "misc"


class Listing(Base):
    """Auction house listing — one item stack offered at a fixed price."""
    __tablename__ = "marketplace_listings"
    __table_args__ = (
        Index("ix_listings_status_expires", "status", "expires_at"),
        Index("ix_listings_seller", "seller_character_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    seller_character_id: Mapped[str] = mapped_column(String(36), nullable=False)
    item_id: Mapped[str] = mapped_column(String(64), nullable=False)
    item_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    category: Mapped[ListingCategory] = mapped_column(
        Enum(ListingCategory, name="listing_category_enum"), nullable=False,
        default=ListingCategory.MISC,
    )
    level_required: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, name="listing_status_enum"), nullable=False,
        default=ListingStatus.ACTIVE, index=True,
    )
    buyer_character_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    ah_fee_paid: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TransactionType(str, enum.Enum):
    GOLD_AWARD = "gold_award"
    GOLD_DEDUCT = "gold_deduct"
    LISTING_SOLD = "listing_sold"
    LISTING_PURCHASED = "listing_purchased"
    LISTING_CANCELLED = "listing_cancelled"
    AH_FEE = "ah_fee"
    GOLD_DROP = "gold_drop"


class Transaction(Base):
    """Immutable audit record for every gold movement."""
    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_transactions_character_created", "character_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    character_id: Mapped[str] = mapped_column(String(36), nullable=False)
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="transaction_type_enum"), nullable=False
    )
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=False)
    related_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    description: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
