"""
FolderChef — Main Application Entry Point
===========================================

This is the heart of the FolderChef backend. When you run the server,
this is the file that starts everything up.

WHAT THIS FILE DOES:
    1. Creates the FastAPI application
    2. Configures CORS (so the frontend can talk to the backend)
    3. Registers all API routers (groups of endpoints)
    4. Sets up startup/shutdown events (e.g., database connections)

HOW TO RUN:
    uvicorn app.main:app --reload

    Then open http://localhost:8000/docs to see the interactive API docs.

ARCHITECTURE NOTE:
    This backend serves a REST API that is used by:
    - The Next.js web frontend (current)
    - Future iOS app
    - Future Android app
    All clients use the exact same API endpoints.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import discounts, recipes, health


# ------------------------------------------------------------------
# Application Lifespan (startup & shutdown)
# ------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application's startup and shutdown lifecycle.

    This function runs:
        - BEFORE the app starts accepting requests (startup)
        - AFTER the app stops accepting requests (shutdown)

    Use this for:
        - Connecting to the database on startup
        - Closing the database connection on shutdown
        - Starting/stopping background tasks (like the scraper scheduler)

    Args:
        app: The FastAPI application instance.

    Yields:
        None — the app runs between the startup and shutdown phases.
    """
    # === STARTUP ===
    # TODO: Initialize database connection pool
    # TODO: Start the discount scraper scheduler
    print("🚀 FolderChef backend is starting up...")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Debug mode:  {settings.DEBUG}")

    yield  # <<< The app runs here, handling requests

    # === SHUTDOWN ===
    # TODO: Close database connection pool
    # TODO: Stop the scheduler
    print("👋 FolderChef backend is shutting down...")


# ------------------------------------------------------------------
# Create the FastAPI Application
# ------------------------------------------------------------------
app = FastAPI(
    title="FolderChef API",
    description=(
        "AI-Powered Reverse Meal Planner for the Dutch market. "
        "Generates budget-friendly recipes from weekly supermarket discounts."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",        # Swagger UI at /docs
    redoc_url="/redoc",      # ReDoc at /redoc
)


# ------------------------------------------------------------------
# CORS Middleware
# ------------------------------------------------------------------
# CORS = Cross-Origin Resource Sharing
# This allows our frontend (running on localhost:3000) to make
# requests to our backend (running on localhost:8000).
# Without this, the browser would block the requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,    # e.g., "http://localhost:3000"
        "http://localhost:3000",   # Always allow local dev
    ],
    allow_credentials=True,       # Allow cookies to be sent
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)


# ------------------------------------------------------------------
# Register Routers (groups of API endpoints)
# ------------------------------------------------------------------
# Each router handles a specific area of the API.
# The prefix means all endpoints in that router start with that path.
# For example, the discounts router at prefix="/api/discounts" means
# its endpoints are at /api/discounts, /api/discounts/{id}, etc.
app.include_router(
    health.router,
    prefix="/api",
    tags=["Health"],
)

app.include_router(
    discounts.router,
    prefix="/api/discounts",
    tags=["Discounts"],
)

app.include_router(
    recipes.router,
    prefix="/api/recipes",
    tags=["Recipes"],
)


# ------------------------------------------------------------------
# Root Endpoint
# ------------------------------------------------------------------
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint — returns a welcome message.

    This is a simple endpoint to verify the API is running.
    Visit http://localhost:8000/ to see it.

    Returns:
        dict: A welcome message with a link to the docs.
    """
    return {
        "message": "Welcome to the FolderChef API! 🍳",
        "docs": "/docs",
        "version": "0.1.0",
    }
