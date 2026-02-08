"""
FolderChef — Data Models Package
==================================

This package contains all Pydantic models used throughout the application.

WHAT ARE MODELS?
    Models define the "shape" of our data. They describe:
    - What fields a piece of data has (name, price, category, etc.)
    - What type each field is (string, number, list, etc.)
    - Which fields are required vs optional

    Think of them as blueprints or templates for our data.

WHY USE MODELS?
    1. Validation — FastAPI automatically validates incoming data against models
    2. Documentation — Models appear in the auto-generated API docs
    3. Type Safety — Your editor can auto-complete model fields
    4. Serialization — Models easily convert to/from JSON

MODULES:
    - discount.py → Models for supermarket discount items
    - recipe.py   → Models for AI-generated recipes
"""

from app.models.discount import (
    DiscountItem,
    DiscountResponse,
    SupermarketEnum,
)
from app.models.recipe import (
    Recipe,
    RecipeIngredient,
    RecipeGenerateRequest,
    RecipeGenerateResponse,
)

# This lets other files do: from app.models import DiscountItem, Recipe
__all__ = [
    "DiscountItem",
    "DiscountResponse",
    "SupermarketEnum",
    "Recipe",
    "RecipeIngredient",
    "RecipeGenerateRequest",
    "RecipeGenerateResponse",
]
