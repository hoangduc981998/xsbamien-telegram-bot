"""Statistics Service - Lottery statistics and analysis"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for lottery statistics and analysis"""

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

    def get_frequency_stats(self, numbers: list, days: int = 30) -> dict:
        """
        Calculate frequency statistics (currently mock, DB later)
        
        Args:
            numbers: List of numbers to analyze
            days: Number of days to analyze (for future DB implementation)
            
        Returns:
            Mock frequency stats
        """
        # For now, return mock data
        # In PR #2, this will query the database
        logger.info(f"Getting frequency stats for {len(numbers)} numbers over {days} days (mock)")
        
        import random
        random.seed(hash(str(numbers)))
        
        stats = {}
        for num in numbers[:10]:  # Top 10
            stats[num] = random.randint(5, 30)
        
        return stats

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
