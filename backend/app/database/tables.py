"""
FolderChef -- Database Table Definitions
==========================================

This module defines the actual database tables using SQLAlchemy ORM.

TABLES:
    1. raw_discounts    -- Stores scraped data exactly as it came from the supermarket
    2. cleaned_products -- Stores AI-cleaned data with common names and labels

WHY TWO TABLES?
    We keep the raw data separate from the cleaned data so we can:
    - Re-run the AI cleaning without re-scraping
    - Debug issues by comparing raw vs cleaned
    - Track what the AI changed

RELATIONSHIPS:
    Each cleaned_product links back to its raw_discount via raw_discount_id.
"""

from datetime import date, datetime

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Float,
    String,
    Date,
    DateTime,
    Text,
    ForeignKey,
    func,
)

from app.database.connection import Base


class RawDiscountTable(Base):
    """
    Database table for raw scraped discount data.

    Stores the product data exactly as scraped from the supermarket
    website, before any AI processing.

    Columns:
        id              -- Auto-incrementing primary key
        batch_name      -- Batch identifier e.g. "albert_heijn_bonus_w06_2026"
        week            -- ISO week number (1-53)
        year            -- Year (e.g. 2026)
        name            -- Product name from supermarket
        supermarket     -- "albert_heijn" or "jumbo"
        original_price  -- Regular price per unit in EUR
        discount_price_per_unit -- Price per unit after discount
        discount_info   -- Discount label (e.g. "1+1 gratis")
        weight          -- Product weight/size (e.g. "500g")
        price_per_unit  -- Price per unit in EUR (unit from weight)
        product_url     -- URL to product page
        start_date      -- Discount start date
        end_date        -- Discount end date
        image_url       -- Product image URL
        scraped_at      -- When this was scraped (auto-filled)
    """
    __tablename__ = "raw_discounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_name = Column(String(100), nullable=False, index=True)
    week = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    name = Column(String(500), nullable=False)
    supermarket = Column(String(50), nullable=False)
    original_price = Column(Float, nullable=True)
    discount_price_per_unit = Column(Float, nullable=True)
    discount_info = Column(String(200), nullable=False)
    weight = Column(String(100), nullable=True)
    price_per_unit = Column(Float, nullable=True)
    product_url = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    image_url = Column(Text, nullable=True)
    scraped_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_raw_discounts_week_year", "week", "year"),
    )

    def __repr__(self):
        return f"<RawDiscount {self.name} ({self.batch_name})>"


class CleanedProductTable(Base):
    """
    Database table for AI-cleaned product data.

    After the AI processes raw discount data, it adds:
    - common_name: A generic name like "tomato" instead of "AH Bio tomaat"
    - labels: Tags from a fixed set like "bio", "vegetable", "fresh"

    Columns:
        id                      -- Auto-incrementing primary key
        batch_name              -- Batch identifier e.g. "albert_heijn_bonus_w06_2026"
        week                    -- ISO week number (1-53)
        year                    -- Year (e.g. 2026)
        raw_discount_id         -- Link back to the raw scraped data
        raw_name                -- Original supermarket product name
        common_name             -- AI-assigned generic name (e.g. "tomato")
        labels                  -- Comma-separated labels (e.g. "bio,vegetable,fresh")
        supermarket             -- "albert_heijn" or "jumbo"
        original_price          -- Regular price per unit in EUR
        discount_price_per_unit -- Price per unit after discount
        discount_info           -- Discount label (e.g. "1+1 gratis")
        weight                  -- Product weight/size
        price_per_unit          -- Price per unit in EUR
        product_url             -- URL to product page
        start_date              -- Discount start date
        end_date                -- Discount end date
        image_url               -- Product image URL
        cleaned_at              -- When AI processed this (auto-filled)

    NOTE ON LABELS:
        Labels are stored as a comma-separated string (e.g. "bio,vegetable,fresh")
        because SQLite does not support array columns. When reading from the DB,
        split on comma to get a list: labels.split(",")
    """
    __tablename__ = "cleaned_products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_name = Column(String(100), nullable=False, index=True)
    week = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    raw_discount_id = Column(Integer, ForeignKey("raw_discounts.id"), nullable=True)
    raw_name = Column(String(500), nullable=False)
    common_name = Column(String(200), nullable=False)
    labels = Column(String(500), nullable=False, default="")
    supermarket = Column(String(50), nullable=False)
    original_price = Column(Float, nullable=True)
    discount_price_per_unit = Column(Float, nullable=True)
    discount_info = Column(String(200), nullable=False)
    weight = Column(String(100), nullable=True)
    price_per_unit = Column(Float, nullable=True)
    product_url = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    image_url = Column(Text, nullable=True)
    cleaned_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_cleaned_products_week_year", "week", "year"),
    )

    def __repr__(self):
        return f"<CleanedProduct {self.common_name} ({self.batch_name})>"
