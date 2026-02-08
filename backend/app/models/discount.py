"""
FolderChef — Discount Data Models
===================================

This module defines the data models (schemas) for supermarket discount items.

WHAT IS A DISCOUNT ITEM?
    A discount item represents a single product that is on sale at a
    Dutch supermarket (Albert Heijn or Jumbo). It contains information
    like the product name, original price, discount price, category, etc.

THESE MODELS ARE USED FOR:
    1. Validating data that comes FROM the scrapers (input validation)
    2. Defining the shape of data we send TO the frontend (API responses)
    3. Storing discount data in the database

EXAMPLE:
    A discount item might look like:
    {
        "name": "Goudse kaas jong belegen",
        "supermarket": "albert_heijn",
        "original_price": 5.99,
        "discount_price": 3.99,
        "discount_percentage": 33,
        "category": "dairy",
        "image_url": "https://...",
        "valid_from": "2025-01-06",
        "valid_until": "2025-01-12"
    }
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SupermarketEnum(str, Enum):
    """
    Enum of supported Dutch supermarkets.

    WHY AN ENUM?
        Enums restrict a field to only specific allowed values.
        This prevents typos like "alber_hijn" or "JUMBO".

    Values:
        ALBERT_HEIJN: Albert Heijn supermarket
        JUMBO: Jumbo supermarket
    """
    ALBERT_HEIJN = "albert_heijn"
    JUMBO = "jumbo"


class DiscountItem(BaseModel):
    """
    A single discounted product from a supermarket.

    This model represents one product that is currently on sale.
    It is used both for API responses and for storing in the database.

    Attributes:
        id (str | None):
            Unique identifier for this discount item.
            None when the item is first scraped (the database assigns the ID).

        name (str):
            The product name as shown in the supermarket.
            Example: "Goudse kaas jong belegen"

        supermarket (SupermarketEnum):
            Which supermarket this deal is from.
            Either "albert_heijn" or "jumbo".

        original_price (float | None):
            The regular price before discount (in EUR).
            None if the original price isn't available.

        discount_price (float | None):
            The discounted sale price (in EUR).
            None if the price is expressed differently (e.g., "2 for 1").

        discount_label (str):
            The discount description as shown by the supermarket.
            Example: "2e halve prijs", "1+1 gratis", "30% korting"

        category (str | None):
            AI-assigned food category.
            Example: "dairy", "meat", "vegetables", "bakery"
            None before AI categorisation.

        image_url (str | None):
            URL to the product image.

        valid_from (date | None):
            Start date of the discount period.

        valid_until (date | None):
            End date of the discount period.
    """

    id: Optional[str] = Field(
        default=None,
        description="Unique identifier (assigned by database)"
    )
    name: str = Field(
        ...,  # "..." means this field is REQUIRED
        description="Product name",
        examples=["Goudse kaas jong belegen"],
    )
    supermarket: SupermarketEnum = Field(
        ...,
        description="Which supermarket this deal is from",
    )
    original_price: Optional[float] = Field(
        default=None,
        description="Regular price in EUR before discount",
        ge=0,  # "ge" = greater than or equal to 0
    )
    discount_price: Optional[float] = Field(
        default=None,
        description="Sale price in EUR",
        ge=0,
    )
    discount_label: str = Field(
        ...,
        description="Discount description (e.g., '2e halve prijs')",
        examples=["1+1 gratis", "30% korting", "2e halve prijs"],
    )
    category: Optional[str] = Field(
        default=None,
        description="AI-assigned food category",
        examples=["dairy", "meat", "vegetables", "bakery", "beverages"],
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL to product image",
    )
    valid_from: Optional[date] = Field(
        default=None,
        description="Start date of the discount period",
    )
    valid_until: Optional[date] = Field(
        default=None,
        description="End date of the discount period",
    )


class DiscountResponse(BaseModel):
    """
    API response model for a list of discounts.

    This is what the frontend receives when it calls GET /api/discounts.

    Attributes:
        supermarket (str):
            The supermarket these discounts are from.

        total_items (int):
            How many discount items are in this response.

        week (str):
            A human-readable label for which week these discounts are for.
            Example: "Week 2, 2025"

        items (list[DiscountItem]):
            The actual list of discounted products.
    """

    supermarket: str = Field(
        ...,
        description="Supermarket name",
    )
    total_items: int = Field(
        ...,
        description="Number of discount items",
    )
    week: str = Field(
        ...,
        description="Which week these discounts are for",
        examples=["Week 2, 2025"],
    )
    items: list[DiscountItem] = Field(
        default_factory=list,
        description="List of discounted products",
    )
