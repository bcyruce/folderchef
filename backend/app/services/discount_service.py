"""
FolderChef — Discount Service
================================

This module manages the discount data pipeline.

WHAT DOES THIS SERVICE DO?
    It orchestrates the full discount data flow:
    1. Trigger scrapers to fetch fresh discount data
    2. Use AI to clean and categorise the raw data
    3. Store the processed data in the database
    4. Serve cached data to API requests

CACHING STRATEGY:
    Supermarket discounts change weekly (usually on Monday).
    We don't need to scrape every time a user requests data.
    Instead:
    - Scrape once when new discounts are published
    - Cache in the database for the rest of the week
    - Only re-scrape when data is stale or manually triggered

DATA FLOW:
    Supermarket Website → Scraper → AI Cleaner → Database → API → User
"""

from typing import Optional

from app.models.discount import DiscountItem, DiscountResponse, SupermarketEnum
from app.scrapers.albert_heijn import AlbertHeijnScraper
from app.scrapers.jumbo import JumboScraper
from app.services.ai_service import AIService


class DiscountService:
    """
    Service for managing supermarket discount data.

    Handles scraping, cleaning, caching, and serving discount data.

    Attributes:
        ai_service (AIService): AI service for data cleaning/categorisation.
        scrapers (dict): Mapping of supermarket names to their scrapers.

    Usage:
        service = DiscountService()
        discounts = await service.get_discounts("albert_heijn")
    """

    def __init__(self):
        """
        Initialise the discount service.

        Sets up the AI service and creates scraper instances for
        each supported supermarket.
        """
        self.ai_service = AIService()
        self.scrapers = {
            SupermarketEnum.ALBERT_HEIJN: AlbertHeijnScraper(),
            SupermarketEnum.JUMBO: JumboScraper(),
        }

    async def get_discounts(
        self,
        supermarket: Optional[SupermarketEnum] = None,
    ) -> list[DiscountResponse]:
        """
        Get current discount data, either from cache or by scraping.

        This is the main method called by the API endpoints.

        Args:
            supermarket: Specific supermarket to get discounts from.
                         If None, returns discounts from ALL supermarkets.

        Returns:
            list[DiscountResponse]: Discount data grouped by supermarket.

        Example:
            # Get discounts from all supermarkets
            all_deals = await service.get_discounts()

            # Get only Albert Heijn discounts
            ah_deals = await service.get_discounts(SupermarketEnum.ALBERT_HEIJN)
        """
        # TODO: Implement with database caching
        # Steps:
        # 1. Check database for cached discounts (are they fresh?)
        # 2. If fresh, return cached data
        # 3. If stale, trigger scrape → clean → cache → return
        results = []

        targets = (
            [supermarket] if supermarket
            else list(self.scrapers.keys())
        )

        for target in targets:
            # TODO: Check cache first, then scrape if needed
            items = await self._scrape_and_clean(target)
            results.append(
                DiscountResponse(
                    supermarket=target.value,
                    total_items=len(items),
                    week="Current week",  # TODO: Calculate actual week
                    items=items,
                )
            )

        return results

    async def _scrape_and_clean(
        self,
        supermarket: SupermarketEnum,
    ) -> list[DiscountItem]:
        """
        Scrape fresh discount data and clean it with AI.

        This private method handles the actual scraping and AI cleaning.

        Args:
            supermarket: Which supermarket to scrape.

        Returns:
            list[DiscountItem]: Cleaned and categorised discount items.
        """
        scraper = self.scrapers.get(supermarket)
        if not scraper:
            print(f"⚠️  No scraper available for {supermarket.value}")
            return []

        try:
            # Step 1: Scrape raw data
            raw_items = await scraper.scrape()

            # Step 2: Clean and categorise with AI
            cleaned_items = await self.ai_service.categorise_items(raw_items)

            # Step 3: TODO — Save to database

            return cleaned_items

        except Exception as e:
            print(f"❌ Error scraping {supermarket.value}: {e}")
            return []

    async def refresh(
        self,
        supermarket: Optional[SupermarketEnum] = None,
    ) -> dict:
        """
        Force a fresh scrape of discount data.

        Ignores the cache and scrapes directly from the supermarket website.

        Args:
            supermarket: Specific supermarket to refresh, or None for all.

        Returns:
            dict: Summary of the refresh operation.
        """
        # TODO: Implement force refresh
        # This should:
        # 1. Clear cached data for the target supermarket(s)
        # 2. Run _scrape_and_clean() for each target
        # 3. Return a summary (items found, errors, etc.)
        return {"status": "not_implemented"}

    async def close(self):
        """
        Clean up all scraper connections.

        Call this when shutting down the application.
        """
        for scraper in self.scrapers.values():
            await scraper.close()
