"""
FolderChef — Recipe Service
==============================

This module orchestrates the recipe generation process.

WHAT DOES THIS SERVICE DO?
    It's the conductor of the recipe generation orchestra:
    1. Gets the current discounts from the DiscountService
    2. Sends them to the AIService for recipe generation
    3. Validates and stores the generated recipes
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

from app.models.discount import SupermarketEnum
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
        response = await service.generate(
            RecipeGenerateRequest(num_recipes=5)
        )
        for recipe in response.recipes:
            print(recipe.title)
    """

    def __init__(self):
        """
        Initialise the recipe service.

        Creates instances of AIService and DiscountService.
        """
        self.ai_service = AIService()
        self.discount_service = DiscountService()

    async def generate(
        self,
        request: RecipeGenerateRequest,
    ) -> RecipeGenerateResponse:
        """
        Generate recipes based on current supermarket discounts.

        This is the CORE method of FolderChef. It:
        1. Fetches current discounts
        2. Generates recipes using AI
        3. Returns the results

        Args:
            request: The generation parameters including:
                - supermarkets to use
                - number of recipes
                - dietary preferences
                - budget limit

        Returns:
            RecipeGenerateResponse: Generated recipes with metadata.

        Raises:
            ValueError: If no discounts are available.
        """
        # Step 1: Get current discounts
        all_items = []
        for supermarket_name in request.supermarkets:
            try:
                supermarket = SupermarketEnum(supermarket_name)
                discount_responses = await self.discount_service.get_discounts(
                    supermarket=supermarket
                )
                for response in discount_responses:
                    all_items.extend(response.items)
            except ValueError:
                print(f"⚠️  Unknown supermarket: {supermarket_name}")

        if not all_items:
            return RecipeGenerateResponse(
                recipes=[],
                total_recipes=0,
                discounts_used=0,
            )

        # Step 2: Generate recipes with AI
        recipes = await self.ai_service.generate_recipes(
            discount_items=all_items,
            num_recipes=request.num_recipes,
            dietary_preferences=request.dietary_preferences,
            max_budget=request.max_budget_per_meal,
        )

        # Step 3: TODO — Store recipes in database

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
        """
        Retrieve all stored recipes.

        Returns:
            list[Recipe]: All recipes from the database.
        """
        # TODO: Implement database retrieval
        return []

    async def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """
        Retrieve a specific recipe by its ID.

        Args:
            recipe_id: The unique identifier of the recipe.

        Returns:
            Recipe | None: The recipe if found, None otherwise.
        """
        # TODO: Implement database retrieval
        return None
