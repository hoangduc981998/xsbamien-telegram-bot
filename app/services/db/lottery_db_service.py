"""Database service for storing and retrieving lottery results"""

import logging
from datetime import date, datetime
from typing import List, Dict, Optional

from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.models import LotteryResult, Lo2SoHistory
from app.database import DatabaseSession

logger = logging.getLogger(__name__)


class LotteryDBService:
    """Service for managing lottery results in database"""

    def __init__(self):
        pass

    async def save_result(self, result_data: Dict) -> Optional[LotteryResult]:
        """
        Save a lottery result to database
        
        Args:
            result_data: Dict with keys: province_code, province_name, region, date, prizes
            
        Returns:
            LotteryResult object or None if error
        """
        try:
            async with DatabaseSession() as session:
                # Parse date
                draw_date = result_data.get("date")
                if isinstance(draw_date, str):
                    # Thử format DD/MM/YYYY trước (từ API)
                    try:
                        draw_date = datetime.strptime(draw_date, "%d/%m/%Y").date()
                    except ValueError:
                        # Nếu không được thì dùng format YYYY-MM-DD
                        draw_date = datetime.strptime(draw_date, "%Y-%m-%d").date()

                elif isinstance(draw_date, datetime):
                    draw_date = draw_date.date()

                # Upsert (insert or update)
                stmt = insert(LotteryResult).values(
                    province_code=result_data.get("province_code"),
                    province_name=result_data.get("province", result_data.get("province_name")),
                    region=result_data.get("region"),
                    draw_date=draw_date,
                    prizes=result_data.get("prizes", result_data),  # Handle both formats
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                # On conflict, update the prizes and updated_at
                stmt = stmt.on_conflict_do_update(
                    index_elements=["province_code", "draw_date"],
                    set_={
                        "prizes": stmt.excluded.prizes,
                        "updated_at": datetime.utcnow(),
                    }
                )

                result = await session.execute(stmt)
                await session.commit()

                # Get the saved record
                query = select(LotteryResult).where(
                    and_(
                        LotteryResult.province_code == result_data.get("province_code"),
                        LotteryResult.draw_date == draw_date
                    )
                )
                result = await session.execute(query)
                lottery_result = result.scalar_one_or_none()

                if lottery_result:
                    logger.info(f"✅ Saved lottery result: {lottery_result.province_code} - {lottery_result.draw_date}")

                    # Extract and save lo 2 so numbers
                    await self._extract_and_save_lo2so(session, lottery_result)

                return lottery_result

        except Exception as e:
            logger.error(f"❌ Error saving lottery result: {e}")
            return None

    async def _extract_and_save_lo2so(self, session: AsyncSession, lottery_result: LotteryResult) -> None:
        """
        Extract 2-digit numbers from lottery result and save to lo_2_so_history
        
        Args:
            session: Database session
            lottery_result: LotteryResult object
        """
        try:
            prizes = lottery_result.prizes

            # Delete existing lo2so records for this result
            from sqlalchemy import delete
            stmt = delete(Lo2SoHistory).where(Lo2SoHistory.lottery_result_id == lottery_result.id)
            await session.execute(stmt)

            # Extract all 2-digit numbers
            prize_keys = ["DB", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]
            lo2so_records = []

            for prize_key in prize_keys:
                if prize_key in prizes and prizes[prize_key]:
                    for num_str in prizes[prize_key]:
                        if len(num_str) >= 2:
                            lo2 = num_str[-2:]  # Last 2 digits

                            lo2so_records.append({
                                "lottery_result_id": lottery_result.id,
                                "province_code": lottery_result.province_code,
                                "region": lottery_result.region,
                                "draw_date": lottery_result.draw_date,
                                "number": lo2,
                                "prize_type": prize_key,
                                "position": "last_2",
                                "created_at": datetime.utcnow(),
                            })

            # Bulk insert
            if lo2so_records:
                stmt = insert(Lo2SoHistory).values(lo2so_records)
                await session.execute(stmt)
                logger.info(f"✅ Saved {len(lo2so_records)} lo2so numbers for {lottery_result.province_code}")

        except Exception as e:
            logger.error(f"❌ Error extracting lo2so: {e}")

    async def get_result(self, province_code: str, draw_date: date) -> Optional[LotteryResult]:
        """
        Get a specific lottery result
        
        Args:
            province_code: Province code
            draw_date: Draw date
            
        Returns:
            LotteryResult or None
        """
        try:
            async with DatabaseSession() as session:
                query = select(LotteryResult).where(
                    and_(
                        LotteryResult.province_code == province_code,
                        LotteryResult.draw_date == draw_date
                    )
                )
                result = await session.execute(query)
                return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"❌ Error getting lottery result: {e}")
            return None

    async def get_latest_result(self, province_code: str) -> Optional[LotteryResult]:
        """
        Get the latest lottery result for a province
        
        Args:
            province_code: Province code
            
        Returns:
            LotteryResult or None
        """
        try:
            async with DatabaseSession() as session:
                query = select(LotteryResult).where(
                    LotteryResult.province_code == province_code
                ).order_by(desc(LotteryResult.draw_date)).limit(1)

                result = await session.execute(query)
                return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"❌ Error getting latest result: {e}")
            return None

    async def get_history(
        self,
        province_code: str,
        limit: int = 60,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[LotteryResult]:
        """
        Get historical lottery results
        
        Args:
            province_code: Province code
            limit: Maximum number of results
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of LotteryResult objects
        """
        try:
            async with DatabaseSession() as session:
                query = select(LotteryResult).where(
                    LotteryResult.province_code == province_code
                )

                if start_date:
                    query = query.where(LotteryResult.draw_date >= start_date)
                if end_date:
                    query = query.where(LotteryResult.draw_date <= end_date)

                query = query.order_by(desc(LotteryResult.draw_date)).limit(limit)

                result = await session.execute(query)
                return list(result.scalars().all())

        except Exception as e:
            logger.error(f"❌ Error getting history: {e}")
            return []

    async def get_results_count(self, province_code: Optional[str] = None) -> int:
        """
        Get count of lottery results in database
        
        Args:
            province_code: Optional province code filter
            
        Returns:
            Count of results
        """
        try:
            async with DatabaseSession() as session:
                query = select(func.count(LotteryResult.id))

                if province_code:
                    query = query.where(LotteryResult.province_code == province_code)

                result = await session.execute(query)
                return result.scalar() or 0

        except Exception as e:
            logger.error(f"❌ Error getting results count: {e}")
            return 0

    async def get_date_range(self, province_code: str) -> Optional[Dict]:
        """
        Get the date range of available results for a province
        
        Args:
            province_code: Province code
            
        Returns:
            Dict with min_date and max_date or None
        """
        try:
            async with DatabaseSession() as session:
                query = select(
                    func.min(LotteryResult.draw_date).label("min_date"),
                    func.max(LotteryResult.draw_date).label("max_date")
                ).where(LotteryResult.province_code == province_code)

                result = await session.execute(query)
                row = result.one_or_none()

                if row and row.min_date:
                    return {
                        "min_date": row.min_date,
                        "max_date": row.max_date,
                        "days": (row.max_date - row.min_date).days + 1
                    }

                return None

        except Exception as e:
            logger.error(f"❌ Error getting date range: {e}")
            return None
