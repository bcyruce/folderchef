"""
FolderChef — API Routers Package
==================================

This package contains all API route definitions (endpoints).

WHAT ARE ROUTERS?
    Routers are groups of related API endpoints. Instead of putting
    all endpoints in one huge file, we split them into logical groups:

    - health.py     → Health check endpoint (is the server alive?)
    - discounts.py  → Endpoints for fetching supermarket discounts
    - recipes.py    → Endpoints for generating and retrieving recipes

HOW ROUTERS WORK:
    Each router file creates an `APIRouter` object and defines endpoints
    on it. Then, in main.py, we "include" each router into the main app.

    This is similar to how a restaurant menu is split into sections
    (appetisers, mains, desserts) — each section has its own page,
    but they're all part of the same menu.
"""
