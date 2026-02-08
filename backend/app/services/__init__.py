"""
FolderChef — Services Package
================================

This package contains the business logic layer of the application.

WHAT ARE SERVICES?
    Services contain the "brains" of the application — the actual logic
    that makes FolderChef work. They sit between the API endpoints
    (routers) and the data layer (database/scrapers).

    Think of it like a restaurant:
    - Routers = the waiter (takes orders from customers)
    - Services = the chef (does the actual cooking)
    - Database/Scrapers = the pantry (where ingredients come from)

MODULES:
    - ai_service.py        → Talks to OpenAI to generate recipes
    - discount_service.py   → Manages discount data (scraping + caching)
    - recipe_service.py     → Orchestrates recipe generation

WHY SEPARATE FROM ROUTERS?
    1. Reusability — Services can be used by multiple routers
    2. Testability — Services can be tested without HTTP
    3. Clarity — Routers handle HTTP, services handle logic
    4. Mobile-ready — Same services power web + future mobile API
"""

from app.services.ai_service import AIService
from app.services.discount_service import DiscountService
from app.services.recipe_service import RecipeService

__all__ = [
    "AIService",
    "DiscountService",
    "RecipeService",
]
