"""
FolderChef — Base Scraper
============================

This module defines the base class that ALL supermarket scrapers inherit from.

WHY A BASE CLASS?
    All scrapers share common behaviour:
    - Making HTTP requests
    - Handling errors and retries
    - Rate limiting (not hitting the server too fast)
    - Logging what's happening

    Instead of duplicating this code in every scraper, we put it in
    a base class. Each specific scraper (Albert Heijn, Jumbo) then
    only needs to implement the parts that are unique to that supermarket.

DESIGN PATTERN:
    This uses the "Template Method" pattern:
    - BaseScraper defines the overall scraping flow
    - Subclasses implement the specific parsing logic

HOW TO CREATE A NEW SCRAPER:
    1. Create a new file (e.g., lidl.py)
    2. Create a class that extends BaseScraper
    3. Implement the `parse_discounts()` method
    4. Register it in __init__.py
"""

from abc import ABC, abstractmethod
from typing import Optional

import httpx

from app.models.discount import DiscountItem


class BaseScraper(ABC):
    """
    Abstract base class for all supermarket scrapers.

    Subclasses MUST implement:
        - parse_discounts(): Parse the raw data into DiscountItem objects

    Subclasses CAN override:
        - get_headers(): Custom HTTP headers for requests
        - get_url(): The URL to scrape

    Attributes:
        supermarket_name (str): Human-readable name of the supermarket.
        base_url (str): The base URL of the supermarket's website.
        timeout (int): HTTP request timeout in seconds.
        _client (httpx.AsyncClient | None): Reusable HTTP client.

    Example Usage:
        scraper = AlbertHeijnScraper()
        discounts = await scraper.scrape()
        print(f"Found {len(discounts)} discounts!")
    """

    def __init__(
        self,
        supermarket_name: str,
        base_url: str,
        timeout: int = 30,
    ):
        """
        Initialise the base scraper.

        Args:
            supermarket_name: Human-readable supermarket name (e.g., "Albert Heijn").
            base_url: The base URL of the supermarket website.
            timeout: How many seconds to wait for HTTP responses. Default: 30.
        """
        self.supermarket_name = supermarket_name
        self.base_url = base_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create a reusable HTTP client.

        We reuse the same client for multiple requests because:
        - It keeps connections alive (faster)
        - It shares cookies between requests
        - It's more efficient than creating a new client each time

        Returns:
            httpx.AsyncClient: An async HTTP client ready to make requests.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.get_headers(),
                follow_redirects=True,
            )
        return self._client

    def get_headers(self) -> dict:
        """
        Get HTTP headers for requests.

        Override this in subclasses to add supermarket-specific headers.
        The default headers mimic a regular web browser to avoid being blocked.

        Returns:
            dict: HTTP headers to include in every request.
        """
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
        """
        Get the URL to scrape for discount data.

        Each supermarket has a different URL structure for their
        discount/aanbieding page. Subclasses MUST implement this.

        Returns:
            str: The full URL to fetch discount data from.
        """
        ...

    @abstractmethod
    async def parse_discounts(self, raw_data: str) -> list[DiscountItem]:
        """
        Parse raw HTML/JSON data into a list of DiscountItem objects.

        This is where the supermarket-specific parsing logic lives.
        Each supermarket structures their website differently, so
        each scraper needs its own parsing implementation.

        Args:
            raw_data: The raw HTML or JSON string from the website.

        Returns:
            list[DiscountItem]: A list of parsed discount items.
        """
        ...

    async def scrape(self) -> list[DiscountItem]:
        """
        Execute the full scraping flow.

        This is the main method to call. It:
        1. Builds the URL
        2. Sends the HTTP request
        3. Passes the response to parse_discounts()
        4. Returns the parsed discount items

        Returns:
            list[DiscountItem]: All discounted items found.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
            Exception: If parsing fails.
        """
        url = self.get_url()
        print(f"🔍 Scraping {self.supermarket_name} discounts from: {url}")

        client = await self._get_client()
        response = await client.get(url)
        response.raise_for_status()  # Raise error if status code is 4xx/5xx

        raw_data = response.text
        discounts = await self.parse_discounts(raw_data)

        print(f"✅ Found {len(discounts)} discounts from {self.supermarket_name}")
        return discounts

    async def close(self):
        """
        Close the HTTP client and release resources.

        Always call this when you're done scraping to free up
        network connections.
        """
        if self._client:
            await self._client.aclose()
            self._client = None
