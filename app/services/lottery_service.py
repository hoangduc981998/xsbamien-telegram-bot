"""Lottery Service - Main service layer for bot"""

from typing import Dict, List, Optional
import logging
from .api.client import MU88APIClient
from .api.transformer import DataTransformer
from .mock_data import get_mock_lottery_result  # Fallback

logger = logging.getLogger(__name__)


class LotteryService:
    """Main service for fetching and managing lottery data"""

    def __init__(self):
        self.api_client = MU88APIClient()
        self.transformer = DataTransformer()

    async def get_latest_result(self, province_code: str) -> Dict:
        """
        Get latest lottery result for a province

        Args:
            province_code: Province code (MB, TPHCM, GILA, etc.)

        Returns:
            Standardized result dict
        """
        try:
            logger.info(f"🎯 Getting latest result for {province_code}")

            # Fetch from API (limit 1 for latest only)
            api_response = await self.api_client.fetch_results(province_code, limit=1)

            if not api_response:
                logger.warning(f"⚠️ API failed for {province_code}, using mock data")
                return get_mock_lottery_result(province_code)

            # Transform results
            results = self.transformer.transform_results(api_response)

            if not results:
                logger.warning(f"⚠️ No results for {province_code}, using mock data")
                return get_mock_lottery_result(province_code)

            # Return latest (first in list)
            latest = results[0]
            logger.info(
                f"✅ Got latest result for {province_code}: {latest.get('date')}"
            )
            return latest

        except Exception as e:
            logger.error(f"❌ Error getting latest result for {province_code}: {e}")
            # Fallback to mock data
            return get_mock_lottery_result(province_code)

    async def get_history(self, province_code: str, limit: int = 60) -> List[Dict]:
        """
        Get historical lottery results for analysis

        Args:
            province_code: Province code
            limit: Number of results (default 60)

        Returns:
            List of standardized result dicts
        """
        try:
            logger.info(f"📊 Getting {limit} results for {province_code}")

            api_response = await self.api_client.fetch_results(province_code, limit)

            if not api_response:
                logger.warning(f"⚠️ API failed for {province_code}")
                return []

            results = self.transformer.transform_results(api_response)
            logger.info(f"✅ Got {len(results)} historical results for {province_code}")
            return results

        except Exception as e:
            logger.error(f"❌ Error getting history for {province_code}: {e}")
            return []

    async def close(self):
        """Close resources"""
        # Future: close any connections if needed
        pass
