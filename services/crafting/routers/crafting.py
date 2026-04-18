"""Player-facing crafting endpoints.

All endpoints require a valid user JWT (verified via Auth Service).
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import character_client
from auth_client import AuthVerificationError, verify_user_jwt
from character_client import CharacterClientError
from database import get_db
from models import Recipe, RecipeCategory
from schemas import CraftRequest, CraftResponse, RecipeDetailResponse, RecipeSummaryResponse

logger = logging.getLogger("crafting")
router = APIRouter(prefix="/crafting", tags=["crafting"])
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


@router.get("/recipes", response_model=list[RecipeSummaryResponse])
async def list_recipes(
    category: Optional[RecipeCategory] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> list[RecipeSummaryResponse]:
    """List all crafting recipes, optionally filtered by category."""
    stmt = select(Recipe)
    if category is not None:
        stmt = stmt.where(Recipe.category == category)
    stmt = stmt.order_by(Recipe.level_required, Recipe.name)
    result = await db.execute(stmt)
    recipes = result.scalars().all()
    return [
        RecipeSummaryResponse(
            id=r.id,
            name=r.name,
            description=r.description,
            category=r.category,
            result_item_id=r.result_item_id,
            result_quantity=r.result_quantity,
            level_required=r.level_required,
        )
        for r in recipes
    ]


@router.get("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
async def get_recipe(
    recipe_id: str,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> RecipeDetailResponse:
    """Get full recipe detail including ingredients."""
    result = await db.execute(
        select(Recipe)
        .options(selectinload(Recipe.ingredients))
        .where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return RecipeDetailResponse(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        category=recipe.category,
        result_item_id=recipe.result_item_id,
        result_quantity=recipe.result_quantity,
        level_required=recipe.level_required,
        ingredients=[
            {"item_id": ing.item_id, "quantity": ing.quantity}
            for ing in recipe.ingredients
        ],
    )


@router.post("/craft", response_model=CraftResponse, status_code=status.HTTP_200_OK)
async def craft_item(
    body: CraftRequest,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(_current_user),
) -> CraftResponse:
    """Attempt to craft an item.

    Validates the recipe, checks the character's backpack for materials,
    then atomically deducts materials and adds the result via the character service.
    All inventory changes are committed in one transaction server-side — no partial states.
    """
    result = await db.execute(
        select(Recipe)
        .options(selectinload(Recipe.ingredients))
        .where(Recipe.id == body.recipe_id)
    )
    recipe = result.scalar_one_or_none()
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    # Fetch current backpack from character service
    try:
        backpack_items = await character_client.get_backpack(body.character_id)
    except CharacterClientError as exc:
        logger.warning("Failed to fetch backpack for %s: %s", body.character_id, exc)
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    # Build inventory map from backpack
    inventory: dict[str, int] = {}
    for item in backpack_items:
        if item.get("item_id"):
            inventory[item["item_id"]] = inventory.get(item["item_id"], 0) + item["quantity"]

    # Validate all ingredients are present
    missing = []
    for ing in recipe.ingredients:
        have = inventory.get(ing.item_id, 0)
        if have < ing.quantity:
            missing.append(f"{ing.item_id} (need {ing.quantity}, have {have})")

    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing materials: {', '.join(missing)}",
        )

    # Commit the craft atomically via the character service
    try:
        await character_client.apply_craft(
            character_id=body.character_id,
            items_to_remove=[
                {"item_id": ing.item_id, "quantity": ing.quantity}
                for ing in recipe.ingredients
            ],
            items_to_add=[
                {"item_id": recipe.result_item_id, "quantity": recipe.result_quantity}
            ],
        )
    except CharacterClientError as exc:
        logger.warning("apply_craft failed for %s: %s", body.character_id, exc)
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    logger.info(
        "Crafted %s x%d for character %s",
        recipe.result_item_id,
        recipe.result_quantity,
        body.character_id,
    )
    return CraftResponse(
        success=True,
        message=f"You crafted {recipe.name}!",
        result_item_id=recipe.result_item_id,
        result_quantity=recipe.result_quantity,
    )
