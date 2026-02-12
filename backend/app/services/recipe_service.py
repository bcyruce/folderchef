"""
FolderChef — Recipe Service
==============================

This module orchestrates the recipe generation process.

WHAT DOES THIS SERVICE DO?
    It's the conductor of the recipe generation orchestra:
    1. Gets the current discounts from the DiscountService
    2. Filters them by user-selected labels (if provided)
    3. Sends them + user prompt to the AIService for recipe generation
    4. Returns recipes to the API endpoints

WHY A SEPARATE SERVICE?
    The recipe generation involves multiple steps and multiple services.
    Having a dedicated RecipeService keeps this logic organised and
    makes it easy to add features like:
    - Favourite recipes
    - Recipe history
    - Rating system
    - Meal planning (future feature)
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.discount import CleanedProduct
from app.models.recipe import Recipe, RecipeGenerateRequest, RecipeGenerateResponse
from app.services.ai_service import AIService
from app.services.discount_service import DiscountService


class RecipeService:
    """
    Service for recipe generation and management.

    Orchestrates the discount-to-recipe pipeline.

    Attributes:
        ai_service (AIService): AI service for recipe generation.
        discount_service (DiscountService): Service for accessing discount data.

    Usage:
        service = RecipeService()
        response = await service.generate(db, RecipeGenerateRequest(num_recipes=5))
        for recipe in response.recipes:
            print(recipe.title)
    """

    def __init__(self):
        self.ai_service = AIService()
        self.discount_service = DiscountService()

    async def generate(
        self,
        db: AsyncSession,
        request: RecipeGenerateRequest,
    ) -> RecipeGenerateResponse:
        """
        Generate recipes based on current supermarket discounts.

        Pipeline:
            1. Fetch current discounts from DB
            2. Filter by label_filter (if provided)
            3. Send filtered items + user_prompt to AI
            4. Return generated recipes

        Args:
            db: Active database session.
            request: Generation parameters (supermarkets, labels, prompt, etc.)

        Returns:
            RecipeGenerateResponse: Generated recipes with metadata.
        """
        # Step 1: Get current discounts from database
        all_items: list[CleanedProduct] = []
        for supermarket_name in request.supermarkets:
            try:
                discount_responses = await self.discount_service.get_discounts(
                    db, supermarket=supermarket_name
                )
                for resp in discount_responses:
                    all_items.extend(resp.items)
            except Exception as e:
                print(f"WARNING: Could not fetch discounts for {supermarket_name}: {e}")

        print(f"Recipe generation: {len(all_items)} total discount items from DB")

        # Step 2: Filter by labels (if user selected any)
        if request.label_filter:
            label_set = set(request.label_filter)
            filtered = [
                item for item in all_items
                if label_set.intersection(item.labels)
            ]
            print(
                f"  Label filter {request.label_filter}: "
                f"{len(all_items)} -> {len(filtered)} items"
            )
            all_items = filtered

        if not all_items:
            print("  No items after filtering — returning empty response")
            return RecipeGenerateResponse(
                recipes=[],
                total_recipes=0,
                discounts_used=0,
            )

        # Step 3: Generate recipes with AI (pass user_prompt)
        recipes = await self.ai_service.generate_recipes(
            discount_items=all_items,
            num_recipes=request.num_recipes,
            dietary_preferences=request.dietary_preferences or [],
            max_budget=request.max_budget_per_meal,
            user_prompt=request.user_prompt,
        )

        # Step 4: Build response
        discounts_used = sum(
            1 for recipe in recipes
            for ingredient in recipe.ingredients
            if ingredient.is_discounted
        )

        return RecipeGenerateResponse(
            recipes=recipes,
            total_recipes=len(recipes),
            discounts_used=discounts_used,
        )

    async def get_all_recipes(self) -> list[Recipe]:
        """Retrieve all stored recipes (TODO: implement DB retrieval)."""
        return []

    async def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Retrieve a specific recipe by ID (TODO: implement DB retrieval)."""
        return None
