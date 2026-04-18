"""Unit tests for crafting service logic."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# ── Inventory helper (mirrors logic in character service apply_craft) ─────────

def compute_inventory(backpack_items: list[dict]) -> dict[str, int]:
    """Aggregate item quantities from a flat backpack list."""
    inventory: dict[str, int] = {}
    for item in backpack_items:
        if item.get("item_id"):
            inventory[item["item_id"]] = inventory.get(item["item_id"], 0) + item["quantity"]
    return inventory


def check_can_craft(inventory: dict[str, int], ingredients: list[dict]) -> list[str]:
    """Return list of missing material descriptions; empty list means craftable."""
    missing = []
    for ing in ingredients:
        have = inventory.get(ing["item_id"], 0)
        if have < ing["quantity"]:
            missing.append(f"{ing['item_id']} (need {ing['quantity']}, have {have})")
    return missing


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestComputeInventory:
    def test_empty_backpack(self):
        assert compute_inventory([]) == {}

    def test_single_item(self):
        items = [{"slot_index": 0, "item_id": "iron_ore", "quantity": 5}]
        assert compute_inventory(items) == {"iron_ore": 5}

    def test_stacks_same_item(self):
        items = [
            {"slot_index": 0, "item_id": "iron_ore", "quantity": 3},
            {"slot_index": 1, "item_id": "iron_ore", "quantity": 2},
        ]
        assert compute_inventory(items) == {"iron_ore": 5}

    def test_multiple_items(self):
        items = [
            {"slot_index": 0, "item_id": "iron_ore", "quantity": 3},
            {"slot_index": 1, "item_id": "wood_plank", "quantity": 1},
        ]
        inv = compute_inventory(items)
        assert inv == {"iron_ore": 3, "wood_plank": 1}

    def test_skips_empty_slots(self):
        items = [{"slot_index": 0, "item_id": None, "quantity": 0}]
        assert compute_inventory(items) == {}


class TestCheckCanCraft:
    def test_can_craft_when_exact_materials(self):
        inventory = {"iron_ore": 3, "wood_plank": 1}
        ingredients = [{"item_id": "iron_ore", "quantity": 3}, {"item_id": "wood_plank", "quantity": 1}]
        assert check_can_craft(inventory, ingredients) == []

    def test_can_craft_when_surplus_materials(self):
        inventory = {"iron_ore": 10, "wood_plank": 5}
        ingredients = [{"item_id": "iron_ore", "quantity": 3}]
        assert check_can_craft(inventory, ingredients) == []

    def test_cannot_craft_missing_item(self):
        inventory = {"iron_ore": 3}
        ingredients = [{"item_id": "iron_ore", "quantity": 3}, {"item_id": "wood_plank", "quantity": 1}]
        missing = check_can_craft(inventory, ingredients)
        assert len(missing) == 1
        assert "wood_plank" in missing[0]

    def test_cannot_craft_insufficient_quantity(self):
        inventory = {"iron_ore": 1}
        ingredients = [{"item_id": "iron_ore", "quantity": 3}]
        missing = check_can_craft(inventory, ingredients)
        assert len(missing) == 1
        assert "need 3, have 1" in missing[0]

    def test_empty_inventory_returns_all_missing(self):
        ingredients = [
            {"item_id": "iron_ore", "quantity": 3},
            {"item_id": "wood_plank", "quantity": 1},
        ]
        missing = check_can_craft({}, ingredients)
        assert len(missing) == 2

    def test_empty_ingredients_always_craftable(self):
        assert check_can_craft({"iron_ore": 99}, []) == []


class TestSeedRecipeData:
    """Verify the seed recipe definitions are internally consistent."""

    def test_all_recipes_have_ingredients(self):
        from seed import _RECIPES
        for recipe in _RECIPES:
            name, _desc, _cat, _result_id, _result_qty, _level_req, ingredients = recipe
            assert len(ingredients) > 0, f"Recipe '{name}' has no ingredients"

    def test_all_result_quantities_positive(self):
        from seed import _RECIPES
        for recipe in _RECIPES:
            name, _desc, _cat, _result_id, result_qty, _level_req, _ingredients = recipe
            assert result_qty >= 1, f"Recipe '{name}' has invalid result_qty {result_qty}"

    def test_all_ingredient_quantities_positive(self):
        from seed import _RECIPES
        for recipe in _RECIPES:
            name, _desc, _cat, _result_id, _result_qty, _level_req, ingredients = recipe
            for item_id, qty in ingredients:
                assert qty >= 1, f"Recipe '{name}' ingredient '{item_id}' has qty {qty}"

    def test_level_requirements_positive(self):
        from seed import _RECIPES
        for recipe in _RECIPES:
            name, _desc, _cat, _result_id, _result_qty, level_req, _ingredients = recipe
            assert level_req >= 1, f"Recipe '{name}' has invalid level_req {level_req}"

    def test_recipe_names_unique(self):
        from seed import _RECIPES
        names = [r[0] for r in _RECIPES]
        assert len(names) == len(set(names)), "Duplicate recipe names in seed data"
