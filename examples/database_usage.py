#!/usr/bin/env python3
"""
Example demonstrating database usage for lottery data and statistics

This example shows how to:
1. Save lottery results to database
2. Query historical data
3. Calculate statistics (frequency, hot/cold numbers, Lô Gan)
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.lottery_service import LotteryService
from app.services.statistics_service import StatisticsService
from app.services.db import LotteryDBService, StatisticsDBService


async def example_save_and_query():
    """Example: Save results and query them"""
    print("\n" + "=" * 60)
    print("📊 EXAMPLE 1: Save and Query Lottery Results")
    print("=" * 60)

    # Create services with database enabled
    lottery_service = LotteryService(use_database=True)
    db_service = LotteryDBService()

    # Get latest result from API and save to DB
    print("\n1️⃣  Fetching latest result for MB...")
    result = await lottery_service.get_latest_result("MB")
    print(f"   ✅ Got result for {result.get('date')}")

    # Query from database
    print("\n2️⃣  Querying from database...")
    db_result = await db_service.get_latest_result("MB")
    if db_result:
        print(f"   ✅ Found in DB: {db_result.province_code} - {db_result.draw_date}")
        print(f"   📊 Prizes: {len(db_result.prizes)} types")
    else:
        print("   ⚠️  Not found in database")

    # Get historical data
    print("\n3️⃣  Getting 10 days of history...")
    history = await db_service.get_history("MB", limit=10)
    print(f"   ✅ Found {len(history)} results")
    for i, result in enumerate(history[:3], 1):
        print(f"      {i}. {result.draw_date} - {result.province_name}")

    # Get date range
    print("\n4️⃣  Getting date range...")
    date_range = await db_service.get_date_range("MB")
    if date_range:
        print(f"   ✅ Data available: {date_range['days']} days")
        print(f"      From: {date_range['min_date']}")
        print(f"      To:   {date_range['max_date']}")


async def example_statistics():
    """Example: Calculate statistics from database"""
    print("\n" + "=" * 60)
    print("📈 EXAMPLE 2: Calculate Statistics")
    print("=" * 60)

    stats_service = StatisticsDBService()

    # Get frequency of numbers (last 30 days)
    print("\n1️⃣  Getting frequency statistics (30 days)...")
    frequency = await stats_service.get_lo2so_frequency("MB", days=30)
    if frequency:
        # Show top 10
        sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        print(f"   ✅ Found {len(frequency)} unique numbers")
        print("\n   🔥 Top 10 Most Frequent:")
        for i, (num, count) in enumerate(sorted_freq[:10], 1):
            print(f"      {i:2d}. {num} - {count:2d} times")
    else:
        print("   ⚠️  No frequency data available (database may be empty)")

    # Get hot numbers
    print("\n2️⃣  Getting hot numbers...")
    hot = await stats_service.get_hot_numbers("MB", days=30, limit=5)
    if hot:
        print("   ✅ Top 5 Hot Numbers:")
        for i, item in enumerate(hot, 1):
            print(f"      {i}. {item['number']} - {item['count']} times")
    else:
        print("   ⚠️  No hot numbers data")

    # Get Lô Gan (cold numbers)
    print("\n3️⃣  Getting Lô Gan (numbers not appeared recently)...")
    lo_gan = await stats_service.get_lo_gan("MB", days=30, limit=10)
    if lo_gan:
        print("   ✅ Top 10 Lô Gan:")
        for i, item in enumerate(lo_gan, 1):
            last_seen = item['last_seen_date'] or 'Never'
            print(f"      {i:2d}. {item['number']} - {item['days_since_last']} days (Last: {last_seen})")
    else:
        print("   ⚠️  No Lô Gan data")

    # Get statistics summary
    print("\n4️⃣  Getting statistics summary...")
    summary = await stats_service.get_statistics_summary("MB", days=30)
    if summary:
        print("   ✅ Statistics Summary:")
        print(f"      Province: {summary['province_code']}")
        print(f"      Period: {summary['days']} days")
        print(f"      Total draws: {summary['total_draws']}")
        print(f"      Unique numbers: {summary['unique_numbers']}")
        print(f"      Total occurrences: {summary['total_occurrences']}")
        print(f"      Average per draw: {summary['avg_per_draw']}")


async def example_number_history():
    """Example: Track specific number history"""
    print("\n" + "=" * 60)
    print("🔍 EXAMPLE 3: Track Specific Number History")
    print("=" * 60)

    stats_service = StatisticsDBService()

    # Track number "45"
    number = "45"
    print(f"\n📊 Tracking number: {number}")

    history = await stats_service.get_number_history("MB", number, limit=10)
    if history:
        print(f"   ✅ Found {len(history)} occurrences:")
        for i, item in enumerate(history, 1):
            print(f"      {i:2d}. {item['date']} - Prize: {item['prize_type']}")
    else:
        print(f"   ⚠️  Number {number} not found in recent history")


async def example_integrated_service():
    """Example: Using integrated services"""
    print("\n" + "=" * 60)
    print("🎯 EXAMPLE 4: Using Integrated Services")
    print("=" * 60)

    # Create services with database integration
    lottery_service = LotteryService(use_database=True)
    stats_service = StatisticsService(use_database=True)

    print("\n1️⃣  Getting latest result (with DB caching)...")
    result = await lottery_service.get_latest_result("TPHCM")
    print(f"   ✅ {result.get('province')} - {result.get('date')}")

    print("\n2️⃣  Getting statistics with real database...")
    frequency = await stats_service.get_frequency_stats("TPHCM", days=30)
    if frequency:
        print(f"   ✅ Frequency data: {len(frequency)} numbers")

    print("\n3️⃣  Getting Lô Gan...")
    lo_gan = await stats_service.get_lo_gan("TPHCM", days=30, limit=5)
    if lo_gan:
        print(f"   ✅ Lô Gan: {len(lo_gan)} numbers")
        for item in lo_gan[:3]:
            print(f"      • {item['number']} - {item['days_since_last']} days")


async def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("🎰 LOTTERY DATABASE USAGE EXAMPLES")
    print("=" * 60)
    print("\nNOTE: These examples require:")
    print("  1. PostgreSQL database running")
    print("  2. Database initialized (alembic upgrade head)")
    print("  3. Historical data loaded (scripts/load_historical_data.py)")
    print("\nIf database is not available, examples will show empty/mock data.")

    try:
        # Example 1: Basic save and query
        await example_save_and_query()

        # Example 2: Statistics
        await example_statistics()

        # Example 3: Number history
        await example_number_history()

        # Example 4: Integrated services
        await example_integrated_service()

        print("\n" + "=" * 60)
        print("✅ All examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("\nThis is likely because:")
        print("  • Database is not running")
        print("  • Database is not initialized")
        print("  • No historical data loaded")
        print("\nSee docs/DATABASE.md for setup instructions")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
