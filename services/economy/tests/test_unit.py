"""Unit tests for economy utilities — no external dependencies required."""
import hashlib
import hmac
import os
import time

import pytest

# conftest.py sets env vars and sys.path before any service import
from zero_trust import ServiceTokenError, make_service_token, verify_service_token_value
from schemas import (
    ConfigUpdateRequest,
    CreateListingRequest,
    GoldAwardRequest,
    GoldDeductRequest,
    GoldDropRequest,
    BuyListingRequest,
)
from models import ListingCategory, ListingStatus, TransactionType


# ── Zero-trust service tokens ─────────────────────────────────────────────────

class TestZeroTrust:
    def test_valid_token_accepted(self):
        token = make_service_token()
        verify_service_token_value(token)  # must not raise

    def test_missing_token_raises(self):
        with pytest.raises(ServiceTokenError, match="Missing"):
            verify_service_token_value(None)

    def test_empty_string_raises(self):
        with pytest.raises(ServiceTokenError, match="Missing"):
            verify_service_token_value("")

    def test_malformed_token_raises(self):
        with pytest.raises(ServiceTokenError, match="Malformed"):
            verify_service_token_value("notimestamp")

    def test_expired_token_raises(self):
        old_bucket = (int(time.time()) // 60) - 5
        digest = hmac.new(
            os.environ["SERVICE_TOKEN"].encode(),
            str(old_bucket).encode(),
            hashlib.sha256,
        ).hexdigest()
        with pytest.raises(ServiceTokenError, match="expired"):
            verify_service_token_value(f"{old_bucket}:{digest}")

    def test_wrong_secret_raises(self):
        ts = int(time.time()) // 60
        bad_digest = hmac.new(
            b"wrong-secret",
            str(ts).encode(),
            hashlib.sha256,
        ).hexdigest()
        with pytest.raises(ServiceTokenError, match="invalid"):
            verify_service_token_value(f"{ts}:{bad_digest}")

    def test_token_format_is_timestamp_colon_hex(self):
        token = make_service_token()
        parts = token.split(":")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert len(parts[1]) == 64  # SHA-256 hex digest


# ── Schema validation ─────────────────────────────────────────────────────────

class TestGoldSchemas:
    def test_award_requires_positive_amount(self):
        with pytest.raises(Exception):
            GoldAwardRequest(character_id="c1", amount=0)

    def test_award_requires_positive_amount_negative(self):
        with pytest.raises(Exception):
            GoldAwardRequest(character_id="c1", amount=-10)

    def test_award_valid(self):
        req = GoldAwardRequest(character_id="c1", amount=100)
        assert req.amount == 100
        assert req.description == "Gold awarded"

    def test_deduct_requires_positive_amount(self):
        with pytest.raises(Exception):
            GoldDeductRequest(character_id="c1", amount=0)

    def test_deduct_valid(self):
        req = GoldDeductRequest(character_id="c1", amount=50)
        assert req.amount == 50

    def test_drop_has_defaults(self):
        req = GoldDropRequest(character_id="c1", monster_id="m1")
        assert req.monster_name == "monster"


class TestListingSchemas:
    def test_create_requires_positive_price(self):
        with pytest.raises(Exception):
            CreateListingRequest(
                character_id="c1", item_id="sword", item_name="Iron Sword",
                quantity=1, unit_price=0,
            )

    def test_create_requires_positive_quantity(self):
        with pytest.raises(Exception):
            CreateListingRequest(
                character_id="c1", item_id="sword", item_name="Iron Sword",
                quantity=0, unit_price=100,
            )

    def test_create_rejects_empty_item_id(self):
        with pytest.raises(Exception):
            CreateListingRequest(
                character_id="c1", item_id="  ", item_name="Iron Sword",
                quantity=1, unit_price=100,
            )

    def test_create_valid_defaults(self):
        req = CreateListingRequest(
            character_id="c1", item_id="sword", item_name="Iron Sword",
            quantity=1, unit_price=100,
        )
        assert req.category == ListingCategory.MISC
        assert req.level_required == 1

    def test_create_with_category(self):
        req = CreateListingRequest(
            character_id="c1", item_id="sword", item_name="Iron Sword",
            quantity=1, unit_price=100, category=ListingCategory.WEAPON,
        )
        assert req.category == ListingCategory.WEAPON

    def test_buy_request_has_character(self):
        req = BuyListingRequest(buyer_character_id="c2")
        assert req.buyer_character_id == "c2"


class TestAdminConfigSchema:
    def test_all_fields_optional(self):
        req = ConfigUpdateRequest()
        assert req.gold_cap is None
        assert req.ah_fee_pct is None

    def test_gold_cap_must_be_positive(self):
        with pytest.raises(Exception):
            ConfigUpdateRequest(gold_cap=0)

    def test_ah_fee_pct_bounds(self):
        with pytest.raises(Exception):
            ConfigUpdateRequest(ah_fee_pct=-1.0)
        with pytest.raises(Exception):
            ConfigUpdateRequest(ah_fee_pct=51.0)

    def test_valid_config_partial(self):
        req = ConfigUpdateRequest(gold_cap=500000, ah_fee_pct=10.0)
        assert req.gold_cap == 500000
        assert req.ah_fee_pct == 10.0

    def test_exclude_none_returns_only_set_fields(self):
        req = ConfigUpdateRequest(gold_cap=100000)
        dumped = req.model_dump(exclude_none=True)
        assert "gold_cap" in dumped
        assert "ah_fee_pct" not in dumped


# ── Enum coverage ─────────────────────────────────────────────────────────────

class TestEnums:
    def test_listing_status_values(self):
        assert ListingStatus.ACTIVE == "active"
        assert ListingStatus.SOLD == "sold"
        assert ListingStatus.CANCELLED == "cancelled"
        assert ListingStatus.EXPIRED == "expired"

    def test_listing_category_values(self):
        assert ListingCategory.WEAPON == "weapon"
        assert ListingCategory.ARMOUR == "armour"
        assert ListingCategory.CONSUMABLE == "consumable"
        assert ListingCategory.MATERIAL == "material"
        assert ListingCategory.MISC == "misc"

    def test_transaction_type_values(self):
        assert TransactionType.GOLD_AWARD == "gold_award"
        assert TransactionType.GOLD_DROP == "gold_drop"
        assert TransactionType.LISTING_PURCHASED == "listing_purchased"
        assert TransactionType.LISTING_SOLD == "listing_sold"
        assert TransactionType.AH_FEE == "ah_fee"
