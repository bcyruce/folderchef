"""
FolderChef — Discounts Router
================================

This module defines API endpoints for supermarket discount data.

ENDPOINTS:
    GET  /api/discounts/          → Get all current discounts
    GET  /api/discounts/{store}   → Get discounts for a specific supermarket
    POST /api/discounts/refresh   → Trigger a fresh scrape of discounts

THE FLOW:
    1. Frontend calls GET /api/discounts/
    2. Backend checks the database for cached discounts
    3. If discounts are fresh (scraped recently), return them
    4. If discounts are stale, trigger a new scrape, then return
    5. Frontend displays the discount items to the user

NOTE FOR BEGINNERS:
    - Each function below is an "endpoint" — a URL that the frontend can call.
    - The decorator (@router.get, @router.post) defines the URL path and HTTP method.
    - FastAPI automatically converts the return value to JSON.
"""

from fastapi import APIRouter, Query

from app.models.discount import DiscountResponse, SupermarketEnum

router = APIRouter()


@router.get(
    "/",
    response_model=list[DiscountResponse],
    summary="Get all current discounts",
)
async def get_all_discounts():
    """
    Retrieve current weekly discounts from ALL supported supermarkets.

    This endpoint returns discounts from both Albert Heijn and Jumbo,
    grouped by supermarket.

    Returns:
        list[DiscountResponse]: A list of discount collections,
            one per supermarket. Each contains the supermarket name,
            the week label, and the list of discounted items.

    Example Response:
        [
            {
                "supermarket": "albert_heijn",
                "total_items": 42,
                "week": "Week 2, 2025",
                "items": [...]
            },
            {
                "supermarket": "jumbo",
                "total_items": 38,
                "week": "Week 2, 2025",
                "items": [...]
            }
        ]
    """
    # TODO: Implement — call DiscountService to fetch from DB/scraper
    # For now, return empty placeholder data
    return [
        DiscountResponse(
            supermarket="albert_heijn",
            total_items=0,
            week="Coming soon",
            items=[],
        ),
        DiscountResponse(
            supermarket="jumbo",
            total_items=0,
            week="Coming soon",
            items=[],
        ),
    ]


@router.get(
    "/{supermarket}",
    response_model=DiscountResponse,
    summary="Get discounts for a specific supermarket",
)
async def get_discounts_by_supermarket(
    supermarket: SupermarketEnum,
):
    """
    Retrieve current weekly discounts for a SPECIFIC supermarket.

    Args:
        supermarket (SupermarketEnum):
            The supermarket to get discounts from.
            Must be "albert_heijn" or "jumbo".
            This value comes from the URL path.

    Returns:
        DiscountResponse: The discount collection for the specified
            supermarket, including the week label and list of items.

    Example:
        GET /api/discounts/albert_heijn
    """
    # TODO: Implement — call DiscountService for this specific supermarket
    return DiscountResponse(
        supermarket=supermarket.value,
        total_items=0,
        week="Coming soon",
        items=[],
    )


@router.post(
    "/refresh",
    summary="Trigger a fresh discount scrape",
)
async def refresh_discounts(
    supermarket: SupermarketEnum = Query(
        default=None,
        description="Specific supermarket to refresh (or all if not specified)",
    ),
):
    """
    Trigger a fresh scrape of supermarket discounts.

    This endpoint tells the backend to go out and fetch the latest
    discounts from the supermarket websites. Useful when:
    - The cached data is outdated
    - A new week of discounts has started
    - An admin wants to force a refresh

    Args:
        supermarket (SupermarketEnum | None):
            If provided, only refresh discounts from this supermarket.
            If None, refresh discounts from ALL supermarkets.

    Returns:
        dict: A status message indicating the refresh was triggered.
    """
    # TODO: Implement — trigger scraper for specified supermarket(s)
    target = supermarket.value if supermarket else "all supermarkets"
    return {
        "status": "refresh_triggered",
        "target": target,
        "message": f"Discount refresh triggered for {target}",
    }
