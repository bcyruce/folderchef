"""
FolderChef -- Discount Data Models
===================================

This module defines the data models for the discount pipeline:

    1. RawDiscount     -- Data as scraped directly from the supermarket
    2. CleanedProduct   -- Data after AI cleaning (common name + labels)
    3. DiscountResponse -- What the API sends to the frontend

THE PIPELINE:
    Scraper --> RawDiscount --> AI Cleaner --> CleanedProduct --> Database --> API

VALID LABELS (fixed set -- AI may only use these):
    bio, fresh, meat, fish, vegetable, fruit, dairy, eggs, cheese,
    ready-to-eat, bakery, pantry, cooking aids, frozen, snack,
    candy, beverage, salad, asia, non-food
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ------------------------------------------------------------------
# Fixed label set -- AI must pick from ONLY these values
# ------------------------------------------------------------------
VALID_LABELS: list[str] = [
    "bio",
    "fresh",
    "meat",
    "fish",
    "vegetable",
    "fruit",
    "dairy",
    "eggs",
    "cheese",
    "ready-to-eat",
    "bakery",
    "pantry",
    "cooking aids",
    "frozen",
    "snack",
    "candy",
    "beverage",
    "salad",
    "asia",
    "non-food",
]


class SupermarketEnum(str, Enum):
    """
    Enum of supported Dutch supermarkets.

    Values:
        ALBERT_HEIJN: Albert Heijn supermarket
        JUMBO: Jumbo supermarket
    """
    ALBERT_HEIJN = "albert_heijn"
    JUMBO = "jumbo"


# ==================================================================
# 1. RAW DISCOUNT -- straight from the scraper, no AI processing
# ==================================================================
class RawDiscount(BaseModel):
    """
    A single discounted product as scraped from a supermarket website.

    This is the raw, unprocessed data before AI cleaning.

    Attributes:
        name (str):
            Product name exactly as shown on the supermarket website.
            Example: "AH Biologische cherry tomaten"

        supermarket (str):
            Which supermarket. "albert_heijn" or "jumbo".

        original_price (float | None):
            Regular price per unit in EUR before discount.

        discount_price_per_unit (float | None):
            Effective price per unit after discount in EUR.
            For "1+1 gratis" at 2.00, this would be 1.00.
            For "2 voor 3.00", this would be 1.50.

        discount_info (str):
            The discount description as displayed by the supermarket.
            Examples: "1+1 gratis", "2 voor 2.49", "30% korting"

        weight (str | None):
            Product weight or size as shown on the website.
            Examples: "500g", "1 liter", "6 stuks"

        price_per_unit (float | None):
            Price per unit in EUR (unit depends on weight: kg, liter, etc.).

        product_url (str | None):
            URL to the product page on the supermarket website.

        start_date (date | None):
            Start date of the discount period.

        end_date (date | None):
            End date of the discount period.

        image_url (str | None):
            URL to the product image.
    """
    name: str = Field(..., description="Product name from supermarket")
    supermarket: str = Field(..., description="Supermarket identifier")
    original_price: Optional[float] = Field(default=None, ge=0)
    discount_price_per_unit: Optional[float] = Field(default=None, ge=0)
    discount_info: str = Field(..., description="Discount label e.g. '1+1 gratis'")
    weight: Optional[str] = Field(default=None)
    price_per_unit: Optional[float] = Field(default=None, ge=0)
    product_url: Optional[str] = Field(default=None)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    image_url: Optional[str] = Field(default=None)


# ==================================================================
# 2. CLEANED PRODUCT -- after AI processing
# ==================================================================
class CleanedProduct(BaseModel):
    """
    A discount product after AI cleaning.

    The AI adds:
        - A common/generic name (e.g., "AH Bio tomaat" -> "tomato")
        - Labels from the fixed set (e.g., ["bio", "vegetable", "fresh"])

    Attributes:
        id (int | None):
            Database primary key. None before saving.

        raw_name (str):
            Original product name from the supermarket.

        common_name (str):
            AI-assigned generic name. Lowercase English.
            This allows matching products across supermarkets.
            Example: "tomato", "chicken breast", "gouda cheese"

        labels (list[str]):
            AI-assigned labels from the VALID_LABELS set.
            Each product can have multiple labels.
            Example: ["bio", "vegetable", "fresh"]

        supermarket (str):
            Which supermarket this is from.

        original_price (float | None):
            Regular price per unit in EUR.

        discount_price_per_unit (float | None):
            Effective price per unit in EUR after discount.

        discount_info (str):
            Discount description (e.g., "1+1 gratis").

        weight (str | None):
            Product weight or size.

        price_per_unit (float | None):
            Price per unit in EUR (unit depends on weight).

        product_url (str | None):
            URL to the product page.

        start_date (date | None):
            Discount start date.

        end_date (date | None):
            Discount end date.

        image_url (str | None):
            Product image URL.

        scraped_at (datetime | None):
            When this product was scraped.
    """
    id: Optional[int] = Field(default=None)
    raw_name: str = Field(..., description="Original supermarket product name")
    common_name: str = Field(..., description="AI-assigned generic name")
    labels: list[str] = Field(default_factory=list, description="Labels from fixed set")
    supermarket: str = Field(...)
    original_price: Optional[float] = Field(default=None, ge=0)
    discount_price_per_unit: Optional[float] = Field(default=None, ge=0)
    discount_info: str = Field(...)
    weight: Optional[str] = Field(default=None)
    price_per_unit: Optional[float] = Field(default=None, ge=0)
    product_url: Optional[str] = Field(default=None)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    image_url: Optional[str] = Field(default=None)
    scraped_at: Optional[datetime] = Field(default=None)


# ==================================================================
# 3. API RESPONSE -- what the frontend receives
# ==================================================================
class DiscountResponse(BaseModel):
    """
    API response for discount data.

    Attributes:
        supermarket (str): Supermarket name.
        total_items (int): Number of items.
        week (str): Human-readable week label.
        items (list[CleanedProduct]): Cleaned discount products.
    """
    supermarket: str = Field(...)
    total_items: int = Field(...)
    week: str = Field(..., examples=["Week 6, 2026"])
    items: list[CleanedProduct] = Field(default_factory=list)
