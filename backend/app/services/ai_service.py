"""
FolderChef -- AI Service
=========================

Handles all AI/LLM operations using OpenAI:

    1. CLEANING -- Takes raw scraped products and returns:
       - A common/generic English name (e.g., "AH Bio tomaat" -> "tomato")
       - Labels from a fixed set (e.g., ["bio", "vegetable", "fresh"])

    2. RECIPE GENERATION -- Takes cleaned products and returns recipes
       (to be implemented later)

AI CLEANING FLOW:
    Raw products come in batches (e.g. 50 at a time).
    We send the batch to GPT with a carefully designed prompt.
    GPT returns a JSON array with common_name and labels for each product.
    We validate the labels against our fixed set and merge the results.

COST MANAGEMENT:
    - We use gpt-4o-mini (cheapest model with good JSON output)
    - We batch products to minimize API calls
    - Each cleaning call costs roughly $0.01-0.05 depending on batch size
"""

import json
from typing import Optional

from openai import AsyncOpenAI

from app.config import settings
from app.models.discount import RawDiscount, CleanedProduct, VALID_LABELS
from app.models.recipe import Recipe


class AIService:
    """
    AI service for product cleaning and recipe generation.

    Attributes:
        client: OpenAI async API client.
        model: Which GPT model to use.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model

    # ==============================================================
    # PRODUCT CLEANING
    # ==============================================================

    async def clean_products(
        self,
        raw_products: list[RawDiscount],
        batch_size: int = 80,
    ) -> list[CleanedProduct]:
        """
        Clean a list of raw scraped products using AI.

        For each product, the AI assigns:
            - common_name: A generic English name (lowercase)
            - labels: A list from the fixed VALID_LABELS set

        Products are processed in batches to stay within token limits.
        With batch_size=80 and ~300 bonus products, that's only ~4 API calls.

        Args:
            raw_products: List of raw scraped discount items.
            batch_size: How many products to send per API call.
                        80 is a good balance of speed vs reliability.

        Returns:
            list[CleanedProduct]: Products with AI-assigned names and labels.
        """
        if not raw_products:
            return []

        if not settings.OPENAI_API_KEY:
            print("WARNING: No OPENAI_API_KEY set. Skipping AI cleaning.")
            return self._fallback_clean(raw_products)

        all_cleaned: list[CleanedProduct] = []

        # Process in batches
        for i in range(0, len(raw_products), batch_size):
            batch = raw_products[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(raw_products) + batch_size - 1) // batch_size
            print(f"  AI cleaning batch {batch_num}/{total_batches} ({len(batch)} products)...")

            try:
                cleaned_batch = await self._clean_batch(batch)
                all_cleaned.extend(cleaned_batch)
            except Exception as e:
                print(f"  ERROR in batch {batch_num}: {e}")
                # Fallback: use raw names without AI cleaning
                all_cleaned.extend(self._fallback_clean(batch))

        return all_cleaned

    async def _clean_batch(self, batch: list[RawDiscount]) -> list[CleanedProduct]:
        """
        Send a batch of products to GPT for cleaning.

        Args:
            batch: A list of raw products (max ~40 at a time).

        Returns:
            list[CleanedProduct]: Cleaned products with common names + labels.
        """
        # Build the product list for the prompt
        product_lines = []
        for idx, p in enumerate(batch):
            product_lines.append(f'{idx}: "{p.name}"')

        products_text = "\n".join(product_lines)

        labels_text = ", ".join(VALID_LABELS)

        system_prompt = f"""You are a food product classifier for a Dutch grocery app.

Your job:
1. For each Dutch supermarket product name, provide a COMMON English name (lowercase, generic).
   - "AH Biologische cherry tomaten" -> "cherry tomato"
   - "Jumbo Kipfilet" -> "chicken breast"
   - "AH Goudse kaas jong belegen" -> "gouda cheese young mature"
   - "Coca-Cola Zero" -> "coca-cola zero"  (keep brand for branded items)
   - "AH Verse jus d'orange" -> "orange juice"

2. Assign one or more LABELS from ONLY this fixed list:
   [{labels_text}]

   Rules for labels:
   - "bio" = organic/biologisch products
   - "fresh" = products sold in the fresh/refrigerated section
   - "meat" = any meat product
   - "fish" = any fish or seafood
   - "vegetable" = vegetables
   - "fruit" = fruits
   - "dairy" = milk, yogurt, butter, cream
   - "eggs" = egg products
   - "cheese" = any cheese
   - "ready-to-eat" = pre-made meals, salads, sandwiches
   - "bakery" = bread, pastries, cakes
   - "pantry" = dry goods, canned food, pasta, rice, sauces
   - "cooking-adds" = herbs, spices, oils, vinegar, condiments
   - "frozen" = frozen food
   - "snack" = chips, crackers, savory snacks
   - "candy" = chocolate, sweets, cookies
   - "beverage" = drinks (soda, juice, water, coffee, tea)
   - "salad" = pre-made salads or salad mixes
   - "asia" = Asian food products (noodles, soy sauce, wok, sushi)

   A product can have MULTIPLE labels. For example:
   - "AH Biologische tomaten" -> ["bio", "vegetable", "fresh"]
   - "AH Verse kipfilet" -> ["meat", "fresh"]

RESPOND WITH ONLY a valid JSON array. Each element has:
  {{"idx": <number>, "common_name": "<string>", "labels": ["<label>", ...]}}

No explanation, no markdown, just the JSON array."""

        user_prompt = f"Classify these products:\n{products_text}"

        # Call OpenAI
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,  # Low temperature = more consistent output
            response_format={"type": "json_object"},
        )

        # Parse the AI response
        raw_content = response.choices[0].message.content or "{}"
        ai_results = self._parse_ai_response(raw_content, len(batch))

        # Merge AI results with raw product data
        cleaned: list[CleanedProduct] = []
        for idx, raw in enumerate(batch):
            ai_data = ai_results.get(idx, {})
            common_name = ai_data.get("common_name", raw.name.lower())
            raw_labels = ai_data.get("labels", [])

            # Validate labels -- only keep ones in our fixed set
            valid = [lbl for lbl in raw_labels if lbl in VALID_LABELS]

            cleaned.append(CleanedProduct(
                raw_name=raw.name,
                common_name=common_name,
                labels=valid,
                supermarket=raw.supermarket,
                original_price=raw.original_price,
                discount_price_per_unit=raw.discount_price_per_unit,
                discount_info=raw.discount_info,
                weight=raw.weight,
                price_per_kg=raw.price_per_kg,
                start_date=raw.start_date,
                end_date=raw.end_date,
                image_url=raw.image_url,
            ))

        return cleaned

    def _parse_ai_response(self, content: str, expected_count: int) -> dict:
        """
        Parse the JSON response from GPT.

        GPT sometimes wraps the array in an object like {"products": [...]},
        so we handle both formats.

        Args:
            content: The raw JSON string from GPT.
            expected_count: How many products we expect.

        Returns:
            dict: Mapping of index -> {"common_name": str, "labels": list}
        """
        try:
            data = json.loads(content)

            # Handle wrapped format: {"products": [...]} or {"items": [...]}
            if isinstance(data, dict):
                # Find the array inside the dict
                for key, value in data.items():
                    if isinstance(value, list):
                        data = value
                        break
                else:
                    # Single item dict -- treat as one result
                    data = [data]

            if not isinstance(data, list):
                print(f"  WARNING: AI returned unexpected format: {type(data)}")
                return {}

            # Build index -> result mapping
            result = {}
            for item in data:
                if isinstance(item, dict):
                    idx = item.get("idx", item.get("index", len(result)))
                    result[idx] = {
                        "common_name": item.get("common_name", ""),
                        "labels": item.get("labels", []),
                    }

            return result

        except json.JSONDecodeError as e:
            print(f"  WARNING: Could not parse AI response as JSON: {e}")
            return {}

    def _fallback_clean(self, products: list[RawDiscount]) -> list[CleanedProduct]:
        """
        Fallback cleaning when AI is not available.

        Uses the raw product name as-is (no AI processing).
        Assigns no labels.

        Args:
            products: Raw products to convert.

        Returns:
            list[CleanedProduct]: Products with raw names and empty labels.
        """
        return [
            CleanedProduct(
                raw_name=p.name,
                common_name=p.name.lower(),
                labels=[],
                supermarket=p.supermarket,
                original_price=p.original_price,
                discount_price_per_unit=p.discount_price_per_unit,
                discount_info=p.discount_info,
                weight=p.weight,
                price_per_kg=p.price_per_kg,
                start_date=p.start_date,
                end_date=p.end_date,
                image_url=p.image_url,
            )
            for p in products
        ]

    # ==============================================================
    # RECIPE GENERATION (to be implemented)
    # ==============================================================

    async def generate_recipes(
        self,
        discount_items: list[CleanedProduct],
        num_recipes: int = 5,
        dietary_preferences: Optional[list[str]] = None,
        max_budget: Optional[float] = None,
    ) -> list[Recipe]:
        """
        Generate recipes using AI based on cleaned discount products.

        TODO: Implement in next iteration.
        """
        print(f"Recipe generation: {len(discount_items)} items, {num_recipes} recipes requested")
        return []
