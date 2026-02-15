"""
FolderChef -- Discount Service
================================

Orchestrates the full discount pipeline:

    1. SCRAPE  -- Fetch raw products from supermarket APIs
    2. CLEAN   -- Send raw products through AI for common names + labels
    3. STORE   -- Save cleaned products to the database (tagged by batch)
    4. SERVE   -- Return cleaned products for API responses

BATCH NAMING:
    Each scrape run is tagged with a batch_name like:
        albert_heijn_bonus_w06_2026

    This allows multiple weeks of data to coexist in the database.
    Re-running the same week replaces that batch only.
"""

from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.discount import RawDiscount, CleanedProduct, DiscountResponse
from app.scrapers.albert_heijn import AlbertHeijnScraper
from app.services.ai_service import AIService
from app.database.tables import RawDiscountTable, CleanedProductTable


class DiscountService:
    """
    Service for managing the full discount data pipeline.

    Attributes:
        ai_service: AI service for cleaning products.
        scrapers: Dict mapping supermarket name to scraper instance.
    """

    def __init__(self):
        self.ai_service = AIService()
        self.scrapers = {
            "albert_heijn": AlbertHeijnScraper(),
        }

    # ==============================================================
    # BATCH NAME HELPERS
    # ==============================================================

    @staticmethod
    def make_batch_name(supermarket: str, week: int, year: int) -> str:
        """
        Build a batch name like 'albert_heijn_bonus_w06_2026'.

        Args:
            supermarket: e.g. "albert_heijn"
            week: ISO week number (1-53)
            year: e.g. 2026

        Returns:
            str: The batch name.
        """
        return f"{supermarket}_bonus_w{week:02d}_{year}"

    @staticmethod
    def current_week_year() -> tuple[int, int]:
        """Return (week, year) for today using ISO calendar."""
        today = date.today()
        iso = today.isocalendar()
        return iso[1], iso[0]

    # ==============================================================
    # MAIN API METHODS (called by routers and CLI)
    # ==============================================================

    async def get_discounts(
        self,
        db: AsyncSession,
        supermarket: Optional[str] = None,
        week: Optional[int] = None,
        year: Optional[int] = None,
    ) -> list[DiscountResponse]:
        """
        Get cleaned discount data from the database.

        If week/year are not provided, returns the latest available batch.

        Args:
            db: Database session.
            supermarket: Optional filter. None = all supermarkets.
            week: Optional ISO week number to filter by.
            year: Optional year to filter by.

        Returns:
            list[DiscountResponse]: Discount data grouped by supermarket.
        """
        results = []

        targets = [supermarket] if supermarket else list(self.scrapers.keys())

        for target in targets:
            items = await self._get_from_db(db, target, week=week, year=year)

            # Build week label from the batch or dates
            week_label = self._get_week_label(items, week=week, year=year)

            results.append(DiscountResponse(
                supermarket=target,
                total_items=len(items),
                week=week_label,
                items=items,
            ))

        return results

    async def refresh_discounts(
        self,
        db: AsyncSession,
        supermarket: Optional[str] = None,
        week: Optional[int] = None,
        year: Optional[int] = None,
    ) -> dict:
        """
        Run the full pipeline: scrape -> clean with AI -> store in DB.

        Each run is tagged with a batch_name. If the same batch already
        exists (re-run for the same week), it is replaced. Other weeks
        are left untouched.

        Args:
            db: Database session.
            supermarket: Which supermarket to refresh. None = all.
            week: ISO week number. Defaults to current week.
            year: Year. Defaults to current year.

        Returns:
            dict: Summary with counts of scraped and cleaned items.
        """
        # Default to current week/year if not specified
        if week is None or year is None:
            cur_week, cur_year = self.current_week_year()
            week = week or cur_week
            year = year or cur_year

        targets = [supermarket] if supermarket else list(self.scrapers.keys())
        summary = {
            "scraped": 0,
            "cleaned": 0,
            "supermarkets": [],
            "batches": [],
        }

        for target in targets:
            batch_name = self.make_batch_name(target, week, year)

            print(f"\n{'='*50}")
            print(f"Refreshing: {batch_name}")
            print(f"{'='*50}")

            scraper = self.scrapers.get(target)
            if not scraper:
                print(f"  No scraper for {target}, skipping")
                continue

            # Step 1: SCRAPE
            print("Step 1: Scraping...")
            raw_products = await scraper.scrape()
            print(f"  Scraped {len(raw_products)} raw products")
            summary["scraped"] += len(raw_products)

            if not raw_products:
                print("  No products found, skipping")
                continue

            # Step 2: CLEAN with AI
            print("Step 2: Cleaning with AI...")
            cleaned_products = await self.ai_service.clean_products(raw_products)
            print(f"  Cleaned {len(cleaned_products)} products")
            summary["cleaned"] += len(cleaned_products)

            # Step 3: STORE in database (per batch)
            print(f"Step 3: Storing as batch '{batch_name}'...")
            await self._store_in_db(
                db, target, batch_name, week, year,
                raw_products, cleaned_products,
            )
            print(f"  Stored in database")

            summary["supermarkets"].append(target)
            summary["batches"].append(batch_name)

        return summary

    # ==============================================================
    # DATABASE METHODS
    # ==============================================================

    async def _get_from_db(
        self,
        db: AsyncSession,
        supermarket: str,
        week: Optional[int] = None,
        year: Optional[int] = None,
    ) -> list[CleanedProduct]:
        """
        Fetch cleaned products from the database for a supermarket.

        If week/year are provided, returns that specific batch.
        Otherwise returns the latest batch (highest year, then week).

        Args:
            db: Database session.
            supermarket: Which supermarket to query.
            week: Optional week filter.
            year: Optional year filter.

        Returns:
            list[CleanedProduct]: Products from the database.
        """
        if week and year:
            # Fetch specific batch
            batch_name = self.make_batch_name(supermarket, week, year)
            query = (
                select(CleanedProductTable)
                .where(CleanedProductTable.batch_name == batch_name)
                .order_by(CleanedProductTable.common_name)
            )
        else:
            # Find the latest batch for this supermarket
            latest = (
                select(
                    CleanedProductTable.batch_name,
                )
                .where(CleanedProductTable.supermarket == supermarket)
                .order_by(
                    CleanedProductTable.year.desc(),
                    CleanedProductTable.week.desc(),
                )
                .limit(1)
            )
            latest_result = await db.execute(latest)
            latest_row = latest_result.first()

            if not latest_row:
                return []

            latest_batch = latest_row[0]
            query = (
                select(CleanedProductTable)
                .where(CleanedProductTable.batch_name == latest_batch)
                .order_by(CleanedProductTable.common_name)
            )

        result = await db.execute(query)
        rows = result.scalars().all()

        return [
            CleanedProduct(
                id=row.id,
                raw_name=row.raw_name,
                common_name=row.common_name,
                labels=row.labels.split(",") if row.labels else [],
                supermarket=row.supermarket,
                original_price=row.original_price,
                discount_price_per_unit=row.discount_price_per_unit,
                discount_info=row.discount_info,
                weight=row.weight,
                price_per_unit=getattr(row, "price_per_unit", None) or getattr(row, "price_per_kg", None),
                product_url=getattr(row, "product_url", None),
                start_date=row.start_date,
                end_date=row.end_date,
                image_url=row.image_url,
                scraped_at=row.cleaned_at,
            )
            for row in rows
        ]

    async def _store_in_db(
        self,
        db: AsyncSession,
        supermarket: str,
        batch_name: str,
        week: int,
        year: int,
        raw_products: list[RawDiscount],
        cleaned_products: list[CleanedProduct],
    ) -> None:
        """
        Store scraped and cleaned products in the database.

        Replaces the specific batch only (deletes old data for that
        batch_name, keeps all other batches intact).

        Args:
            db: Database session.
            supermarket: Which supermarket this data belongs to.
            batch_name: The batch identifier (e.g. "albert_heijn_bonus_w06_2026").
            week: ISO week number.
            year: Year.
            raw_products: The raw scraped data.
            cleaned_products: The AI-cleaned data.
        """
        # Delete old data for THIS BATCH ONLY (other weeks are untouched)
        await db.execute(
            delete(CleanedProductTable).where(
                CleanedProductTable.batch_name == batch_name
            )
        )
        await db.execute(
            delete(RawDiscountTable).where(
                RawDiscountTable.batch_name == batch_name
            )
        )

        # Use batch week for consistent start/end dates (same week = same dates)
        week_start, week_end = self._week_start_end(week, year)

        # Insert raw discounts
        raw_rows = []
        for raw in raw_products:
            row = RawDiscountTable(
                batch_name=batch_name,
                week=week,
                year=year,
                name=raw.name,
                supermarket=raw.supermarket,
                original_price=raw.original_price,
                discount_price_per_unit=raw.discount_price_per_unit,
                discount_info=raw.discount_info,
                weight=raw.weight,
                price_per_unit=raw.price_per_unit,
                product_url=raw.product_url,
                start_date=week_start,
                end_date=week_end,
                image_url=raw.image_url,
            )
            db.add(row)
            raw_rows.append(row)

        await db.flush()  # Get IDs for the raw rows

        # Insert cleaned products
        for idx, cleaned in enumerate(cleaned_products):
            raw_id = raw_rows[idx].id if idx < len(raw_rows) else None
            labels_str = ",".join(cleaned.labels) if cleaned.labels else ""

            row = CleanedProductTable(
                batch_name=batch_name,
                week=week,
                year=year,
                raw_discount_id=raw_id,
                raw_name=cleaned.raw_name,
                common_name=cleaned.common_name,
                labels=labels_str,
                supermarket=cleaned.supermarket,
                original_price=cleaned.original_price,
                discount_price_per_unit=cleaned.discount_price_per_unit,
                discount_info=cleaned.discount_info,
                weight=cleaned.weight,
                price_per_unit=cleaned.price_per_unit,
                product_url=cleaned.product_url,
                start_date=week_start,
                end_date=week_end,
                image_url=cleaned.image_url,
            )
            db.add(row)

        await db.flush()
        print(f"  Batch '{batch_name}': {len(raw_rows)} raw, {len(cleaned_products)} cleaned")

    # ==============================================================
    # HELPERS
    # ==============================================================

    @staticmethod
    def _week_start_end(week: int, year: int) -> tuple[date, date]:
        """Get Monday and Sunday of ISO week."""
        # Jan 4 is always in week 1
        jan4 = date(year, 1, 4)
        week1_monday = jan4 - timedelta(days=jan4.weekday())
        week_start = week1_monday + timedelta(weeks=week - 1)
        week_end = week_start + timedelta(days=6)
        return week_start, week_end

    def _get_week_label(
        self,
        items: list[CleanedProduct],
        week: Optional[int] = None,
        year: Optional[int] = None,
    ) -> str:
        """
        Generate a human-readable week label.

        Example: "Week 6, 2026"
        """
        if week and year:
            return f"Week {week}, {year}"

        if not items:
            today = date.today()
            week_num = today.isocalendar()[1]
            return f"Week {week_num}, {today.year}"

        # Use the first item's start_date
        for item in items:
            if item.start_date:
                week_num = item.start_date.isocalendar()[1]
                return f"Week {week_num}, {item.start_date.year}"

        today = date.today()
        week_num = today.isocalendar()[1]
        return f"Week {week_num}, {today.year}"

    async def close(self):
        """Close all scraper connections."""
        for scraper in self.scrapers.values():
            await scraper.close()
