"""SQLAlchemy ORM models for the crafting service."""
import enum
import uuid

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class RecipeCategory(str, enum.Enum):
    WEAPON = "weapon"
    ARMOUR = "armour"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    MISC = "misc"


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    category: Mapped[RecipeCategory] = mapped_column(
        Enum(RecipeCategory, name="recipe_category_enum"), nullable=False
    )
    result_item_id: Mapped[str] = mapped_column(String(64), nullable=False)
    result_quantity: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    level_required: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        UniqueConstraint("recipe_id", "item_id", name="uq_ingredient_recipe_item"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    recipe_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
