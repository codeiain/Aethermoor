"""Pydantic request/response schemas for the economy service."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from models import ListingCategory, ListingStatus, TransactionType


# ── Gold ──────────────────────────────────────────────────────────────────────

class GoldBalanceResponse(BaseModel):
    character_id: str
    balance: int


class GoldAwardRequest(BaseModel):
    character_id: str
    amount: int = Field(gt=0)
    description: str = "Gold awarded"
    related_id: Optional[str] = None


class GoldDeductRequest(BaseModel):
    character_id: str
    amount: int = Field(gt=0)
    description: str = "Gold deducted"
    related_id: Optional[str] = None


class GoldDropRequest(BaseModel):
    character_id: str
    monster_id: str
    monster_name: str = "monster"


class GoldOperationResponse(BaseModel):
    character_id: str
    amount: int
    balance_after: int
    description: str


# ── Listings ──────────────────────────────────────────────────────────────────

class CreateListingRequest(BaseModel):
    character_id: str
    item_id: str
    item_name: str = Field(max_length=128)
    quantity: int = Field(gt=0)
    unit_price: int = Field(gt=0)
    category: ListingCategory = ListingCategory.MISC
    level_required: int = Field(ge=1, default=1)

    @field_validator("item_id")
    @classmethod
    def validate_item_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("item_id must not be empty")
        return v


class ListingResponse(BaseModel):
    id: str
    seller_character_id: str
    item_id: str
    item_name: str
    quantity: int
    unit_price: int
    total_price: int
    category: ListingCategory
    level_required: int
    status: ListingStatus
    buyer_character_id: Optional[str]
    expires_at: datetime
    created_at: datetime
    sold_at: Optional[datetime]


class BuyListingRequest(BaseModel):
    buyer_character_id: str


class BuyListingResponse(BaseModel):
    listing_id: str
    buyer_character_id: str
    seller_character_id: str
    item_id: str
    quantity: int
    total_price: int
    ah_fee: int
    seller_received: int
    buyer_balance_after: int
    seller_balance_after: int


# ── Transactions ──────────────────────────────────────────────────────────────

class TransactionResponse(BaseModel):
    id: str
    character_id: str
    type: TransactionType
    amount: int
    balance_after: int
    related_id: Optional[str]
    description: str
    created_at: datetime


# ── Admin Config ──────────────────────────────────────────────────────────────

class ConfigUpdateRequest(BaseModel):
    gold_cap: Optional[int] = Field(default=None, gt=0)
    ah_fee_pct: Optional[float] = Field(default=None, ge=0.0, le=50.0)
    listing_duration_hours: Optional[int] = Field(default=None, gt=0)
    gold_drop_min: Optional[int] = Field(default=None, ge=0)
    gold_drop_max: Optional[int] = Field(default=None, ge=0)


class ConfigResponse(BaseModel):
    gold_cap: int
    ah_fee_pct: float
    listing_duration_hours: int
    gold_drop_min: int
    gold_drop_max: int


# ── Generic ───────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
