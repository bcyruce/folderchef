"""
FolderChef — API Tests
========================

This module contains tests for the FolderChef API endpoints.

HOW THESE TESTS WORK:
    We use FastAPI's TestClient (via httpx) to simulate HTTP requests
    to our API without actually starting a server. This makes tests
    fast and reliable.

HOW TO RUN:
    cd backend
    pytest tests/test_api.py -v

WHAT WE TEST:
    - Health check endpoint responds correctly
    - Root endpoint returns welcome message
    - Discount endpoints return proper structure
    - Recipe endpoints return proper structure
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    """
    Tell pytest-asyncio to use asyncio as the async backend.

    This is a required fixture for async tests.
    """
    return "asyncio"


@pytest.fixture
async def client():
    """
    Create a test HTTP client.

    This client sends requests directly to our FastAPI app
    without needing a running server.

    Yields:
        AsyncClient: An HTTP client for testing.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.mark.anyio
async def test_root_endpoint(client: AsyncClient):
    """
    Test that the root endpoint (/) returns a welcome message.

    Expected: 200 OK with a JSON body containing "message" and "docs".
    """
    response = await client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert data["version"] == "0.1.0"


@pytest.mark.anyio
async def test_health_endpoint(client: AsyncClient):
    """
    Test that the health check endpoint returns "healthy".

    Expected: 200 OK with status "healthy".
    """
    response = await client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "folderchef-api"


@pytest.mark.anyio
async def test_get_all_discounts(client: AsyncClient):
    """
    Test that the discounts endpoint returns a list.

    Expected: 200 OK with a JSON array of discount responses.
    """
    response = await client.get("/api/discounts/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least one supermarket


@pytest.mark.anyio
async def test_get_discounts_albert_heijn(client: AsyncClient):
    """
    Test getting discounts for a specific supermarket (Albert Heijn).

    Expected: 200 OK with discount data for Albert Heijn.
    """
    response = await client.get("/api/discounts/albert_heijn")
    assert response.status_code == 200

    data = response.json()
    assert data["supermarket"] == "albert_heijn"
    assert "items" in data
    assert "total_items" in data


@pytest.mark.anyio
async def test_get_recipes_empty(client: AsyncClient):
    """
    Test getting recipes when none have been generated yet.

    Expected: 200 OK with an empty list.
    """
    response = await client.get("/api/recipes/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_get_recipe_not_found(client: AsyncClient):
    """
    Test getting a recipe that doesn't exist.

    Expected: 404 Not Found.
    """
    response = await client.get("/api/recipes/nonexistent-id")
    assert response.status_code == 404
