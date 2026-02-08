"""
FolderChef -- Scrapers Package
================================

Web scrapers for Dutch supermarket discount data.

Modules:
    - base.py          -- BaseScraper abstract class
    - albert_heijn.py  -- Albert Heijn Bonus scraper (uses AH mobile API)
    - jumbo.py         -- Jumbo scraper (to be implemented)
"""

from app.scrapers.base import BaseScraper
from app.scrapers.albert_heijn import AlbertHeijnScraper
from app.scrapers.jumbo import JumboScraper

__all__ = [
    "BaseScraper",
    "AlbertHeijnScraper",
    "JumboScraper",
]
