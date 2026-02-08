"""
FolderChef -- Albert Heijn Scraper
====================================

Fetches weekly "Bonus" discount products from Albert Heijn using their
mobile API.

HOW IT WORKS:
    1. Get an anonymous access token from AH's auth endpoint
    2. Use the token to call the product search API with bonus filter
    3. Parse each product into a RawDiscount object

AH API DETAILS (reverse-engineered from the AH mobile app):
    Auth:    POST https://api.ah.nl/mobile-auth/v1/auth/token/anonymous
    Search:  GET  https://api.ah.nl/mobile-services/product/search/v2
    Headers: User-Agent must mimic the AH "Appie" mobile app

FIELDS WE EXTRACT:
    - name                   --> product title
    - original_price         --> priceBeforeBonus
    - discount_price_per_unit --> calculated from bonusMechanism + prices
    - discount_info          --> bonusMechanism (e.g. "1+1 GRATIS")
    - weight                 --> salesUnitSize (e.g. "500 gram")
    - price_per_kg           --> parsed from unitPriceDescription
    - start_date / end_date  --> bonusStartDate / bonusEndDate
    - image_url              --> first image URL
"""

import re
from datetime import date, datetime
from typing import Optional

import httpx

from app.models.discount import RawDiscount
from app.scrapers.base import BaseScraper


class AlbertHeijnScraper(BaseScraper):
    """
    Scraper for Albert Heijn weekly Bonus discounts.

    Uses AH's mobile API to fetch all products currently on bonus.

    Usage:
        scraper = AlbertHeijnScraper()
        products = await scraper.scrape()
        for p in products:
            print(f"{p.name}: {p.discount_info} -- EUR {p.discount_price_per_unit}")
        await scraper.close()
    """

    # AH API endpoints
    AUTH_URL = "https://api.ah.nl/mobile-auth/v1/auth/token/anonymous"
    SEARCH_URL = "https://api.ah.nl/mobile-services/product/search/v2"

    def __init__(self):
        super().__init__(
            supermarket_name="Albert Heijn",
            base_url="https://api.ah.nl",
        )
        self._token: Optional[str] = None

    def get_url(self) -> str:
        """Return the search API URL."""
        return self.SEARCH_URL

    def get_headers(self) -> dict:
        """
        Headers that mimic the official AH 'Appie' mobile app.

        The User-Agent is important -- AH may block requests that
        don't look like they come from the app.
        """
        headers = {
            "User-Agent": "Appie/8.22.3",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-application": "AHWEBSHOP",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    async def _get_anonymous_token(self) -> str:
        """
        Get an anonymous access token from AH's auth API.

        This token allows us to call the product APIs without
        a user account. It expires after some time.

        Returns:
            str: The access token string.

        Raises:
            httpx.HTTPError: If the auth request fails.
        """
        client = await self._get_client()
        response = await client.post(
            self.AUTH_URL,
            json={"clientId": "appie"},
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token", "")
        print(f"  Got AH anonymous token (length: {len(token)})")
        return token

    async def scrape(self) -> list[RawDiscount]:
        """
        Fetch ALL current Bonus products from Albert Heijn.

        Steps:
            1. Get anonymous auth token
            2. Search for bonus products, paginating through all results
            3. Parse each product into a RawDiscount

        Returns:
            list[RawDiscount]: All bonus products found.
        """
        print("Scraping Albert Heijn bonus products...")

        # Step 1: Authenticate
        self._token = await self._get_anonymous_token()

        # Update client headers with the new token
        if self._client:
            await self._client.aclose()
            self._client = None

        # Step 2: Fetch bonus products (paginated)
        all_products: list[RawDiscount] = []
        page = 0
        page_size = 750
        skipped = 0

        while True:
            print(f"  Fetching page {page}...")
            client = await self._get_client()

            params = {
                "page": page,
                "size": page_size,
                "query": "",
                "bonus": "BONUS",
                "sortOn": "RELEVANCE",
            }

            try:
                response = await client.get(self.SEARCH_URL, params=params)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"  Error fetching page {page}: {e}")
                break

            products_data = data.get("products", [])
            if not products_data:
                print(f"  No more products on page {page}")
                break

            # IMPORTANT: Only keep products that are actually on bonus
            # The API may return non-bonus items too. We filter on
            # isBonus, isBonusPrice, or the presence of bonusMechanism.
            for product in products_data:
                is_bonus = (
                    product.get("isBonus") is True
                    or product.get("isBonusPrice") is True
                    or product.get("bonusMechanism")
                )
                if not is_bonus:
                    skipped += 1
                    continue

                parsed = self._parse_product(product)
                if parsed:
                    all_products.append(parsed)

            print(f"  Page {page}: {len(products_data)} returned, {len(all_products)} bonus so far")

            # Check if there are more pages
            page_info = data.get("page", {})
            total_pages = page_info.get("totalPages", 1)

            page += 1
            if page >= total_pages:
                break

        print(f"  Albert Heijn: {len(all_products)} bonus products ({skipped} non-bonus skipped)")
        return all_products

    def _parse_product(self, product: dict) -> Optional[RawDiscount]:
        """
        Parse a single AH API product object into a RawDiscount.

        Args:
            product: A product dictionary from the AH search API.

        Returns:
            RawDiscount if parsing succeeds, None if the product
            should be skipped (e.g. missing essential fields).
        """
        try:
            # --- Name ---
            name = product.get("title", "").strip()
            if not name:
                return None

            # --- Prices ---
            original_price = product.get("priceBeforeBonus")
            current_price = product.get("currentPrice")

            # --- Discount info ---
            discount_info = product.get("bonusMechanism", "")
            if not discount_info:
                # Try alternative field names
                discount_info = product.get("discountDescription", "BONUS")

            # --- Calculate discount price per unit ---
            discount_price_per_unit = self._calculate_unit_price(
                original_price=original_price,
                current_price=current_price,
                discount_info=discount_info,
            )

            # --- Weight / size ---
            weight = product.get("salesUnitSize", None)

            # --- Price per kg ---
            price_per_kg = self._parse_price_per_kg(
                product.get("unitPriceDescription", "")
            )

            # --- Dates ---
            start_date = self._parse_date(product.get("bonusStartDate"))
            end_date = self._parse_date(product.get("bonusEndDate"))

            # --- Image ---
            images = product.get("images", [])
            image_url = None
            if images:
                # Pick the largest image available
                largest = max(images, key=lambda img: img.get("width", 0))
                image_url = largest.get("url")

            return RawDiscount(
                name=name,
                supermarket="albert_heijn",
                original_price=original_price,
                discount_price_per_unit=discount_price_per_unit,
                discount_info=discount_info,
                weight=weight,
                price_per_kg=price_per_kg,
                start_date=start_date,
                end_date=end_date,
                image_url=image_url,
            )

        except Exception as e:
            print(f"  Warning: could not parse product: {e}")
            return None

    def _calculate_unit_price(
        self,
        original_price: Optional[float],
        current_price: Optional[float],
        discount_info: str,
    ) -> Optional[float]:
        """
        Calculate the effective price per unit after the discount.

        Handles Dutch discount formats:
            - "1+1 GRATIS"       --> price / 2
            - "2+1 GRATIS"       --> (price * 2) / 3
            - "2e HALVE PRIJS"   --> price * 0.75
            - "2 VOOR 3.00"      --> 3.00 / 2
            - "3 VOOR 5.00"      --> 5.00 / 3
            - "30% KORTING"      --> price * 0.70
            - Direct price       --> currentPrice

        Args:
            original_price: Regular price of one unit.
            current_price: Current selling price (may already be discounted).
            discount_info: The discount description string.

        Returns:
            The calculated price per unit, or None if it cannot be determined.
        """
        info = discount_info.upper().strip()
        price = original_price or current_price

        if not price and not current_price:
            return None

        # "1+1 GRATIS" or "1 + 1 GRATIS"
        match = re.match(r"(\d)\s*\+\s*(\d)\s*GRATIS", info)
        if match:
            buy = int(match.group(1))
            free = int(match.group(2))
            if price:
                return round(price * buy / (buy + free), 2)

        # "2e HALVE PRIJS" (second half price)
        if "HALVE PRIJS" in info:
            if price:
                return round(price * 0.75, 2)

        # "2 VOOR 3.00" or "3 VOOR 5.00"
        match = re.match(r"(\d+)\s*VOOR\s*([\d.,]+)", info)
        if match:
            count = int(match.group(1))
            total = float(match.group(2).replace(",", "."))
            return round(total / count, 2)

        # "30% KORTING"
        match = re.match(r"(\d+)%\s*KORTING", info)
        if match:
            pct = int(match.group(1))
            if price:
                return round(price * (100 - pct) / 100, 2)

        # "EURO KORTING" e.g. "1.00 KORTING"
        match = re.match(r"([\d.,]+)\s*KORTING", info)
        if match:
            discount_amount = float(match.group(1).replace(",", "."))
            if price:
                return round(price - discount_amount, 2)

        # Fallback: use currentPrice directly
        if current_price is not None:
            return current_price

        return None

    def _parse_price_per_kg(self, unit_desc: str) -> Optional[float]:
        """
        Extract price per kg from the unitPriceDescription string.

        AH format examples:
            "normale prijs per kg EUR 6.36"
            "prijs per kg EUR 12.50"
            "per kg 8.99"

        Args:
            unit_desc: The unit price description from AH.

        Returns:
            Price per kg as float, or None if not parseable.
        """
        if not unit_desc:
            return None

        # Look for a price pattern after "kg"
        match = re.search(r"(?:per\s*kg|per\s*kilo)[^\d]*([\d]+[.,][\d]+)", unit_desc, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", "."))

        # Try pattern: "EUR X.XX" after "kg"
        match = re.search(r"kg.*?(?:EUR|€)\s*([\d]+[.,][\d]+)", unit_desc, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", "."))

        return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """
        Parse a date string from the AH API.

        AH uses ISO format: "2026-02-03"

        Args:
            date_str: Date string or None.

        Returns:
            date object or None.
        """
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    async def parse_discounts(self, raw_data: str) -> list[RawDiscount]:
        """
        Not used -- this scraper overrides scrape() directly.

        The AH scraper uses the API (JSON) rather than HTML parsing,
        so the base class scrape() flow is replaced entirely.
        """
        return []
