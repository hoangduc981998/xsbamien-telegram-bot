#!/usr/bin/env python3
"""Test data transformer"""

import asyncio
import json
from app.services.api.client import MU88APIClient
from app.services.api.transformer import DataTransformer


async def test():
    client = MU88APIClient()

    # Test all 3 regions
    test_cases = [
        ("MB", "Miền Bắc"),
        ("TPHCM", "TP.HCM (MN)"),
        ("GILA", "Gia Lai (MT)"),
    ]

    for province_code, name in test_cases:
        print(f"\n{'='*70}")
        print(f"Testing: {name}")
        print("=" * 70)

        # Fetch from API
        api_response = await client.fetch_results(province_code, limit=3)

        if not api_response:
            print(f"❌ Failed to fetch {province_code}")
            continue

        # Transform
        results = DataTransformer.transform_results(api_response)

        print(f"\n📊 Transformed {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Date: {result.get('date')}")
            print(f"Province: {result.get('province')}")
            print(f"Keys: {list(result.keys())}")

            # Show prizes
            if "DB" in result:
                print(f"DB: {result['DB']}")
            if "G1" in result:
                print(f"G1: {result['G1']}")
            if "G8" in result:
                print(f"G8: {result['G8']}")

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(test())
