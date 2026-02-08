"""
FolderChef -- Jumbo Scraper
=============================

Scrapes weekly discount data from Jumbo supermarket.

STATUS: Not yet implemented.
Jumbo uses a GraphQL API at https://www.jumbo.com/api/graphql
This will be implemented in a future iteration.
"""

from app.models.discount import RawDiscount
from app.scrapers.base import BaseScraper


class JumboScraper(BaseScraper):
    """
    Scraper for Jumbo weekly discounts.

    TODO: Implement using Jumbo's GraphQL API.
    """

    def __init__(self):
        super().__init__(
            supermarket_name="Jumbo",
            base_url="https://www.jumbo.com",
        )

    def get_url(self) -> str:
        return f"{self.base_url}/api/graphql"

    async def scrape(self) -> list[RawDiscount]:
        """Jumbo scraper -- not yet implemented."""
        print("Jumbo scraper not yet implemented")
        return []
