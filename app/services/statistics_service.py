"""Statistics Service - Lottery statistics and analysis"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for lottery statistics and analysis"""
    
    def __init__(self, use_database: bool = False):
        self.use_database = use_database
        self.db_service = None
        
        # Initialize database service if enabled
        if use_database:
            try:
                from .db.statistics_db_service import StatisticsDBService
                self.db_service = StatisticsDBService()
                logger.info("✅ Database statistics enabled")
            except Exception as e:
                logger.warning(f"⚠️  Database statistics disabled: {e}")
                self.use_database = False

    def analyze_lo_2_so(self, result_data: dict) -> dict:
        """
        Analyze 2-digit lottery numbers from result

        Args:
            result_data: Result data dict with prizes

        Returns:
            {
                'all_numbers': ['45', '12', '78', ...],  # All 2-digit numbers
                'frequency': {'45': 2, '12': 1, ...},    # Frequency count
                'by_head': {0: ['01', '05'], 1: ['12', '15'], ...},  # Group by tens
                'by_tail': {0: ['10', '20'], 1: ['01', '21'], ...},  # Group by units
                'date': '2025-10-15',
                'province': 'TP.HCM'
            }
        """
        try:
            # Extract prizes from result_data
            if "prizes" in result_data:
                prizes = result_data["prizes"]
            else:
                prizes = result_data

            date = result_data.get("date", "")
            province = result_data.get("province", "")

            # Collect all 2-digit numbers
            lo2_list = []
            prize_keys = ["DB", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]

            for prize_key in prize_keys:
                if prize_key in prizes and prizes[prize_key]:
                    for num in prizes[prize_key]:
                        if len(num) >= 2:
                            lo2 = num[-2:]  # Last 2 digits
                            lo2_list.append(lo2)

            # Calculate frequency
            frequency = {}
            for num in lo2_list:
                frequency[num] = frequency.get(num, 0) + 1

            # Group by head (tens digit)
            by_head = {i: [] for i in range(10)}
            for num in set(lo2_list):  # Use set to avoid duplicates
                head = int(num[0])
                by_head[head].append(num)

            # Sort numbers within each head group
            for head in by_head:
                by_head[head].sort()

            # Group by tail (units digit)
            by_tail = {i: [] for i in range(10)}
            for num in set(lo2_list):
                tail = int(num[1])
                by_tail[tail].append(num)

            # Sort numbers within each tail group
            for tail in by_tail:
                by_tail[tail].sort()

            return {
                'all_numbers': sorted(list(set(lo2_list))),
                'frequency': frequency,
                'by_head': by_head,
                'by_tail': by_tail,
                'date': date,
                'province': province,
            }

        except Exception as e:
            logger.error(f"Error analyzing lo 2 so: {e}")
            return {
                'all_numbers': [],
                'frequency': {},
                'by_head': {str(i): [] for i in range(10)},
                'by_tail': {str(i): [] for i in range(10)},
                'date': '',
                'province': '',
            }

    def analyze_lo_3_so(self, result_data: dict) -> dict:
        """
        Analyze 3-digit lottery numbers from result

        Args:
            result_data: Result data dict with prizes

        Returns:
            {
                'all_numbers': ['456', '123', '789', ...],
                'frequency': {'456': 2, '123': 1, ...},
                'date': '2025-10-15',
                'province': 'TP.HCM'
            }
        """
        try:
            # Extract prizes from result_data
            if "prizes" in result_data:
                prizes = result_data["prizes"]
            else:
                prizes = result_data

            date = result_data.get("date", "")
            province = result_data.get("province", "")

            # Collect all 3-digit numbers
            lo3_list = []
            prize_keys = ["DB", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]

            for prize_key in prize_keys:
                if prize_key in prizes and prizes[prize_key]:
                    for num in prizes[prize_key]:
                        if len(num) >= 3:
                            lo3 = num[-3:]  # Last 3 digits
                            lo3_list.append(lo3)

            # Calculate frequency
            frequency = {}
            for num in lo3_list:
                frequency[num] = frequency.get(num, 0) + 1

            return {
                'all_numbers': sorted(list(set(lo3_list))),
                'frequency': frequency,
                'date': date,
                'province': province,
            }

        except Exception as e:
            logger.error(f"Error analyzing lo 3 so: {e}")
            return {
                'all_numbers': [],
                'frequency': {},
                'date': '',
                'province': '',
            }

    async def get_frequency_stats(
        self, 
        province_code: str, 
        days: int = 30
    ) -> dict:
        """
        Calculate frequency statistics from database or mock data

        Args:
            province_code: Province code
            days: Number of days to analyze

        Returns:
            Frequency stats dict {number: count}
        """
        # Use database if available
        if self.use_database and self.db_service:
            try:
                logger.info(f"Getting frequency stats from DB for {province_code} ({days} days)")
                frequency = await self.db_service.get_lo2so_frequency(province_code, days)
                return frequency
            except Exception as e:
                logger.warning(f"⚠️  DB query failed, using mock data: {e}")
        
        # Fallback to mock data
        logger.info(f"Getting frequency stats (mock) for {province_code} over {days} days")
        
        import random
        random.seed(hash(str(province_code) + str(days)))
        
        stats = {}
        for i in range(10):  # Top 10
            num = f"{random.randint(0, 99):02d}"
            stats[num] = random.randint(5, 30)
        
        return stats
    
    async def get_lo3so_frequency_stats(
        self, 
        province_code: str, 
        days: int = 30
    ) -> dict[str, int]:
        """
        Get lo 3 so frequency from database
    
        Args:
            province_code: Province code
            days: Number of days to analyze
        
        Returns:
            Frequency stats dict {number: count}
        """
        # Use database if available
        if self.use_database and self.db_service:
            try:
                logger.info(f"Getting lo3so frequency stats from DB for {province_code} ({days} days)")
                frequency = await self.db_service.get_lo3so_frequency_stats(province_code, days)
                return frequency
            except Exception as e:
                logger.warning(f"⚠️  DB query failed for lo3so: {e}")
                return {}
    
        # No fallback - return empty if DB not available
        logger.warning(f"Database not enabled for lo3so frequency stats")
        return {}
    async def get_lo_gan(
        self, 
        province_code: str, 
        draws: int = 200,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get Lô Gan (cold numbers) from database or mock data

        Args:
            province_code: Province code
            draws: Number of draw periods to analyze (default: 200)
            limit: Maximum number of results

        Returns:
            List of dicts with {number, gan_value, days_since_last, periods_since_last, 
                                last_seen_date, max_cycle, is_daily, category,
                                analysis_draws, analysis_days, analysis_window}
        """
        # Use database if available
        if self.use_database and self.db_service:
            try:
                logger.info(f"Getting lô gan from DB for {province_code} ({draws} draws)")
                lo_gan = await self.db_service.get_lo_gan(
                    province_code,
                    draws=draws,
                    limit=limit
                )
                return lo_gan
            except Exception as e:
                logger.warning(f"⚠️  DB query failed, using mock data: {e}")
        
        # Fallback to mock data
        logger.info(f"Getting lô gan (mock) for {province_code}")
        
        import random
        random.seed(hash(str(province_code) + str(draws)))
        
        lo_gan = []
        for i in range(limit):
            num = f"{random.randint(0, 99):02d}"
            lo_gan.append({
                "number": num,
                "gan_value": random.randint(10, 30),
                "days_since_last": random.randint(10, 30),
                "periods_since_last": random.randint(3, 10),
                "last_seen_date": None,
                "max_cycle": random.randint(15, 40),
                "is_daily": province_code == "MB",
                "category": "gan_thuong",
                "analysis_draws": draws,
                "analysis_days": draws if province_code == "MB" else draws * 7,
                "analysis_window": f"{draws} {'ngày' if province_code == 'MB' else 'kỳ'}"
            })
        
        return lo_gan
    
    async def get_hot_numbers(
        self, 
        province_code: str, 
        days: int = 30, 
        limit: int = 10
    ) -> List[Dict]:
        """
        Get hot numbers (most frequent) from database or mock data

        Args:
            province_code: Province code
            days: Number of days to look back
            limit: Maximum number of results

        Returns:
            List of dicts with {number, count}
        """
        # Use database if available
        if self.use_database and self.db_service:
            try:
                logger.info(f"Getting hot numbers from DB for {province_code} ({days} days)")
                hot = await self.db_service.get_hot_numbers(province_code, days, limit)
                return hot
            except Exception as e:
                logger.warning(f"⚠️  DB query failed, using mock data: {e}")
        
        # Fallback to mock data
        frequency = await self.get_frequency_stats(province_code, days)
        hot = [
            {"number": num, "count": count}
            for num, count in sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        ]
        return hot[:limit]

    def format_frequency_table(self, freq_data: dict) -> str:
        """
        Format frequency data as HTML table for Telegram

        Args:
            freq_data: Dict of {number: count}

        Returns:
            Formatted HTML string
        """
        if not freq_data:
            return "Không có dữ liệu"

        # Sort by frequency (descending)
        sorted_freq = sorted(freq_data.items(), key=lambda x: x[1], reverse=True)

        lines = []
        for num, count in sorted_freq[:10]:  # Top 10
            lines.append(f"• <b>{num}</b>: {count} lần")

        return "\n".join(lines)
    async def get_lo2so_streaks(self, province_code: str, draws: int = 200, min_streak: int = 2) -> dict:
        """
        Phân tích chuỗi liên tiếp cho lô 2 số
        
        Args:
            province_code: Mã tỉnh (MB, TPHCM, etc.)
            draws: Số kỳ quay phân tích
            min_streak: Ngưỡng tối thiểu (mặc định 2 kỳ)
            
        Returns:
            Dict {current_streaks: [...], max_streaks: [...]}
        """
        from app.database import DatabaseSession
        from app.models import Lo2SoHistory
        from sqlalchemy import select, and_
        
        try:
            async with DatabaseSession() as session:
                # Lấy danh sách ngày quay
                date_query = select(Lo2SoHistory.draw_date).where(
                    Lo2SoHistory.province_code == province_code
                ).distinct().order_by(Lo2SoHistory.draw_date.desc()).limit(draws)
                
                date_result = await session.execute(date_query)
                draw_dates = sorted([row[0] for row in date_result.fetchall()])
                
                if not draw_dates:
                    return {"current_streaks": [], "max_streaks": []}
                
                # Lấy dữ liệu lô 2 số
                data_query = select(Lo2SoHistory.draw_date, Lo2SoHistory.number).where(
                    and_(Lo2SoHistory.province_code == province_code, Lo2SoHistory.draw_date.in_(draw_dates))
                ).order_by(Lo2SoHistory.draw_date.asc())
                
                data_result = await session.execute(data_query)
                all_data = data_result.fetchall()
                
                # Tổ chức theo ngày
                draws_by_date = {}
                for draw_date, number in all_data:
                    if draw_date not in draws_by_date:
                        draws_by_date[draw_date] = set()
                    draws_by_date[draw_date].add(number)
                
                # Phân tích streak cho tất cả số 00-99
                all_numbers = [f"{i:02d}" for i in range(100)]
                current_streaks = {}
                max_streaks = {}
                
                for number in all_numbers:
                    temp_streak = 0
                    temp_start = None
                    max_streak_val = 0
                    max_streak_date = None
                    
                    for draw_date in draw_dates:
                        if number in draws_by_date.get(draw_date, set()):
                            if temp_streak == 0:
                                temp_start = draw_date
                            temp_streak += 1
                            if temp_streak > max_streak_val:
                                max_streak_val = temp_streak
                                max_streak_date = draw_date
                        else:
                            temp_streak = 0
                    
                    # Current streak (cuối cùng)
                    if temp_streak >= min_streak:
                        current_streaks[number] = {
                            "streak": temp_streak,
                            "start_date": temp_start,
                            "end_date": draw_dates[-1]
                        }
                    
                    # Max streak (lịch sử)
                    if max_streak_val >= min_streak:
                        max_streaks[number] = {
                            "max_streak": max_streak_val,
                            "last_streak_date": max_streak_date
                        }
                
                # Format kết quả
                current_list = [
                    {
                        "number": n,
                        "streak": d["streak"],
                        "start_date": d["start_date"].strftime("%d/%m/%Y"),
                        "end_date": d["end_date"].strftime("%d/%m/%Y")
                    }
                    for n, d in sorted(current_streaks.items(), key=lambda x: x[1]["streak"], reverse=True)
                ][:15]
                
                max_list = [
                    {
                        "number": n,
                        "max_streak": d["max_streak"],
                        "last_streak_date": d["last_streak_date"].strftime("%d/%m/%Y")
                    }
                    for n, d in sorted(max_streaks.items(), key=lambda x: x[1]["max_streak"], reverse=True)
                ][:15]
                
                logger.info(f"✅ Lo2so streaks: {len(current_list)} current, {len(max_list)} max")
                return {"current_streaks": current_list, "max_streaks": max_list}
        except Exception as e:
            logger.error(f"Error in get_lo2so_streaks: {e}")
            return {"current_streaks": [], "max_streaks": []}
    
    async def get_lo3so_streaks(self, province_code: str, draws: int = 200, min_streak: int = 2) -> dict:
        """Phân tích chuỗi liên tiếp cho lô 3 số"""
        from app.database import DatabaseSession
        from app.models import Lo3SoHistory
        from sqlalchemy import select, and_
        
        try:
            async with DatabaseSession() as session:
                date_query = select(Lo3SoHistory.draw_date).where(
                    Lo3SoHistory.province_code == province_code
                ).distinct().order_by(Lo3SoHistory.draw_date.desc()).limit(draws)
                
                date_result = await session.execute(date_query)
                draw_dates = sorted([row[0] for row in date_result.fetchall()])
                
                if not draw_dates:
                    return {"current_streaks": [], "max_streaks": []}
                
                data_query = select(Lo3SoHistory.draw_date, Lo3SoHistory.number).where(
                    and_(Lo3SoHistory.province_code == province_code, Lo3SoHistory.draw_date.in_(draw_dates))
                ).order_by(Lo3SoHistory.draw_date.asc())
                
                data_result = await session.execute(data_query)
                all_data = data_result.fetchall()
                
                draws_by_date = {}
                unique_numbers = set()
                for draw_date, number in all_data:
                    if draw_date not in draws_by_date:
                        draws_by_date[draw_date] = set()
                    draws_by_date[draw_date].add(number)
                    unique_numbers.add(number)
                
                current_streaks = {}
                max_streaks = {}
                
                for number in unique_numbers:
                    temp_streak = 0
                    temp_start = None
                    max_streak_val = 0
                    max_streak_date = None
                    
                    for draw_date in draw_dates:
                        if number in draws_by_date.get(draw_date, set()):
                            if temp_streak == 0:
                                temp_start = draw_date
                            temp_streak += 1
                            if temp_streak > max_streak_val:
                                max_streak_val = temp_streak
                                max_streak_date = draw_date
                        else:
                            temp_streak = 0
                    
                    if temp_streak >= min_streak:
                        current_streaks[number] = {
                            "streak": temp_streak,
                            "start_date": temp_start,
                            "end_date": draw_dates[-1]
                        }
                    
                    if max_streak_val >= min_streak:
                        max_streaks[number] = {
                            "max_streak": max_streak_val,
                            "last_streak_date": max_streak_date
                        }
                
                current_list = [
                    {
                        "number": n,
                        "streak": d["streak"],
                        "start_date": d["start_date"].strftime("%d/%m/%Y"),
                        "end_date": d["end_date"].strftime("%d/%m/%Y")
                    }
                    for n, d in sorted(current_streaks.items(), key=lambda x: x[1]["streak"], reverse=True)
                ][:15]
                
                max_list = [
                    {
                        "number": n,
                        "max_streak": d["max_streak"],
                        "last_streak_date": d["last_streak_date"].strftime("%d/%m/%Y")
                    }
                    for n, d in sorted(max_streaks.items(), key=lambda x: x[1]["max_streak"], reverse=True)
                ][:15]
                
                logger.info(f"✅ Lo3so streaks: {len(current_list)} current, {len(max_list)} max")
                return {"current_streaks": current_list, "max_streaks": max_list}
        except Exception as e:
            logger.error(f"Error in get_lo3so_streaks: {e}")
            return {"current_streaks": [], "max_streaks": []}