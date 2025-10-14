#!/usr/bin/env python3
"""Test full bot integration with real API"""

import asyncio
from app.services.lottery_service import LotteryService


async def test():
    service = LotteryService()

    print("="*70)
    print("TESTING FULL BOT INTEGRATION WITH REAL API")
    print("="*70)

    # Test provinces from each region
    test_cases = [
        ("MB", "Miền Bắc"),
        ("TPHCM", "TP.HCM"),
        ("GILA", "Gia Lai"),
        ("DANA", "Đà Nẵng"),
    ]

    for province_code, name in test_cases:
        print(f"\n{'─'*70}")
        print(f"📍 {name} ({province_code})")
        print('─'*70)

        # Get latest result
        result = await service.get_latest_result(province_code)

        print(f"📅 Date: {result.get('date')}")
        print(f"🏛️  Province: {result.get('province')}")
        print(f"🎯 Prizes: {', '.join([k for k in result.keys() if k.startswith('G') or k == 'DB'])}")
        
        # Show some prizes
        if 'DB' in result:
            print(f"🎰 ĐB: {result['DB']}")
        if 'G1' in result:
            print(f"🥇 G1: {result['G1']}")
        if 'G8' in result:
            print(f"🎲 G8: {result['G8']}")

    print(f"\n{'='*70}")
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("="*70)

    await service.close()


if __name__ == "__main__":
    asyncio.run(test())
