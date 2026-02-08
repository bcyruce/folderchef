"""
FolderChef — Database Connection
===================================

This module sets up the connection to the PostgreSQL database.

HOW IT WORKS:
    1. We create an "engine" — this is the connection to the database.
    2. We create a "session factory" — this creates individual sessions
       for each request (like opening a conversation with the database).
    3. We provide a `get_db()` function that FastAPI uses to give each
       API request its own database session.

WHY ASYNC?
    We use async (asynchronous) database operations because:
    - FastAPI is async, so the database should be too
    - Async means the server can handle other requests while waiting
      for the database to respond
    - This makes the app faster under load

SETUP ON RAILWAY:
    Railway automatically provides a DATABASE_URL environment variable
    when you add a PostgreSQL database to your project. Our config.py
    reads this variable, and this module uses it to connect.

LOCAL DEVELOPMENT:
    For local development, you can:
    1. Install PostgreSQL locally
    2. Create a database called "folderchef"
    3. Set DATABASE_URL in your .env file
    OR
    4. Use the Railway CLI to connect to the cloud database
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# ------------------------------------------------------------------
# Database Engine
# ------------------------------------------------------------------
# The engine is the starting point for all database operations.
# It manages the connection pool (a set of reusable connections).
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,   # If DEBUG=True, print all SQL queries (helpful for learning!)
    pool_size=5,           # Keep 5 connections open at all times
    max_overflow=10,       # Allow up to 10 extra connections during high traffic
)


# ------------------------------------------------------------------
# Session Factory
# ------------------------------------------------------------------
# A session is a "conversation" with the database.
# Each API request gets its own session.
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
)


# ------------------------------------------------------------------
# Base Model Class
# ------------------------------------------------------------------
class Base(DeclarativeBase):
    """
    Base class for all database models (tables).

    All database table classes should inherit from this Base class.
    SQLAlchemy uses this to know which classes represent tables.

    Example:
        class DiscountTable(Base):
            __tablename__ = "discounts"
            id = Column(Integer, primary_key=True)
            name = Column(String)
    """
    pass


# ------------------------------------------------------------------
# Dependency: Get Database Session
# ------------------------------------------------------------------
async def get_db() -> AsyncSession:
    """
    FastAPI dependency that provides a database session.

    This is used in API endpoints to get a database session:

        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # Use 'db' to query the database
            ...

    The session is automatically closed when the request is done.

    Yields:
        AsyncSession: An async database session.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()   # Save changes if everything went well
        except Exception:
            await session.rollback()  # Undo changes if something went wrong
            raise
        finally:
            await session.close()     # Always close the session


async def init_db():
    """
    Initialise the database — create all tables.

    Call this once during app startup to create the database tables
    if they don't exist yet.

    NOTE:
        In production, use Alembic migrations instead of this function.
        Alembic can safely update table schemas without losing data.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")


async def close_db():
    """
    Close the database engine and all connections.

    Call this during app shutdown to cleanly release resources.
    """
    await engine.dispose()
    print("🔌 Database connections closed")
