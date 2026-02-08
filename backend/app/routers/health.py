"""
FolderChef — Health Check Router
===================================

This module provides a simple health check endpoint.

WHY DO WE NEED THIS?
    - Railway (our hosting platform) pings this endpoint to check if
      the server is alive and responding.
    - If this endpoint stops responding, Railway knows something is
      wrong and can restart the server.
    - It's also useful during development to quickly verify the API is running.

ENDPOINT:
    GET /api/health → Returns {"status": "healthy"}
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Railway and monitoring tools call this endpoint to verify the
    server is running and responsive.

    Returns:
        dict: A simple status object.
            - status (str): "healthy" if everything is OK.
            - service (str): The name of this service.
            - version (str): The current API version.
    """
    return {
        "status": "healthy",
        "service": "folderchef-api",
        "version": "0.1.0",
    }
