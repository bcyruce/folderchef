"""
FolderChef — Database Package
================================

This package handles all database operations.

DATABASE OVERVIEW:
    FolderChef uses PostgreSQL as its database, accessed via SQLAlchemy
    (an ORM — Object Relational Mapper).

    An ORM lets us work with database tables as Python objects instead
    of writing raw SQL queries. This makes the code:
    - Easier to read and write
    - Safer (prevents SQL injection attacks)
    - Portable (could switch databases if needed)

MODULES:
    - connection.py → Database connection setup and session management

WHY POSTGRESQL?
    1. Railway provides PostgreSQL databases out of the box
    2. It's reliable, fast, and free for small projects
    3. It supports JSON columns (useful for recipe data)
    4. It scales well as the app grows

TABLES (planned):
    - discounts     → Cached supermarket discount items
    - recipes       → AI-generated recipes
    - users         → User accounts (future)
    - favourites    → User's favourite recipes (future)
"""
