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
                'by_head': {i: [] for i in range(10)},
                'by_tail': {i: [] for i in range(10)},
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
