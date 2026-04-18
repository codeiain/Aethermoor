"""Pydantic request and response schemas for the crafting service."""
from pydantic import BaseModel

from models import RecipeCategory


# ── Responses ─────────────────────────────────────────────────────────────────

class IngredientResponse(BaseModel):
    item_id: str
    quantity: int


class RecipeSummaryResponse(BaseModel):
    id: str
    name: str
    description: str
    category: RecipeCategory
    result_item_id: str
    result_quantity: int
    level_required: int


class RecipeDetailResponse(RecipeSummaryResponse):
    ingredients: list[IngredientResponse]


# ── Requests ──────────────────────────────────────────────────────────────────

class CraftRequest(BaseModel):
    character_id: str
    recipe_id: str


class CraftResponse(BaseModel):
    success: bool
    message: str
    result_item_id: str
    result_quantity: int


class MessageResponse(BaseModel):
    message: str
