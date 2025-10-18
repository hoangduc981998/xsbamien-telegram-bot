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

    async def get_latest_result(self, province_code: str, force_api: bool = False) -> Dict:
        """
        Get latest lottery result for a province
        
        Strategy:
        1. Check DB first - if has TODAY's result → return immediately (cached)
        2. If no today's result or force_api=True → fetch from API
        3. Save new API result to DB
        4. Fallback to DB if API fails
        5. Fallback to mock data if both fail
        
        Args:
            province_code: Province code (MB, TPHCM, GILA, etc.)
            force_api: Force fetch from API even if DB has data (default: False)
        Returns:
            Standardized result dict
        """
        try:
            logger.info(f"🎯 Getting latest result for {province_code}")
            
            # ✅ SMART CACHING: Check DB first unless forced
            if not force_api and self.use_database and self.db_service:
                db_result = await self.db_service.get_latest_result(province_code)
                
                if db_result:
                    # Check if it's today's result
                    from datetime import date
                    today = date.today()
                    
                    if db_result.draw_date == today:
                        logger.info(f"💾 Using cached result from DB for {province_code}: {db_result.draw_date}")
                        result = db_result.to_dict()
                        if "prizes" not in result:
                            result["prizes"] = result.get("prizes", {})
                        return result
                    else:
                        logger.info(f"🔄 DB has old result ({db_result.draw_date}), fetching from API...")

            # ✅ Fetch from API if no today's result in DB
            logger.info(f"📡 Fetching from API for {province_code}...")
            api_response = await self.api_client.fetch_results(province_code, limit=1)

            if api_response:
                # Transform results
                results = self.transformer.transform_results(api_response)
                
                if results:
                    # Return latest (first in list)
                    latest = results[0]
                    logger.info(f"✅ Got latest result from API for {province_code}: {latest.get('date')}")
                    
                    # Save to database if enabled
                    if self.use_database and self.db_service:
                        try:
                            from app.config import PROVINCES
                            province_info = PROVINCES.get(province_code, {})
                            latest["province_code"] = province_code
                            latest["region"] = province_info.get("region", "MN")
                            await self.db_service.save_result(latest)
                            logger.info(f"💾 Saved {province_code} result to DB: {latest.get('date')}")
                        except Exception as e:
                            logger.warning(f"⚠️  Failed to save to DB: {e}")
                    
                    return latest

            # ⚠️ API failed, try database as fallback
            logger.warning(f"⚠️ API failed for {province_code}, trying DB fallback...")
            
            if self.use_database and self.db_service:
                db_result = await self.db_service.get_latest_result(province_code)
                if db_result:
                    logger.info(f"✅ Got result from DB fallback for {province_code}: {db_result.draw_date}")
                    result = db_result.to_dict()
                    if "prizes" not in result:
                        result["prizes"] = result.get("prizes", {})
                    return result

            # ❌ Both API and DB failed, use mock data
            logger.warning(f"⚠️ Both API and DB failed for {province_code}, using mock data")

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
