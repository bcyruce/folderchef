"""
FolderChef -- Database Connection
===================================

Sets up the database engine and session factory.

SUPPORTS BOTH:
    - SQLite   (local development -- no server needed)
    - PostgreSQL (production on Railway)

The DATABASE_URL in your .env (or env var) controls which one is used.

    SQLite:     sqlite+aiosqlite:///./folderchef.db
    PostgreSQL: postgresql+asyncpg://user:pass@host:5432/folderchef
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# ------------------------------------------------------------------
# Detect database type and configure engine accordingly
# ------------------------------------------------------------------
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs = {
    "echo": settings.DEBUG,
}

# SQLite does not support pool_size / max_overflow
if not is_sqlite:
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)


# ------------------------------------------------------------------
# Session Factory
# ------------------------------------------------------------------
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ------------------------------------------------------------------
# Base class for all ORM table models
# ------------------------------------------------------------------
class Base(DeclarativeBase):
    """
    Base class for all database table definitions.

    Every table class in database/tables.py inherits from this.
    SQLAlchemy uses it to track which classes represent database tables.
    """
    pass


# ------------------------------------------------------------------
# FastAPI dependency -- gives each request a database session
# ------------------------------------------------------------------
async def get_db():
    """
    Provide a database session for a single API request.

    Usage in a router:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...

    The session auto-commits on success, rolls back on error,
    and always closes when done.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Create all database tables if they don't exist yet.

    Called once during app startup.
    """
    # Import tables so SQLAlchemy knows about them
    import app.database.tables  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created")


async def close_db():
    """Close the database engine and release connections."""
    await engine.dispose()
    print("Database connections closed")
