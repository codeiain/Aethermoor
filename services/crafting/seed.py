"""Seed initial crafting recipes on service startup."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Recipe, RecipeCategory, RecipeIngredient

# (name, description, category, result_item_id, result_qty, level_req, ingredients[(item_id, qty)])
_RECIPES = [
    (
        "Iron Sword",
        "A sturdy blade forged from raw iron ore.",
        RecipeCategory.WEAPON,
        "iron_sword",
        1,
        1,
        [("iron_ore", 3), ("wood_plank", 1)],
    ),
    (
        "Health Potion",
        "Restores 20 HP when consumed.",
        RecipeCategory.CONSUMABLE,
        "health_potion",
        1,
        1,
        [("healing_herb", 2), ("empty_vial", 1)],
    ),
    (
        "Leather Armour",
        "Light armour crafted from tanned hides.",
        RecipeCategory.ARMOUR,
        "leather_armour",
        1,
        1,
        [("leather_hide", 4), ("leather_strip", 2)],
    ),
    (
        "Magic Staff",
        "Channels arcane energy through a crystal focus.",
        RecipeCategory.WEAPON,
        "magic_staff",
        1,
        5,
        [("magic_crystal", 2), ("wood_plank", 2)],
    ),
    (
        "Steel Helmet",
        "Protective headgear smelted from iron and coal.",
        RecipeCategory.ARMOUR,
        "steel_helmet",
        1,
        3,
        [("iron_ore", 3), ("coal", 1)],
    ),
    (
        "Arrow Bundle",
        "Twenty arrows fletched from feathers and wood.",
        RecipeCategory.CONSUMABLE,
        "arrow_bundle",
        20,
        1,
        [("wood_plank", 1), ("feather", 3), ("iron_ore", 1)],
    ),
    (
        "Iron Ingot",
        "Refined iron ready for smithing.",
        RecipeCategory.MATERIAL,
        "iron_ingot",
        1,
        1,
        [("iron_ore", 2), ("coal", 1)],
    ),
]


async def seed_recipes(db: AsyncSession) -> None:
    """Insert default recipes if they do not already exist."""
    for (name, desc, cat, result_id, result_qty, level_req, ingredients) in _RECIPES:
        existing = await db.execute(select(Recipe).where(Recipe.name == name))
        if existing.scalar_one_or_none() is not None:
            continue

        recipe = Recipe(
            id=str(uuid.uuid4()),
            name=name,
            description=desc,
            category=cat,
            result_item_id=result_id,
            result_quantity=result_qty,
            level_required=level_req,
        )
        db.add(recipe)
        await db.flush()  # get the recipe id

        for item_id, qty in ingredients:
            db.add(RecipeIngredient(
                id=str(uuid.uuid4()),
                recipe_id=recipe.id,
                item_id=item_id,
                quantity=qty,
            ))

    await db.commit()
