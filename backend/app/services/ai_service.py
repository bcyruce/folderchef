"""
FolderChef — AI Service
=========================

This module handles all communication with the OpenAI API.

WHAT DOES THIS SERVICE DO?
    1. Takes a list of discounted supermarket items
    2. Crafts a prompt for the AI model (GPT)
    3. Sends the prompt to OpenAI's API
    4. Parses the AI's response into structured Recipe objects

THE AI PROMPT STRATEGY:
    We use a carefully designed prompt that tells the AI to:
    - Create recipes using ONLY the discounted ingredients
    - Estimate costs based on discount prices
    - Generate Dutch-friendly meals
    - Return structured JSON that matches our Recipe model

WHY OPENAI?
    - GPT models are excellent at understanding food/cooking context
    - They can generate structured JSON output reliably
    - The API is well-documented and easy to use

COST NOTE:
    Each recipe generation call costs real money (OpenAI charges per token).
    We should:
    - Cache results when possible
    - Batch requests efficiently
    - Use the cheapest model that gives good results (e.g., gpt-4o-mini)
"""

from typing import Optional

from openai import AsyncOpenAI

from app.config import settings
from app.models.discount import DiscountItem
from app.models.recipe import Recipe


class AIService:
    """
    Service for AI-powered recipe generation using OpenAI.

    This service is responsible for turning a list of discounted
    supermarket items into delicious, budget-friendly recipes.

    Attributes:
        client (AsyncOpenAI): The OpenAI API client.
        model (str): Which GPT model to use (default: gpt-4o-mini).

    Usage:
        ai = AIService()
        recipes = await ai.generate_recipes(
            discount_items=[...],
            num_recipes=5,
        )
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialise the AI service.

        Args:
            model: The OpenAI model to use. Default is "gpt-4o-mini"
                   which is fast and affordable. Use "gpt-4o" for
                   higher quality (but more expensive) results.
        """
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model

    def _build_system_prompt(self) -> str:
        """
        Build the system prompt that tells the AI how to behave.

        The system prompt sets the AI's "personality" and rules.
        It tells the AI it's a Dutch meal planner that creates
        budget-friendly recipes from discounted ingredients.

        Returns:
            str: The system prompt string.
        """
        return """You are FolderChef, an expert Dutch meal planning assistant.
Your job is to create delicious, budget-friendly recipes using ingredients
that are currently on sale at Dutch supermarkets (Albert Heijn and Jumbo).

RULES:
1. Prioritise discounted ingredients — they should make up the core of each recipe.
2. You may include a few common pantry staples (oil, salt, pepper, etc.) that aren't on sale.
3. Estimate the total cost based on the discount prices provided.
4. Create recipes suitable for the Dutch market (consider local tastes and ingredients).
5. Include a mix of meal types: quick dinners, meal prep, soups, etc.
6. Always respond in valid JSON format matching the schema provided.
7. Keep instructions clear and beginner-friendly.
8. Estimate realistic preparation and cooking times."""

    def _build_recipe_prompt(
        self,
        discount_items: list[DiscountItem],
        num_recipes: int = 5,
        dietary_preferences: Optional[list[str]] = None,
        max_budget: Optional[float] = None,
    ) -> str:
        """
        Build the user prompt with discount data and preferences.

        This creates the specific request that includes the current
        discount items and the user's preferences.

        Args:
            discount_items: List of currently discounted products.
            num_recipes: How many recipes to generate.
            dietary_preferences: Optional dietary restrictions.
            max_budget: Optional maximum cost per meal in EUR.

        Returns:
            str: The formatted user prompt string.
        """
        # Format the discount items into a readable list
        items_text = "\n".join(
            f"- {item.name} ({item.supermarket.value}): "
            f"{item.discount_label}"
            f"{f' — €{item.discount_price:.2f}' if item.discount_price else ''}"
            for item in discount_items
        )

        prompt = f"""Here are the current supermarket discounts in the Netherlands:

{items_text}

Please generate {num_recipes} recipes using these discounted ingredients."""

        if dietary_preferences:
            prefs = ", ".join(dietary_preferences)
            prompt += f"\n\nDietary preferences: {prefs}"

        if max_budget:
            prompt += f"\n\nMaximum budget per meal: €{max_budget:.2f}"

        prompt += """

Respond with a JSON array of recipe objects. Each recipe should have:
- title (string)
- description (string, 1-2 sentences)
- servings (integer)
- prep_time_minutes (integer)
- cook_time_minutes (integer)
- estimated_cost (float, in EUR)
- ingredients (array of {name, quantity, is_discounted, estimated_price})
- instructions (array of strings, step-by-step)
- tags (array of strings like "vegetarian", "quick", "budget")
- supermarkets (array of supermarket names used)"""

        return prompt

    async def generate_recipes(
        self,
        discount_items: list[DiscountItem],
        num_recipes: int = 5,
        dietary_preferences: Optional[list[str]] = None,
        max_budget: Optional[float] = None,
    ) -> list[Recipe]:
        """
        Generate recipes using AI based on discounted ingredients.

        This is the main method of the AI service. It sends the
        discount data to OpenAI and returns structured recipes.

        Args:
            discount_items: Currently discounted supermarket items.
            num_recipes: Number of recipes to generate (1-20).
            dietary_preferences: User's dietary restrictions/preferences.
            max_budget: Maximum budget per meal in EUR.

        Returns:
            list[Recipe]: Generated recipe objects.

        Raises:
            openai.APIError: If the OpenAI API call fails.
            ValueError: If the AI response can't be parsed into recipes.

        Example:
            recipes = await ai_service.generate_recipes(
                discount_items=discounts,
                num_recipes=5,
                dietary_preferences=["vegetarian"],
                max_budget=10.00,
            )
        """
        # TODO: Implement the actual API call and response parsing
        # Steps:
        # 1. Build the prompt using _build_recipe_prompt()
        # 2. Call self.client.chat.completions.create()
        # 3. Parse the JSON response
        # 4. Validate and convert to Recipe objects
        # 5. Return the recipes

        print(f"🤖 Generating {num_recipes} recipes from {len(discount_items)} discounted items...")

        # Placeholder — return empty list until implemented
        return []

    async def categorise_items(
        self,
        items: list[DiscountItem],
    ) -> list[DiscountItem]:
        """
        Use AI to categorise discount items into food categories.

        The scraped discount data often lacks proper categorisation.
        This method uses AI to assign categories like "dairy", "meat",
        "vegetables", etc. to each item.

        Args:
            items: List of discount items without categories.

        Returns:
            list[DiscountItem]: The same items with categories filled in.
        """
        # TODO: Implement AI-based categorisation
        print(f"🏷️  Categorising {len(items)} items with AI...")
        return items
