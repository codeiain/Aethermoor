"""Unit tests for the AETHERMOOR Inventory Service.

Tests cover zero-trust auth, schema validation, seed data integrity,
inventory helper logic, and business rules — no DB or network required.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import time
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from zero_trust import ServiceTokenError, make_service_token, verify_service_token_value
from schemas import (
    ALL_EQUIPMENT_SLOTS,
    BACKPACK_SIZE,
    DropRequest,
    EquipRequest,
    InventoryItemResponse,
    ItemResponse,
    LootRequest,
    UnequipRequest,
    UseRequest,
)
from models import EquipmentSlot, ItemRarity, ItemType
from seed import SEED_ITEMS
from routers.inventory import _compute_equipped_stats, _find_free_backpack_slot


# ── Zero-trust service tokens ─────────────────────────────────────────────────

class TestZeroTrust:
    def test_valid_token_accepted(self):
        token = make_service_token()
        verify_service_token_value(token)

    def test_missing_token_raises(self):
        with pytest.raises(ServiceTokenError, match="Missing"):
            verify_service_token_value(None)

    def test_empty_string_raises(self):
        with pytest.raises(ServiceTokenError, match="Missing"):
            verify_service_token_value("")

    def test_malformed_token_raises(self):
        with pytest.raises(ServiceTokenError, match="Malformed"):
            verify_service_token_value("no-colon-here")

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

    def test_token_format(self):
        token = make_service_token()
        parts = token.split(":")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert len(parts[1]) == 64


# ── Schema validation ─────────────────────────────────────────────────────────

class TestDropRequest:
    def test_defaults_quantity_one(self):
        req = DropRequest(inventory_item_id="inv-1")
        assert req.quantity == 1

    def test_quantity_must_be_at_least_one(self):
        with pytest.raises(Exception):
            DropRequest(inventory_item_id="inv-1", quantity=0)

    def test_negative_quantity_rejected(self):
        with pytest.raises(Exception):
            DropRequest(inventory_item_id="inv-1", quantity=-5)

    def test_explicit_quantity(self):
        req = DropRequest(inventory_item_id="inv-1", quantity=10)
        assert req.quantity == 10


class TestEquipRequest:
    def test_valid_equip_request(self):
        req = EquipRequest(inventory_item_id="inv-1", slot=EquipmentSlot.MAIN_HAND)
        assert req.slot == EquipmentSlot.MAIN_HAND

    def test_invalid_slot_rejected(self):
        with pytest.raises(Exception):
            EquipRequest(inventory_item_id="inv-1", slot="banana")

    def test_all_slots_accepted(self):
        for slot in EquipmentSlot:
            req = EquipRequest(inventory_item_id="x", slot=slot)
            assert req.slot == slot


class TestUnequipRequest:
    def test_valid(self):
        req = UnequipRequest(slot=EquipmentSlot.HEAD)
        assert req.slot == EquipmentSlot.HEAD


class TestUseRequest:
    def test_valid(self):
        req = UseRequest(inventory_item_id="inv-potion")
        assert req.inventory_item_id == "inv-potion"


class TestLootRequest:
    def test_defaults_quantity_one(self):
        req = LootRequest(character_id="char-1", item_id="health_potion")
        assert req.quantity == 1

    def test_explicit_quantity(self):
        req = LootRequest(character_id="char-1", item_id="iron_ore", quantity=5)
        assert req.quantity == 5

    def test_quantity_must_be_positive(self):
        with pytest.raises(Exception):
            LootRequest(character_id="char-1", item_id="iron_ore", quantity=0)


# ── Seed data integrity ────────────────────────────────────────────────────────

class TestSeedData:
    def test_has_required_starter_items(self):
        ids = {item["id"] for item in SEED_ITEMS}
        assert "basic_sword" in ids
        assert "leather_armour" in ids
        assert "health_potion" in ids
        assert "iron_ore" in ids

    def test_all_items_have_required_fields(self):
        required = {"id", "name", "type", "rarity", "stackable", "max_stack", "stats", "description"}
        for item in SEED_ITEMS:
            missing = required - item.keys()
            assert not missing, f"Item {item.get('id')} missing fields: {missing}"

    def test_stackable_items_have_max_stack_gt_1(self):
        for item in SEED_ITEMS:
            if item["stackable"]:
                assert item["max_stack"] > 1, f"{item['id']} stackable but max_stack=1"

    def test_non_stackable_items_have_max_stack_1(self):
        for item in SEED_ITEMS:
            if not item["stackable"]:
                assert item["max_stack"] == 1, f"{item['id']} not stackable but max_stack>1"

    def test_consumables_are_stackable(self):
        for item in SEED_ITEMS:
            if item["type"] == "consumable":
                assert item["stackable"], f"{item['id']} is consumable but not stackable"

    def test_equippable_items_have_valid_slot(self):
        valid_slots = {s.value for s in EquipmentSlot} | {None}
        for item in SEED_ITEMS:
            assert item.get("equippable_slot") in valid_slots, (
                f"{item['id']} has invalid equippable_slot: {item.get('equippable_slot')}"
            )

    def test_weapons_equipped_in_hand(self):
        for item in SEED_ITEMS:
            if item["type"] == "weapon" and item.get("equippable_slot"):
                assert item["equippable_slot"] in ("main_hand", "off_hand"), (
                    f"Weapon {item['id']} equipped in non-hand slot"
                )

    def test_no_duplicate_ids(self):
        ids = [item["id"] for item in SEED_ITEMS]
        assert len(ids) == len(set(ids))

    def test_item_types_are_valid(self):
        valid = {t.value for t in ItemType}
        for item in SEED_ITEMS:
            assert item["type"] in valid

    def test_item_rarities_are_valid(self):
        valid = {r.value for r in ItemRarity}
        for item in SEED_ITEMS:
            assert item["rarity"] in valid

    def test_health_potion_has_hp_restore(self):
        potion = next(i for i in SEED_ITEMS if i["id"] == "health_potion")
        assert "hp_restore" in potion["stats"]
        assert potion["stats"]["hp_restore"] > 0

    def test_basic_sword_has_bonus_attack(self):
        sword = next(i for i in SEED_ITEMS if i["id"] == "basic_sword")
        assert "bonus_attack" in sword["stats"]
        assert sword["stats"]["bonus_attack"] > 0

    def test_leather_armour_has_bonus_defense(self):
        armour = next(i for i in SEED_ITEMS if i["id"] == "leather_armour")
        assert "bonus_defense" in armour["stats"]
        assert armour["stats"]["bonus_defense"] > 0


# ── Backpack slot logic ────────────────────────────────────────────────────────

class TestFindFreeBackpackSlot:
    def test_empty_backpack_returns_slot_zero(self):
        assert _find_free_backpack_slot(set()) == 0

    def test_slot_zero_occupied_returns_one(self):
        assert _find_free_backpack_slot({0}) == 1

    def test_contiguous_occupied_returns_next(self):
        occupied = set(range(5))
        assert _find_free_backpack_slot(occupied) == 5

    def test_full_backpack_returns_none(self):
        full = set(range(BACKPACK_SIZE))
        assert _find_free_backpack_slot(full) is None

    def test_gap_in_middle_returns_gap(self):
        occupied = {0, 1, 3, 4}
        assert _find_free_backpack_slot(occupied) == 2

    def test_only_last_slot_free(self):
        occupied = set(range(BACKPACK_SIZE - 1))
        assert _find_free_backpack_slot(occupied) == BACKPACK_SIZE - 1


# ── Equipped stats calculation ────────────────────────────────────────────────

def _make_item_resp(item_id: str, stats: dict) -> ItemResponse:
    return ItemResponse(
        id=item_id,
        name=item_id.replace("_", " ").title(),
        type=ItemType.WEAPON,
        rarity=ItemRarity.COMMON,
        stackable=False,
        max_stack=1,
        stats=stats,
        description="",
        equippable_slot=None,
    )


def _make_inv_resp(item_resp: ItemResponse, slot: str) -> InventoryItemResponse:
    return InventoryItemResponse(
        id=f"inv-{item_resp.id}",
        item_id=item_resp.id,
        quantity=1,
        slot_index=None,
        equipped_slot=slot,
        item=item_resp,
    )


class TestComputeEquippedStats:
    def test_empty_equipment_returns_empty(self):
        equipment = {s: None for s in ALL_EQUIPMENT_SLOTS}
        assert _compute_equipped_stats(equipment) == {}

    def test_single_item_stats_returned(self):
        item = _make_item_resp("basic_sword", {"bonus_attack": 3})
        inv = _make_inv_resp(item, "main_hand")
        equipment = {s: None for s in ALL_EQUIPMENT_SLOTS}
        equipment["main_hand"] = inv
        result = _compute_equipped_stats(equipment)
        assert result == {"bonus_attack": 3}

    def test_multiple_items_stats_summed(self):
        sword = _make_item_resp("basic_sword", {"bonus_attack": 3})
        armour = _make_item_resp("leather_armour", {"bonus_defense": 2})
        equipment = {s: None for s in ALL_EQUIPMENT_SLOTS}
        equipment["main_hand"] = _make_inv_resp(sword, "main_hand")
        equipment["chest"] = _make_inv_resp(armour, "chest")
        result = _compute_equipped_stats(equipment)
        assert result["bonus_attack"] == 3
        assert result["bonus_defense"] == 2

    def test_stacking_same_stat(self):
        ring1 = _make_item_resp("silver_ring_1", {"bonus_attack": 1})
        ring2 = _make_item_resp("silver_ring_2", {"bonus_attack": 1})
        equipment = {s: None for s in ALL_EQUIPMENT_SLOTS}
        equipment["ring_1"] = _make_inv_resp(ring1, "ring_1")
        equipment["ring_2"] = _make_inv_resp(ring2, "ring_2")
        result = _compute_equipped_stats(equipment)
        assert result["bonus_attack"] == 2

    def test_non_numeric_stats_excluded(self):
        item = _make_item_resp("weird", {"bonus_attack": 3, "name": "ignored"})
        equipment = {s: None for s in ALL_EQUIPMENT_SLOTS}
        equipment["main_hand"] = _make_inv_resp(item, "main_hand")
        result = _compute_equipped_stats(equipment)
        assert "name" not in result
        assert result.get("bonus_attack") == 3


# ── Constants ─────────────────────────────────────────────────────────────────

class TestConstants:
    def test_backpack_size_is_24(self):
        assert BACKPACK_SIZE == 24

    def test_all_equipment_slots_present(self):
        expected = {"head", "chest", "legs", "feet", "main_hand", "off_hand", "ring_1", "ring_2", "amulet"}
        assert set(ALL_EQUIPMENT_SLOTS) == expected

    def test_equipment_slot_enum_matches_constants(self):
        enum_values = {s.value for s in EquipmentSlot}
        assert enum_values == set(ALL_EQUIPMENT_SLOTS)


# ── Enum values ────────────────────────────────────────────────────────────────

class TestEnums:
    def test_item_type_values(self):
        assert ItemType.WEAPON == "weapon"
        assert ItemType.ARMOUR == "armour"
        assert ItemType.CONSUMABLE == "consumable"
        assert ItemType.MATERIAL == "material"
        assert ItemType.MISC == "misc"

    def test_item_rarity_values(self):
        assert ItemRarity.COMMON == "common"
        assert ItemRarity.UNCOMMON == "uncommon"
        assert ItemRarity.RARE == "rare"
        assert ItemRarity.EPIC == "epic"
        assert ItemRarity.LEGENDARY == "legendary"

    def test_equipment_slot_values(self):
        assert EquipmentSlot.HEAD == "head"
        assert EquipmentSlot.CHEST == "chest"
        assert EquipmentSlot.MAIN_HAND == "main_hand"
        assert EquipmentSlot.OFF_HAND == "off_hand"
        assert EquipmentSlot.RING_1 == "ring_1"
        assert EquipmentSlot.RING_2 == "ring_2"
        assert EquipmentSlot.AMULET == "amulet"
