#!/usr/bin/env python3
"""Test MU88 API to understand response structure"""

import httpx
import json
from datetime import datetime


async def test_api():
    """Test MU88 API structure"""

    url = "https://mu88.live/api/front/open/lottery/history/list/game"

    # Test 3 provinces (MB, MT, MN)
    test_cases = [
        {"gameCode": "miba", "name": "Miền Bắc"},
        {"gameCode": "gila", "name": "Gia Lai (MT)"},
        {"gameCode": "tphc", "name": "TP.HCM (MN)"},
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            print(f"\n{'='*60}")
            print(f"Testing: {test['name']} ({test['gameCode']})")
            print("=" * 60)

            try:
                response = await client.get(
                    url,
                    params={
                        "limitNum": 3,  # Only 3 records for testing
                        "gameCode": test["gameCode"],
                    },
                )

                data = response.json()

                # Analyze structure
                print(f"\nStatus Code: {response.status_code}")
                print(f"Response Type: {type(data)}")

                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())}")

                    # Show first record
                    if "data" in data and data["data"]:
                        print(f"\nFirst record keys: {list(data['data'][0].keys())}")
                        print(f"\nFirst record sample:")
                        print(json.dumps(data["data"][0], indent=2, ensure_ascii=False))

                elif isinstance(data, list):
                    if data:
                        print(f"First item keys: {list(data[0].keys())}")
                        print(f"\nFirst item sample:")
                        print(json.dumps(data[0], indent=2, ensure_ascii=False))

                # Save sample
                filename = f"samples/mu88_{test['gameCode']}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n✅ Saved to {filename}")

            except Exception as e:
                print(f"❌ Error: {e}")


if __name__ == "__main__":
    import asyncio
    import os

    # Create samples directory
    os.makedirs("samples", exist_ok=True)

    asyncio.run(test_api())
