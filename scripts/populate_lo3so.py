"""Populate lo_3_so_history from existing lottery_results"""

import asyncio
import logging
from datetime import datetime

from app.database import DatabaseSession
from app.models import LotteryResult, Lo3SoHistory
from sqlalchemy import select, delete
from sqlalchemy.dialects.sqlite import insert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def extract_lo3so_from_prizes(prizes: dict, lottery_result) -> list[dict]:
    """Extract 3-digit numbers from prizes"""
    numbers = []
    prize_keys = ["DB", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]
    
    for prize_key in prize_keys:
        if prize_key in prizes and prizes[prize_key]:
            prize_values = prizes[prize_key]
            if isinstance(prize_values, str):
                prize_values = [prize_values]
            
            for idx, num_str in enumerate(prize_values):
                if len(num_str) >= 3:
                    lo3 = num_str[-3:]  # Last 3 digits
                    numbers.append({
                        "lottery_result_id": lottery_result.id,
                        "province_code": lottery_result.province_code,
                        "region": lottery_result.region,
                        "draw_date": lottery_result.draw_date,
                        "number": lo3,
                        "prize_type": prize_key,
                        "position": f"{prize_key}_{idx}",
                        "created_at": datetime.utcnow(),
                    })
    
    return numbers


async def populate_lo3so():
    """Populate lo_3_so_history from existing lottery_results"""
    logger.info("🚀 Starting lo3so population...")
    
    async with DatabaseSession() as session:
        # Clear existing lo3so data
        logger.info("🗑️  Clearing existing lo3so data...")
        await session.execute(delete(Lo3SoHistory))
        await session.commit()
        
        # Get all lottery results
        query = select(LotteryResult).order_by(LotteryResult.draw_date.desc())
        result = await session.execute(query)
        lottery_results = result.scalars().all()
        
        logger.info(f"📊 Found {len(lottery_results)} lottery results")
        
        total_lo3so = 0
        
        for lottery_result in lottery_results:
            # Extract lo3so numbers
            lo3so_numbers = await extract_lo3so_from_prizes(
                lottery_result.prizes,
                lottery_result
            )
            
            if lo3so_numbers:
                # Insert lo3so records
                stmt = insert(Lo3SoHistory).values(lo3so_numbers)
                stmt = stmt.on_conflict_do_nothing()
                await session.execute(stmt)
                
                total_lo3so += len(lo3so_numbers)
                
                if total_lo3so % 1000 == 0:
                    logger.info(f"  💾 Processed {total_lo3so} lo3so numbers...")
        
        await session.commit()
        
        logger.info(f"✅ Completed! Saved {total_lo3so} lo3so numbers")
        
        # Verify
        from sqlalchemy import func
        count_query = select(func.count(Lo3SoHistory.id))
        count_result = await session.execute(count_query)
        count = count_result.scalar()
        
        logger.info(f"📊 Database now has {count} lo3so records")


if __name__ == "__main__":
    asyncio.run(populate_lo3so())
