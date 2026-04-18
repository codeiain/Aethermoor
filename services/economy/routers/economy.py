"""Economy endpoints: gold management, marketplace, and transaction history.

Gold internal endpoints (award/deduct/drop) require X-Service-Token.
Player-facing endpoints require a valid user JWT.
"""
import logging
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

import cache
from auth_client import AuthVerificationError, verify_user_jwt
from database import get_db
from models import CharacterGold, Listing, ListingStatus, Transaction, TransactionType
from schemas import (
    BuyListingRequest,
    BuyListingResponse,
    CreateListingRequest,
    GoldAwardRequest,
    GoldBalanceResponse,
    GoldDeductRequest,
    GoldDropRequest,
    GoldOperationResponse,
    ListingCategory,
    ListingResponse,
    MessageResponse,
    TransactionResponse,
)
from zero_trust import require_service_token

logger = logging.getLogger("economy")
router = APIRouter(prefix="/economy", tags=["economy"])
_bearer = HTTPBearer()


async def _current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    try:
        return await verify_user_jwt(credentials.credentials)
    except AuthVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def _get_or_create_gold(db: AsyncSession, character_id: str) -> CharacterGold:
    """Fetch the gold record for a character, creating it at 0 if absent."""
    result = await db.execute(
        select(CharacterGold).where(CharacterGold.character_id == character_id).with_for_update()
    )
    record = result.scalar_one_or_none()
    if record is None:
        record = CharacterGold(character_id=character_id, balance=0)
        db.add(record)
        await db.flush()
    return record


async def _record_transaction(
    db: AsyncSession,
    character_id: str,
    tx_type: TransactionType,
    amount: int,
    balance_after: int,
    description: str,
    related_id: Optional[str] = None,
) -> None:
    tx = Transaction(
        character_id=character_id,
        type=tx_type,
        amount=amount,
        balance_after=balance_after,
        related_id=related_id,
        description=description,
    )
    db.add(tx)


# ── Gold balance ───────────────────────────────────────────────────────────────

@router.get("/gold/{character_id}", response_model=GoldBalanceResponse)
async def get_gold(
    character_id: str,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_service_token),
) -> GoldBalanceResponse:
    """Get a character's current gold balance. Requires service token."""
    result = await db.execute(
        select(CharacterGold).where(CharacterGold.character_id == character_id)
    )
    record = result.scalar_one_or_none()
    balance = record.balance if record else 0
    return GoldBalanceResponse(character_id=character_id, balance=balance)


# ── Internal gold operations (service-to-service only) ───────────────────────

@router.post("/gold/award", response_model=GoldOperationResponse)
async def award_gold(
    body: GoldAwardRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_service_token),
) -> GoldOperationResponse:
    """Award gold to a character. Enforces the gold cap. Service-token only."""
    config = await cache.get_config()
    gold_cap: int = config["gold_cap"]

    async with db.begin():
        record = await _get_or_create_gold(db, body.character_id)
        new_balance = min(record.balance + body.amount, gold_cap)
        awarded = new_balance - record.balance
        record.balance = new_balance
        await _record_transaction(
            db, body.character_id, TransactionType.GOLD_AWARD,
            awarded, new_balance, body.description, body.related_id,
        )

    logger.info("Awarded %d gold to %s (balance: %d)", awarded, body.character_id, new_balance)
    return GoldOperationResponse(
        character_id=body.character_id,
        amount=awarded,
        balance_after=new_balance,
        description=body.description,
    )


@router.post("/gold/deduct", response_model=GoldOperationResponse)
async def deduct_gold(
    body: GoldDeductRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_service_token),
) -> GoldOperationResponse:
    """Deduct gold from a character. Fails if insufficient funds. Service-token only."""
    async with db.begin():
        record = await _get_or_create_gold(db, body.character_id)
        if record.balance < body.amount:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Insufficient gold: have {record.balance}, need {body.amount}",
            )
        record.balance -= body.amount
        await _record_transaction(
            db, body.character_id, TransactionType.GOLD_DEDUCT,
            -body.amount, record.balance, body.description, body.related_id,
        )
        new_balance = record.balance

    logger.info("Deducted %d gold from %s (balance: %d)", body.amount, body.character_id, new_balance)
    return GoldOperationResponse(
        character_id=body.character_id,
        amount=body.amount,
        balance_after=new_balance,
        description=body.description,
    )


@router.post("/gold/drop", response_model=GoldOperationResponse)
async def gold_drop(
    body: GoldDropRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_service_token),
) -> GoldOperationResponse:
    """Award a random gold drop for a monster kill. Service-token only."""
    config = await cache.get_config()
    gold_cap: int = config["gold_cap"]
    drop_min: int = config["gold_drop_min"]
    drop_max: int = config["gold_drop_max"]

    amount = random.randint(drop_min, max(drop_min, drop_max))
    description = f"Gold drop from {body.monster_name}"

    async with db.begin():
        record = await _get_or_create_gold(db, body.character_id)
        new_balance = min(record.balance + amount, gold_cap)
        actual = new_balance - record.balance
        record.balance = new_balance
        await _record_transaction(
            db, body.character_id, TransactionType.GOLD_DROP,
            actual, new_balance, description, body.monster_id,
        )

    logger.info("Gold drop %d for %s from %s", actual, body.character_id, body.monster_id)
    return GoldOperationResponse(
        character_id=body.character_id,
        amount=actual,
        balance_after=new_balance,
        description=description,
    )


# ── Marketplace ────────────────────────────────────────────────────────────────

def _listing_to_response(listing: Listing) -> ListingResponse:
    return ListingResponse(
        id=listing.id,
        seller_character_id=listing.seller_character_id,
        item_id=listing.item_id,
        item_name=listing.item_name,
        quantity=listing.quantity,
        unit_price=listing.unit_price,
        total_price=listing.unit_price * listing.quantity,
        category=listing.category,
        level_required=listing.level_required,
        status=listing.status,
        buyer_character_id=listing.buyer_character_id,
        expires_at=listing.expires_at,
        created_at=listing.created_at,
        sold_at=listing.sold_at,
    )


@router.post("/listings", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    body: CreateListingRequest,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> ListingResponse:
    """List an item for sale on the auction house."""
    config = await cache.get_config()
    duration_hours: int = config["listing_duration_hours"]
    expires_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)

    now = datetime.now(timezone.utc)
    listing = Listing(
        id=str(uuid.uuid4()),
        seller_character_id=body.character_id,
        item_id=body.item_id,
        item_name=body.item_name,
        quantity=body.quantity,
        unit_price=body.unit_price,
        category=body.category,
        level_required=body.level_required,
        status=ListingStatus.ACTIVE,
        expires_at=expires_at,
        created_at=now,
    )
    async with db.begin():
        db.add(listing)

    logger.info(
        "Listing created: %s x%d @%d by %s",
        body.item_id, body.quantity, body.unit_price, body.character_id,
    )
    return _listing_to_response(listing)


@router.get("/listings", response_model=list[ListingResponse])
async def browse_listings(
    category: Optional[ListingCategory] = Query(default=None),
    min_level: Optional[int] = Query(default=None, ge=1),
    max_level: Optional[int] = Query(default=None, ge=1),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> list[ListingResponse]:
    """Browse active marketplace listings."""
    now = datetime.now(timezone.utc)
    conditions = [
        Listing.status == ListingStatus.ACTIVE,
        Listing.expires_at > now,
    ]
    if category is not None:
        conditions.append(Listing.category == category)
    if min_level is not None:
        conditions.append(Listing.level_required >= min_level)
    if max_level is not None:
        conditions.append(Listing.level_required <= max_level)

    stmt = (
        select(Listing)
        .where(and_(*conditions))
        .order_by(Listing.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    listings = result.scalars().all()
    return [_listing_to_response(l) for l in listings]


@router.post("/listings/{listing_id}/buy", response_model=BuyListingResponse)
async def buy_listing(
    listing_id: str,
    body: BuyListingRequest,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> BuyListingResponse:
    """Purchase an active listing. Atomically transfers gold and marks listing sold."""
    config = await cache.get_config()
    ah_fee_pct: float = config["ah_fee_pct"]
    gold_cap: int = config["gold_cap"]
    now = datetime.now(timezone.utc)

    async with db.begin():
        # Lock listing row
        result = await db.execute(
            select(Listing).where(Listing.id == listing_id).with_for_update()
        )
        listing = result.scalar_one_or_none()

        if listing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
        if listing.status != ListingStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Listing is no longer active")
        if listing.expires_at <= now:
            listing.status = ListingStatus.EXPIRED
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Listing has expired")
        if listing.seller_character_id == body.buyer_character_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cannot buy your own listing")

        total_price = listing.unit_price * listing.quantity
        ah_fee = max(1, round(total_price * ah_fee_pct / 100))
        seller_receives = total_price - ah_fee

        # Lock buyer gold
        buyer_record = await _get_or_create_gold(db, body.buyer_character_id)
        if buyer_record.balance < total_price:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Insufficient gold: have {buyer_record.balance}, need {total_price}",
            )

        # Lock seller gold
        seller_result = await db.execute(
            select(CharacterGold)
            .where(CharacterGold.character_id == listing.seller_character_id)
            .with_for_update()
        )
        seller_record = seller_result.scalar_one_or_none()
        if seller_record is None:
            seller_record = CharacterGold(character_id=listing.seller_character_id, balance=0)
            db.add(seller_record)
            await db.flush()

        # Deduct from buyer
        buyer_record.balance -= total_price
        buyer_balance_after = buyer_record.balance

        # Credit seller (respecting cap)
        seller_record.balance = min(seller_record.balance + seller_receives, gold_cap)
        seller_balance_after = seller_record.balance

        # Update listing
        listing.status = ListingStatus.SOLD
        listing.buyer_character_id = body.buyer_character_id
        listing.ah_fee_paid = ah_fee
        listing.sold_at = now

        # Audit trail
        await _record_transaction(
            db, body.buyer_character_id, TransactionType.LISTING_PURCHASED,
            -total_price, buyer_balance_after,
            f"Purchased {listing.quantity}x {listing.item_name} from AH",
            listing_id,
        )
        await _record_transaction(
            db, listing.seller_character_id, TransactionType.LISTING_SOLD,
            seller_receives, seller_balance_after,
            f"Sold {listing.quantity}x {listing.item_name} on AH",
            listing_id,
        )
        await _record_transaction(
            db, listing.seller_character_id, TransactionType.AH_FEE,
            -ah_fee, seller_balance_after,
            f"AH fee ({ah_fee_pct}%) for sale of {listing.item_name}",
            listing_id,
        )

    logger.info(
        "Listing %s sold: %s bought from %s for %d (fee %d)",
        listing_id, body.buyer_character_id, listing.seller_character_id, total_price, ah_fee,
    )
    return BuyListingResponse(
        listing_id=listing_id,
        buyer_character_id=body.buyer_character_id,
        seller_character_id=listing.seller_character_id,
        item_id=listing.item_id,
        quantity=listing.quantity,
        total_price=total_price,
        ah_fee=ah_fee,
        seller_received=seller_receives,
        buyer_balance_after=buyer_balance_after,
        seller_balance_after=seller_balance_after,
    )


@router.delete("/listings/{listing_id}", response_model=MessageResponse)
async def cancel_listing(
    listing_id: str,
    character_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> MessageResponse:
    """Cancel an active listing. Only the seller can cancel. Item is returned to seller."""
    now = datetime.now(timezone.utc)

    async with db.begin():
        result = await db.execute(
            select(Listing).where(Listing.id == listing_id).with_for_update()
        )
        listing = result.scalar_one_or_none()

        if listing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
        if listing.seller_character_id != character_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the seller can cancel this listing")
        if listing.status != ListingStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Listing is not active")

        listing.status = ListingStatus.CANCELLED

        await _record_transaction(
            db, character_id, TransactionType.LISTING_CANCELLED,
            0, 0,
            f"Cancelled listing for {listing.quantity}x {listing.item_name}",
            listing_id,
        )

    logger.info("Listing %s cancelled by %s", listing_id, character_id)
    return MessageResponse(message="Listing cancelled. Item will be returned to your inventory.")


# ── Transaction history ────────────────────────────────────────────────────────

@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    character_id: str = Query(...),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> list[TransactionResponse]:
    """Retrieve a character's transaction history."""
    stmt = (
        select(Transaction)
        .where(Transaction.character_id == character_id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    txs = result.scalars().all()
    return [
        TransactionResponse(
            id=tx.id,
            character_id=tx.character_id,
            type=tx.type,
            amount=tx.amount,
            balance_after=tx.balance_after,
            related_id=tx.related_id,
            description=tx.description,
            created_at=tx.created_at,
        )
        for tx in txs
    ]
