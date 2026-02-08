"""
FolderChef -- Services Package
================================

Business logic layer. Sits between routers (HTTP) and data (DB/scrapers).

Modules:
    - ai_service.py        -- OpenAI integration (cleaning + recipes)
    - discount_service.py  -- Full discount pipeline (scrape -> clean -> store)
    - recipe_service.py    -- Recipe generation orchestrator
"""

from app.services.ai_service import AIService
from app.services.discount_service import DiscountService
from app.services.recipe_service import RecipeService

__all__ = [
    "AIService",
    "DiscountService",
    "RecipeService",
]
