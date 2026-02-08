"""
FolderChef — Recipes Router
==============================

This module defines API endpoints for recipe generation and retrieval.

ENDPOINTS:
    POST /api/recipes/generate    → Generate new recipes from current discounts
    GET  /api/recipes/            → Get previously generated recipes
    GET  /api/recipes/{recipe_id} → Get a specific recipe by ID

THE CORE LOOP:
    1. Frontend sends a POST to /api/recipes/generate with preferences
    2. Backend fetches current discounts from the database
    3. Backend sends discounted items to the AI service (OpenAI)
    4. AI generates structured recipe JSONs
    5. Backend validates, stores, and returns the recipes
    6. Frontend displays the recipes with cost savings info

NOTE:
    Recipe generation can take a few seconds because it calls the
    OpenAI API. The frontend should show a loading state while waiting.
"""

from fastapi import APIRouter, HTTPException

from app.models.recipe import (
    Recipe,
    RecipeGenerateRequest,
    RecipeGenerateResponse,
)

router = APIRouter()


@router.post(
    "/generate",
    response_model=RecipeGenerateResponse,
    summary="Generate recipes from current discounts",
)
async def generate_recipes(
    request: RecipeGenerateRequest,
):
    """
    Generate AI-powered recipes using currently discounted ingredients.

    This is the CORE endpoint of FolderChef. It:
    1. Fetches current discount data from the database
    2. Sends the discount items to the AI service
    3. Returns structured recipe suggestions

    Args:
        request (RecipeGenerateRequest):
            The generation parameters, sent as JSON in the request body.
            Includes: supermarkets to use, number of recipes,
            dietary preferences, and optional budget limit.

    Returns:
        RecipeGenerateResponse: The generated recipes with metadata.

    Raises:
        HTTPException(503): If the AI service is unavailable.
        HTTPException(400): If no discounts are available to generate from.

    Example Request Body:
        {
            "supermarkets": ["albert_heijn", "jumbo"],
            "num_recipes": 5,
            "dietary_preferences": ["vegetarian"],
            "max_budget_per_meal": 10.00
        }
    """
    # TODO: Implement — call RecipeService.generate()
    # For now, return an empty response
    return RecipeGenerateResponse(
        recipes=[],
        total_recipes=0,
        discounts_used=0,
    )


@router.get(
    "/",
    response_model=list[Recipe],
    summary="Get all generated recipes",
)
async def get_recipes():
    """
    Retrieve all previously generated recipes.

    Returns the most recent batch of recipes that were generated
    by the AI service.

    Returns:
        list[Recipe]: A list of generated recipes.
            Empty list if no recipes have been generated yet.
    """
    # TODO: Implement — fetch from database via RecipeService
    return []


@router.get(
    "/{recipe_id}",
    response_model=Recipe,
    summary="Get a specific recipe",
)
async def get_recipe_by_id(recipe_id: str):
    """
    Retrieve a specific recipe by its unique ID.

    Args:
        recipe_id (str):
            The unique identifier of the recipe.
            This comes from the URL path (e.g., /api/recipes/abc123).

    Returns:
        Recipe: The full recipe object.

    Raises:
        HTTPException(404): If no recipe exists with the given ID.

    Example:
        GET /api/recipes/abc123
    """
    # TODO: Implement — fetch from database via RecipeService
    raise HTTPException(
        status_code=404,
        detail=f"Recipe with id '{recipe_id}' not found",
    )
