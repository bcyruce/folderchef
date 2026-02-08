"""
FolderChef — Scrapers Package
================================

This package contains web scrapers for Dutch supermarket discount data.

WHAT ARE SCRAPERS?
    Scrapers are programs that automatically visit websites, read the
    HTML content, and extract structured data from them. In our case,
    we scrape discount/aanbieding (offer) pages from:

    - Albert Heijn (ah.nl)
    - Jumbo (jumbo.com)

HOW IT WORKS:
    1. The scraper sends an HTTP request to the supermarket's website or API
    2. It receives HTML or JSON data back
    3. It parses the data to extract product names, prices, discounts, etc.
    4. It returns a list of DiscountItem objects

ARCHITECTURE:
    - base.py          → BaseScraper class (shared logic for all scrapers)
    - albert_heijn.py  → Albert Heijn specific scraper
    - jumbo.py         → Jumbo specific scraper

    Each supermarket scraper extends BaseScraper and implements the
    specific logic for that supermarket's website structure.

IMPORTANT:
    Web scraping should be done responsibly:
    - Respect rate limits (don't send too many requests)
    - Check robots.txt
    - Cache results to avoid unnecessary requests
    - Consider using official APIs when available
"""

from app.scrapers.base import BaseScraper
from app.scrapers.albert_heijn import AlbertHeijnScraper
from app.scrapers.jumbo import JumboScraper

__all__ = [
    "BaseScraper",
    "AlbertHeijnScraper",
    "JumboScraper",
]
