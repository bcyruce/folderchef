"""
FolderChef -- CLI Entry Point
================================

Run the scraper from the command line, with optional week/year selection.

USAGE:
    # Scrape current week, all supermarkets:
    python -m app.cli scrape

    # Scrape specific week for Albert Heijn:
    python -m app.cli scrape --supermarket albert_heijn --week 6 --year 2026

    # Scrape current week for Albert Heijn only:
    python -m app.cli scrape --supermarket albert_heijn

ON RAILWAY:
    railway run python -m app.cli scrape --week 6 --year 2026
"""

import argparse
import asyncio
import sys


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="folderchef",
        description="FolderChef -- Supermarket Discount Scraper CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- scrape command ---
    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Run the scrape -> AI clean -> store pipeline",
    )
    scrape_parser.add_argument(
        "--supermarket",
        type=str,
        default=None,
        help="Supermarket to scrape (e.g. 'albert_heijn'). Default: all.",
    )
    scrape_parser.add_argument(
        "--week",
        type=int,
        default=None,
        help="ISO week number (1-53). Default: current week.",
    )
    scrape_parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Year (e.g. 2026). Default: current year.",
    )

    return parser


async def run_scrape(
    supermarket: str | None,
    week: int | None,
    year: int | None,
) -> None:
    """
    Execute the scrape pipeline.

    Connects directly to the database (no FastAPI needed).
    """
    from app.database.connection import init_db, close_db
    from app.services.discount_service import DiscountService

    # Resolve defaults
    service = DiscountService()
    cur_week, cur_year = service.current_week_year()
    week = week or cur_week
    year = year or cur_year

    targets = [supermarket] if supermarket else list(service.scrapers.keys())
    batch_names = [service.make_batch_name(t, week, year) for t in targets]

    print("=" * 60)
    print("FolderChef Scraper CLI")
    print("=" * 60)
    print(f"  Week:          {week}")
    print(f"  Year:          {year}")
    print(f"  Supermarkets:  {', '.join(targets)}")
    print(f"  Batches:       {', '.join(batch_names)}")
    print("=" * 60)

    # Initialize database
    await init_db()

    try:
        # Pass db=None so service uses fresh session for store (avoids idle timeout)
        summary = await service.refresh_discounts(
            db=None,
            supermarket=supermarket,
            week=week,
            year=year,
        )

        print("\n" + "=" * 60)
        print("DONE!")
        print("=" * 60)
        print(f"  Scraped:       {summary['scraped']} raw products")
        print(f"  Cleaned:       {summary['cleaned']} products")
        print(f"  Batches saved: {', '.join(summary.get('batches', []))}")
        print("=" * 60)

    finally:
        await service.close()
        await close_db()


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "scrape":
        asyncio.run(run_scrape(
            supermarket=args.supermarket,
            week=args.week,
            year=args.year,
        ))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
