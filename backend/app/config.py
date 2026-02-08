"""
FolderChef — Application Configuration
========================================

This module loads all configuration from environment variables (or a .env file).

WHY THIS EXISTS:
    - We never hard-code secrets (API keys, database URLs) in our code.
    - Instead, we store them in environment variables or a .env file.
    - This module reads those variables and makes them available as a
      simple Python object: `settings.DATABASE_URL`, `settings.OPENAI_API_KEY`, etc.

HOW TO USE:
    from app.config import settings

    print(settings.DATABASE_URL)
    print(settings.OPENAI_API_KEY)

HOW IT WORKS:
    - Pydantic's BaseSettings class automatically reads from environment
      variables AND from a .env file (if it exists).
    - If a required variable is missing, the app will refuse to start
      and tell you exactly which variable is missing.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Each attribute below corresponds to an environment variable.
    For example, `DATABASE_URL` reads the `DATABASE_URL` env var.

    Attributes:
        DATABASE_URL (str):
            PostgreSQL connection string.
            Example: "postgresql+asyncpg://user:pass@localhost:5432/folderchef"

        OPENAI_API_KEY (str):
            Your OpenAI API key for GPT-based recipe generation.

        ENVIRONMENT (str):
            Current environment. Either "development" or "production".
            Default: "development"

        DEBUG (bool):
            Whether to enable debug mode (detailed error messages).
            Default: True

        SECRET_KEY (str):
            Secret key used for signing tokens / sessions.
            Default: "change-me" (MUST be changed in production!)

        FRONTEND_URL (str):
            The URL of the frontend app (for CORS configuration).
            Default: "http://localhost:3000"
    """

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/folderchef"

    # --- AI / LLM ---
    OPENAI_API_KEY: str = ""

    # --- App ---
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me"

    # --- CORS ---
    FRONTEND_URL: str = "http://localhost:3000"

    # Tell Pydantic to also read from a .env file
    model_config = SettingsConfigDict(
        env_file=".env",          # Path to the .env file
        env_file_encoding="utf-8",
        case_sensitive=True,      # DATABASE_URL ≠ database_url
    )


# Create a single settings instance that the whole app shares.
# Import this in other files: `from app.config import settings`
settings = Settings()
