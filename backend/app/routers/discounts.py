"""
FolderChef -- Discounts Router
================================

API endpoints for supermarket discount data.

ENDPOINTS:
    GET  /api/discounts/            --> Get all cleaned discounts from DB
    GET  /api/discounts/{store}     --> Get discounts for one supermarket
    POST /api/discounts/refresh     --> Trigger scrape -> AI clean -> store

QUERY PARAMS (optional on all endpoints):
    week  -- ISO week number (1-53). Default: latest available / current week.
    year  -- Year (e.g. 2026). Default: latest available / current year.

THE FLOW:
    1. Call POST /api/discounts/refresh to populate the database
       (scrapes AH, cleans with AI, stores results as a named batch)
    2. Call GET /api/discounts/ to retrieve the cleaned data
       (reads from database, fast response)
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.discount import DiscountResponse
from app.services.discount_service import DiscountService
from app.database.connection import get_db

router = APIRouter()

# Create a single shared service instance
_discount_service = DiscountService()


@router.get(
    "/",
    response_model=list[DiscountResponse],
    summary="Get all current discounts from database",
)
async def get_all_discounts(
    week: Optional[int] = Query(default=None, description="ISO week number (1-53)"),
    year: Optional[int] = Query(default=None, description="Year (e.g. 2026)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve cleaned discount data from the database.

    Returns products grouped by supermarket. Each product has:
    - common_name (AI-assigned generic name)
    - labels (from the fixed label set)
    - prices, weight, discount info, dates, image

    If week/year are omitted, returns the latest available batch.
    Call POST /api/discounts/refresh first to populate the database.

    Returns:
        list[DiscountResponse]: Discount data grouped by supermarket.
    """
    return await _discount_service.get_discounts(db, week=week, year=year)


@router.get(
    "/{supermarket}",
    response_model=DiscountResponse,
    summary="Get discounts for a specific supermarket",
)
async def get_discounts_by_supermarket(
    supermarket: str,
    week: Optional[int] = Query(default=None, description="ISO week number (1-53)"),
    year: Optional[int] = Query(default=None, description="Year (e.g. 2026)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve cleaned discounts for a specific supermarket.

    Args:
        supermarket: "albert_heijn" or "jumbo"
        week: Optional ISO week number. Default: latest batch.
        year: Optional year. Default: latest batch.

    Returns:
        DiscountResponse: Discount data for that supermarket.
    """
    results = await _discount_service.get_discounts(
        db, supermarket=supermarket, week=week, year=year,
    )
    if results:
        return results[0]
    return DiscountResponse(
        supermarket=supermarket,
        total_items=0,
        week="No data",
        items=[],
    )


@router.post(
    "/refresh",
    summary="Scrape, clean with AI, and store discounts",
)
async def refresh_discounts(
    supermarket: Optional[str] = Query(
        default=None,
        description="Specific supermarket to refresh (or all if not specified)",
    ),
    week: Optional[int] = Query(
        default=None,
        description="ISO week number (1-53). Default: current week.",
    ),
    year: Optional[int] = Query(
        default=None,
        description="Year (e.g. 2026). Default: current year.",
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger the full discount pipeline:

        1. SCRAPE -- Fetch raw products from supermarket APIs
        2. CLEAN  -- Send to AI for common names + labels
        3. STORE  -- Save to database as a named batch

    The batch is named like: albert_heijn_bonus_w06_2026

    If the same batch already exists, it is replaced.
    Other weeks remain untouched.

    This can take 30-60 seconds depending on the number of products
    and the AI processing time.

    Args:
        supermarket: Optional. "albert_heijn" or "jumbo".
                     If not set, refreshes all supermarkets.
        week: Optional. ISO week number. Default: current week.
        year: Optional. Year. Default: current year.

    Returns:
        dict: Summary of what was scraped and cleaned.
    """
    summary = await _discount_service.refresh_discounts(
        db, supermarket=supermarket, week=week, year=year,
    )
    return {
        "status": "completed",
        "summary": summary,
    }
