"""
FolderChef — Recipes Router
==============================

API endpoints for recipe generation and retrieval.

ENDPOINTS:
    POST /api/recipes/generate    → Generate new recipes from current discounts
    GET  /api/recipes/            → Get previously generated recipes
    GET  /api/recipes/{recipe_id} → Get a specific recipe by ID

THE CORE LOOP:
    1. Frontend sends a POST to /api/recipes/generate with preferences
    2. Backend fetches current discounts from the database
    3. Filters by user-selected labels
    4. Backend sends filtered items + user prompt to the AI service (OpenAI)
    5. AI generates structured recipe JSONs
    6. Backend validates and returns the recipes
    7. Frontend displays the recipes with cost savings info
"""

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.recipe import (
    Recipe,
    RecipeGenerateRequest,
    RecipeGenerateResponse,
)
from app.services.recipe_service import RecipeService

router = APIRouter()

_recipe_service = RecipeService()


@router.post(
    "/generate",
    response_model=RecipeGenerateResponse,
    summary="Generate recipes from current discounts",
)
async def generate_recipes(
    request: RecipeGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI-powered recipes using currently discounted ingredients.

    Pipeline:
        1. Fetch discounts from database
        2. Filter by label_filter (if provided)
        3. Call OpenAI with the filtered items + user_prompt
        4. Return structured recipes

    Args:
        request: Generation parameters (supermarkets, labels, prompt, etc.)

    Returns:
        RecipeGenerateResponse: Generated recipes with metadata.
    """
    try:
        return await _recipe_service.generate(db, request)
    except Exception as e:
        print(f"ERROR in generate_recipes: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get(
    "/",
    response_model=list[Recipe],
    summary="Get all generated recipes",
)
async def get_recipes():
    """Retrieve all previously generated recipes."""
    return await _recipe_service.get_all_recipes()


@router.get(
    "/{recipe_id}",
    response_model=Recipe,
    summary="Get a specific recipe",
)
async def get_recipe_by_id(recipe_id: str):
    """Retrieve a specific recipe by its unique ID."""
    recipe = await _recipe_service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=404,
            detail=f"Recipe with id '{recipe_id}' not found",
        )
    return recipe
