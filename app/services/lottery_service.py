"""Lottery Service - Main service layer for bot"""

from typing import Dict, List, Optional
import logging
from datetime import date, datetime, timedelta
from .api.client import MU88APIClient
from .api.transformer import DataTransformer
from .mock_data import get_mock_lottery_result  # Fallback

logger = logging.getLogger(__name__)


class LotteryService:
    """Main service for fetching and managing lottery data"""

    def __init__(self, use_database: bool = False):
        self.api_client = MU88APIClient()
        self.transformer = DataTransformer()
        self.use_database = use_database
        self.db_service = None
        
        # Initialize database service if enabled
        if use_database:
            try:
                from .db.lottery_db_service import LotteryDBService
                self.db_service = LotteryDBService()
                logger.info("✅ Database integration enabled")
            except Exception as e:
                logger.warning(f"⚠️  Database integration disabled: {e}")
                self.use_database = False

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

            # Try database first if enabled
            if self.use_database and self.db_service:
                db_result = await self.db_service.get_latest_result(province_code)
                if db_result:
                    logger.info(f"✅ Got latest result from DB for {province_code}: {db_result.draw_date}")
                    result = db_result.to_dict()
                    # Add prizes key if not present (for backwards compatibility)
                    if "prizes" not in result:
                        result["prizes"] = result.get("prizes", {})
                    return result

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
            logger.info(f"✅ Got latest result for {province_code}: {latest.get('date')}")
            
            # Save to database if enabled
            if self.use_database and self.db_service:
                try:
                    from app.config import PROVINCES
                    province_info = PROVINCES.get(province_code, {})
                    latest["province_code"] = province_code
                    latest["region"] = province_info.get("region", "MN")
                    await self.db_service.save_result(latest)
                except Exception as e:
                    logger.warning(f"⚠️  Failed to save to DB: {e}")
            
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

            # Try database first if enabled
            if self.use_database and self.db_service:
                db_results = await self.db_service.get_history(province_code, limit)
                if db_results:
                    logger.info(f"✅ Got {len(db_results)} historical results from DB for {province_code}")
                    return [r.to_dict() for r in db_results]

            # Fetch from API
            api_response = await self.api_client.fetch_results(province_code, limit)

            if not api_response:
                logger.warning(f"⚠️ API failed for {province_code}")
                return []

            results = self.transformer.transform_results(api_response)
            logger.info(f"✅ Got {len(results)} historical results for {province_code}")
            
            # Save to database if enabled
            if self.use_database and self.db_service:
                try:
                    from app.config import PROVINCES
                    province_info = PROVINCES.get(province_code, {})
                    region = province_info.get("region", "MN")
                    
                    for result in results:
                        result["province_code"] = province_code
                        result["region"] = region
                        await self.db_service.save_result(result)
                except Exception as e:
                    logger.warning(f"⚠️  Failed to save history to DB: {e}")
            
            return results

        except Exception as e:
            logger.error(f"❌ Error getting history for {province_code}: {e}")
            return []

    async def close(self):
        """Close resources"""
        # Future: close any connections if needed
        pass
