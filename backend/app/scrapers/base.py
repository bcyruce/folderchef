"""
FolderChef -- Base Scraper
============================

Abstract base class that all supermarket scrapers inherit from.

Shared behaviour:
    - HTTP client management (reusable connections)
    - Default headers (mimic a browser/app)
    - Error handling pattern

Each supermarket scraper (Albert Heijn, Jumbo) extends this and
implements its own scraping logic.
"""

from abc import ABC, abstractmethod
from typing import Optional

import httpx

from app.models.discount import RawDiscount


class BaseScraper(ABC):
    """
    Abstract base class for supermarket scrapers.

    Subclasses MUST implement:
        - scrape() or parse_discounts()
        - get_url()

    Attributes:
        supermarket_name: Human-readable name (e.g. "Albert Heijn").
        base_url: Base URL of the supermarket API/website.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        supermarket_name: str,
        base_url: str,
        timeout: int = 30,
    ):
        self.supermarket_name = supermarket_name
        self.base_url = base_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create a reusable async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.get_headers(),
                follow_redirects=True,
            )
        return self._client

    def get_headers(self) -> dict:
        """Default HTTP headers. Override in subclasses for custom headers."""
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/json",
            "Accept-Language": "nl-NL,nl;q=0.9,en;q=0.8",
        }

    @abstractmethod
    def get_url(self) -> str:
        """Return the URL to scrape. Subclasses must implement."""
        ...

    @abstractmethod
    async def scrape(self) -> list[RawDiscount]:
        """
        Execute the full scraping flow and return raw discount items.

        Subclasses must implement the actual scraping logic.

        Returns:
            list[RawDiscount]: Scraped discount products.
        """
        ...

    async def parse_discounts(self, raw_data: str) -> list[RawDiscount]:
        """
        Parse raw HTML/JSON into RawDiscount objects.

        Override in subclasses that use the default scrape() flow.
        Some scrapers (like AH) override scrape() entirely instead.
        """
        return []

    async def close(self):
        """Close the HTTP client and release resources."""
        if self._client:
            await self._client.aclose()
            self._client = None
