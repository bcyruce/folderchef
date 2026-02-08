"""
FolderChef -- Application Configuration
========================================

Loads settings from environment variables or a .env file.

LOCAL DEVELOPMENT:
    Uses SQLite by default (no database server needed).
    Just a file called 'folderchef.db' in the backend folder.

PRODUCTION (Railway):
    Uses PostgreSQL. Railway provides DATABASE_URL automatically
    when you add a PostgreSQL service.

HOW TO USE:
    from app.config import settings
    print(settings.DATABASE_URL)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        DATABASE_URL (str):
            Database connection string.
            Default: SQLite file for local development.
            Railway sets this to a PostgreSQL URL in production.

        OPENAI_API_KEY (str):
            Your OpenAI API key for AI cleaning and recipe generation.

        ENVIRONMENT (str):
            "development" or "production". Default: "development"

        DEBUG (bool):
            Show detailed errors and SQL queries. Default: True

        SECRET_KEY (str):
            Secret key for signing tokens. Change in production!

        FRONTEND_URL (str):
            Frontend URL for CORS. Default: "http://localhost:3000"
    """

    # --- Database ---
    # Default to SQLite for local dev (no server needed!)
    # On Railway, set this to: postgresql+asyncpg://...
    DATABASE_URL: str = "sqlite+aiosqlite:///./folderchef.db"

    # --- AI / LLM ---
    OPENAI_API_KEY: str = ""

    # --- App ---
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me"

    # --- CORS ---
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


_settings = Settings()

# Railway provides DATABASE_URL as "postgresql://..." but SQLAlchemy's
# async engine needs "postgresql+asyncpg://...". Auto-convert it.
if _settings.DATABASE_URL.startswith("postgresql://"):
    _settings.DATABASE_URL = _settings.DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )

settings = _settings
