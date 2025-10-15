#!/usr/bin/env python3
"""
CLI tool for loading historical lottery data

Usage:
    python scripts/load_historical_data.py --days 100 --all
    python scripts/load_historical_data.py --days 60 --province MB
    python scripts/load_historical_data.py --days 30 --region MN
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.crawler import HistoricalDataCrawler
from app.database import init_db
from app.config import PROVINCES

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="Load historical lottery data")
    parser.add_argument(
        "--days",
        type=int,
        default=100,
        help="Number of days of historical data to load (default: 100)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Load data for all provinces"
    )
    parser.add_argument(
        "--province",
        type=str,
        help="Load data for specific province (e.g., MB, TPHCM)"
    )
    parser.add_argument(
        "--region",
        type=str,
        choices=["MB", "MN", "MT"],
        help="Load data for all provinces in a region"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip provinces that already have data (default: True)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize database tables before loading"
    )

    args = parser.parse_args()

    try:
        # Initialize database if requested
        if args.init_db:
            logger.info("🗄️  Initializing database tables...")
            await init_db()

        # Create crawler
        crawler = HistoricalDataCrawler()

        # Determine what to crawl
        if args.all:
            logger.info(f"📊 Loading {args.days} days of data for ALL provinces")
            result = await crawler.crawl_all_provinces(
                limit=args.days,
                skip_existing=args.skip_existing,
                delay=args.delay
            )
        elif args.province:
            province = args.province.upper()
            if province not in PROVINCES:
                logger.error(f"❌ Unknown province: {province}")
                logger.info(f"Available provinces: {', '.join(PROVINCES.keys())}")
                return 1

            logger.info(f"📊 Loading {args.days} days of data for {province}")
            result = await crawler.crawl_province(
                province,
                limit=args.days,
                skip_existing=args.skip_existing
            )
            result = {"results": [result]}
        elif args.region:
            region = args.region.upper()
            logger.info(f"📊 Loading {args.days} days of data for region {region}")
            result = await crawler.crawl_region(
                region,
                limit=args.days,
                skip_existing=args.skip_existing,
                delay=args.delay
            )
        else:
            logger.error("❌ Must specify --all, --province, or --region")
            parser.print_help()
            return 1

        # Print summary
        print("\n" + "=" * 60)
        print("📊 CRAWL SUMMARY")
        print("=" * 60)

        if "results" in result:
            for res in result["results"]:
                status_emoji = {
                    "success": "✅",
                    "error": "❌",
                    "skipped": "⏭️ "
                }.get(res.get("status"), "❓")

                print(f"{status_emoji} {res.get('province_code', 'N/A'):8s} - "
                      f"Status: {res.get('status', 'unknown'):8s} - "
                      f"Fetched: {res.get('fetched', 0):3d} - "
                      f"Saved: {res.get('saved', 0):3d}")

        if "total_saved" in result:
            print("\n" + "-" * 60)
            print(f"Total provinces: {result.get('total_provinces', 0)}")
            print(f"Success: {result.get('success', 0)}")
            print(f"Errors: {result.get('errors', 0)}")
            print(f"Skipped: {result.get('skipped', 0)}")
            print(f"Total saved: {result.get('total_saved', 0)} results")
            print(f"Duration: {result.get('duration_seconds', 0):.2f}s")

        print("=" * 60)
        print("\n✅ Data loading completed!")
        return 0

    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
