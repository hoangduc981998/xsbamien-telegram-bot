"""Database service for lottery statistics queries"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional

from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LotteryResult, Lo2SoHistory
from app.database import DatabaseSession

logger = logging.getLogger(__name__)


class StatisticsDBService:
    """Service for querying lottery statistics from database"""

    def __init__(self):
        pass

    async def get_lo2so_frequency(
        self,
        province_code: str,
        days: int = 30,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, int]:
        """
        Get frequency of 2-digit numbers over a period
        
        Args:
            province_code: Province code
            days: Number of days to look back (if start_date not provided)
            start_date: Optional start date
            end_date: Optional end date (defaults to today)
            
        Returns:
            Dict of {number: count}
        """
        try:
            async with DatabaseSession() as session:
                # Set date range
                if not end_date:
                    end_date = date.today()
                if not start_date:
                    start_date = end_date - timedelta(days=days)

                # Query frequency
                query = select(
                    Lo2SoHistory.number,
                    func.count(Lo2SoHistory.id).label("count")
                ).where(
                    and_(
                        Lo2SoHistory.province_code == province_code,
                        Lo2SoHistory.draw_date >= start_date,
                        Lo2SoHistory.draw_date <= end_date
                    )
                ).group_by(Lo2SoHistory.number)

                result = await session.execute(query)

                frequency = {}
                for row in result:
                    frequency[row.number] = row.count

                logger.info(f"✅ Got frequency for {province_code}: {len(frequency)} unique numbers")
                return frequency

        except Exception as e:
            logger.error(f"❌ Error getting lo2so frequency: {e}")
            return {}

    async def get_lo_gan(
        self,
        province_code: str,
        days: int = 100,
        limit: int = 15
    ) -> list[dict]:
        """
        Get "Lô Gan" (numbers that haven't appeared recently)
        
        Args:
            province_code: Province code
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            List of dicts with {number, days_since_last, last_seen_date, max_cycle, category}
        """
        try:
            async with DatabaseSession() as session:
                end_date = date.today()
                start_date = end_date - timedelta(days=days)
                
                # Get all numbers 00-99
                all_numbers = [f"{i:02d}" for i in range(100)]
                
                # Query: Get last appearance date for each number (TOÀN BỘ LỊCH SỬ)
                query = select(
                    Lo2SoHistory.number,
                    func.max(Lo2SoHistory.draw_date).label("last_date")
                ).where(
                    Lo2SoHistory.province_code == province_code  # Chỉ filter province
                ).group_by(Lo2SoHistory.number)
                
                result = await session.execute(query)
                last_appearances = {row.number: row.last_date for row in result}
                
                # Calculate gan data
                lo_gan = []
                for num in all_numbers:
                    if num in last_appearances:
                        last_date = last_appearances[num]
                        days_since = (end_date - last_date).days - 1
                        if days_since < 0:
                            days_since = 0
                        
                        # Only include if gan (>= 10 days)
                        if days_since >= 10:
                            # Categorize
                            if days_since >= 21:
                                category = "cuc_gan"
                            elif days_since >= 16:
                                category = "gan_lon"
                            else:
                                category = "gan_thuong"
                            
                            # Calculate max cycle (simple version - just use current days_since)
                            max_cycle = days_since
                            
                            lo_gan.append({
                                "number": num,
                                "days_since_last": days_since,
                                "last_seen_date": last_date.strftime("%d/%m/%Y"),
                                "max_cycle": max_cycle,
                                "category": category
                            })
                    else:
                        # Never appeared in this period
                        lo_gan.append({
                            "number": num,
                            "days_since_last": days,
                            "last_seen_date": "Chưa về",
                            "max_cycle": days,
                            "category": "cuc_gan"
                        })
                
                # Sort by days_since_last (descending)
                lo_gan.sort(key=lambda x: x["days_since_last"], reverse=True)
                
                logger.info(f"✅ Got {len(lo_gan)} lo gan numbers for {province_code}")
                return lo_gan[:limit]
                
        except Exception as e:
            logger.error(f"❌ Error getting lo gan: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    async def get_hot_numbers(
        self,
        province_code: str,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get "hot numbers" (most frequent numbers)
        
        Args:
            province_code: Province code
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            List of dicts with {number, count}
        """
        try:
            frequency = await self.get_lo2so_frequency(province_code, days)

            # Sort by count (descending)
            hot = [
                {"number": num, "count": count}
                for num, count in sorted(frequency.items(), key=lambda x: x[1], reverse=True)
            ]

            logger.info(f"✅ Got {len(hot)} hot numbers for {province_code}")
            return hot[:limit]

        except Exception as e:
            logger.error(f"❌ Error getting hot numbers: {e}")
            return []

    async def get_cold_numbers(
        self,
        province_code: str,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get "cold numbers" (least frequent numbers that have appeared)
        
        Args:
            province_code: Province code
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            List of dicts with {number, count}
        """
        try:
            frequency = await self.get_lo2so_frequency(province_code, days)

            # Sort by count (ascending)
            cold = [
                {"number": num, "count": count}
                for num, count in sorted(frequency.items(), key=lambda x: x[1])
            ]

            logger.info(f"✅ Got {len(cold)} cold numbers for {province_code}")
            return cold[:limit]

        except Exception as e:
            logger.error(f"❌ Error getting cold numbers: {e}")
            return []

    async def get_number_history(
        self,
        province_code: str,
        number: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get history of when a specific number appeared
        
        Args:
            province_code: Province code
            number: 2-digit number (00-99)
            limit: Maximum number of results
            
        Returns:
            List of dicts with {date, prize_type}
        """
        try:
            async with DatabaseSession() as session:
                query = select(
                    Lo2SoHistory.draw_date,
                    Lo2SoHistory.prize_type
                ).where(
                    and_(
                        Lo2SoHistory.province_code == province_code,
                        Lo2SoHistory.number == number
                    )
                ).order_by(desc(Lo2SoHistory.draw_date)).limit(limit)

                result = await session.execute(query)

                history = []
                for row in result:
                    history.append({
                        "date": row.draw_date.strftime("%Y-%m-%d"),
                        "prize_type": row.prize_type
                    })

                logger.info(f"✅ Got history for number {number}: {len(history)} occurrences")
                return history

        except Exception as e:
            logger.error(f"❌ Error getting number history: {e}")
            return []

    async def get_statistics_summary(self, province_code: str, days: int = 30) -> Dict:
        """
        Get a summary of statistics for a province
        
        Args:
            province_code: Province code
            days: Number of days to look back
            
        Returns:
            Dict with various statistics
        """
        try:
            async with DatabaseSession() as session:
                end_date = date.today()
                start_date = end_date - timedelta(days=days)

                # Get total draws count
                draws_query = select(func.count(LotteryResult.id)).where(
                    and_(
                        LotteryResult.province_code == province_code,
                        LotteryResult.draw_date >= start_date,
                        LotteryResult.draw_date <= end_date
                    )
                )
                draws_result = await session.execute(draws_query)
                total_draws = draws_result.scalar() or 0

                # Get unique numbers count
                numbers_query = select(func.count(func.distinct(Lo2SoHistory.number))).where(
                    and_(
                        Lo2SoHistory.province_code == province_code,
                        Lo2SoHistory.draw_date >= start_date,
                        Lo2SoHistory.draw_date <= end_date
                    )
                )
                numbers_result = await session.execute(numbers_query)
                unique_numbers = numbers_result.scalar() or 0

                # Get frequency stats
                frequency = await self.get_lo2so_frequency(province_code, days)

                return {
                    "province_code": province_code,
                    "days": days,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "total_draws": total_draws,
                    "unique_numbers": unique_numbers,
                    "total_occurrences": sum(frequency.values()),
                    "avg_per_draw": round(sum(frequency.values()) / total_draws, 2) if total_draws > 0 else 0
                }

        except Exception as e:
            logger.error(f"❌ Error getting statistics summary: {e}")
            return {}

    async def get_lo3so_frequency_stats(
        self, 
        province_code: str, 
        days: int = 30
    ) -> dict[str, int]:
        """
        Get frequency statistics for lo 3 so (3-digit numbers)
        
        Args:
            province_code: Province code (e.g., "MB", "TPHCM")
            days: Number of days to look back
            
        Returns:
            Dictionary of {number: frequency}
        """
        from app.models import LotteryResult, Lo3SoHistory
        from sqlalchemy import select, func
        from datetime import datetime, timedelta
        
        try:
            async with DatabaseSession() as session:
                # Calculate date range
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days)
                
                # Query: Count lo3so numbers in date range
                query = (
                    select(
                        Lo3SoHistory.number,
                        func.count(Lo3SoHistory.number).label("count")
                    )
                    .where(Lo3SoHistory.province_code == province_code)
                    .where(Lo3SoHistory.draw_date >= start_date)
                    .where(Lo3SoHistory.draw_date <= end_date)
                    .group_by(Lo3SoHistory.number)
                    .order_by(func.count(Lo3SoHistory.number).desc())
                )
                
                result = await session.execute(query)
                rows = result.all()
                
                # Convert to dict
                frequency = {row[0]: row[1] for row in rows}
                
                logger.info(f"✅ Got lo3so frequency for {province_code}: {len(frequency)} unique numbers")
                return frequency
                
        except Exception as e:
            logger.error(f"❌ Error getting lo3so frequency: {e}")
            return {}