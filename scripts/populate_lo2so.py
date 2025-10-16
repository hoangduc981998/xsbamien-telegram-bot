#!/usr/bin/env python3
"""
Populate lo_2_so_history table from lottery_results
Extracts last 2 digits from all prizes
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import DatabaseSession, init_db
from app.models import LotteryResult, Lo2SoHistory
from sqlalchemy import select, delete


async def populate_lo2so():
    """Populate lo_2_so_history from lottery_results"""
    
    print("🚀 Starting lo_2_so_history population...")
    
    # Initialize database
    await init_db()
    
    async with DatabaseSession() as session:
        # Delete existing data
        await session.execute(delete(Lo2SoHistory))
        await session.commit()
        print("🗑️  Cleared existing lo_2_so_history")
        
        # Get all lottery results
        result = await session.execute(
            select(LotteryResult).order_by(LotteryResult.draw_date)
        )
        
        all_results = result.scalars().all()
        
        print(f"📊 Found {len(all_results)} lottery results")
        
        inserted = 0
        for lottery in all_results:
            # Extract 2-digit numbers from prizes
            prizes = lottery.prizes
            
            if not prizes:
                continue
            
            # Collect all numbers
            numbers_set = set()  # Use set to avoid duplicates in same draw
            
            for prize_type, values in prizes.items():
                if isinstance(values, list):
                    for val in values:
                        # Extract last 2 digits
                        val_str = str(val).strip()
                        if val_str and len(val_str) >= 2:
                            last_2 = val_str[-2:]
                            numbers_set.add((last_2, prize_type))
                elif values:
                    val_str = str(values).strip()
                    if val_str and len(val_str) >= 2:
                        last_2 = val_str[-2:]
                        numbers_set.add((last_2, prize_type))
            
            # Insert into lo_2_so_history
            for num, prize_type in numbers_set:
                lo2so = Lo2SoHistory(
                    lottery_result_id=lottery.id,  # ← THÊM!
                    province_code=lottery.province_code,
                    region=lottery.region,  # ← THÊM!
                    draw_date=lottery.draw_date,
                    number=num,
                    prize_type=prize_type,
                    position='last_2'  # ← THÊM (optional)
                )
                session.add(lo2so)
                inserted += 1
        
        await session.commit()
        print(f"✅ Inserted {inserted} records into lo_2_so_history")
        
        # Show statistics
        result = await session.execute(
            select(Lo2SoHistory.province_code, 
                   Lo2SoHistory.number)
            .distinct()
        )
        
        unique_count = len(result.all())
        print(f"📈 Unique (province, number) pairs: {unique_count}")


if __name__ == "__main__":
    asyncio.run(populate_lo2so())
