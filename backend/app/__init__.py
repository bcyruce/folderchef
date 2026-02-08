"""
FolderChef Backend Application Package
=======================================

This is the main Python package for the FolderChef backend.

The backend is built with FastAPI and is responsible for:
    - Scraping weekly discounts from Dutch supermarkets (Albert Heijn, Jumbo)
    - Cleaning and structuring the discount data using AI
    - Generating optimised, budget-friendly recipes using AI
    - Serving all data through a REST API (used by web + future mobile apps)

Package Structure:
    - main.py       → The FastAPI app entry point
    - config.py     → App settings loaded from environment variables
    - models/       → Pydantic data models (what our data looks like)
    - routers/      → API endpoint definitions (the URLs users can call)
    - scrapers/     → Web scrapers for supermarket discounts
    - services/     → Business logic (AI, recipes, discount processing)
    - database/     → Database connection and query helpers
"""
