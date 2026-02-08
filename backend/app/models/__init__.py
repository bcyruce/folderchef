"""
FolderChef -- Data Models Package
==================================

Pydantic models that define the shape of data throughout the app.

Modules:
    - discount.py -- RawDiscount, CleanedProduct, DiscountResponse
    - recipe.py   -- Recipe, RecipeIngredient, RecipeGenerateRequest/Response
"""

from app.models.discount import (
    RawDiscount,
    CleanedProduct,
    DiscountResponse,
    SupermarketEnum,
    VALID_LABELS,
)
from app.models.recipe import (
    Recipe,
    RecipeIngredient,
    RecipeGenerateRequest,
    RecipeGenerateResponse,
)

__all__ = [
    "RawDiscount",
    "CleanedProduct",
    "DiscountResponse",
    "SupermarketEnum",
    "VALID_LABELS",
    "Recipe",
    "RecipeIngredient",
    "RecipeGenerateRequest",
    "RecipeGenerateResponse",
]
