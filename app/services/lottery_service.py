from typing import Dict, List, Optional
from datetime import date, datetime, timedelta
import logging

from .api.client import MU88APIClient
from .api.transformer import DataTransformer
from .mock_data import get_mock_lottery_result  # Fallback
from app.services.cache import CacheService

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
        Get latest lottery result with 3-layer caching
        
        CACHE LAYERS:
        1. Redis (1 hour TTL) - ⚡ FASTEST (~0.001s)
        2. Database (if today) - 🚀 FAST (~0.02s)  
        3. API fetch - 🐌 SLOW (~2s)
        
        Args:
            province_code: Province code (MB, TPHCM, GILA, etc.)
            force_api: Force fetch from API even if cached (default: False)
            
        Returns:
            Standardized result dict
        """
        try:
            logger.info(f"🎯 Getting latest result for {province_code}")
            
            today = date.today()
            cache_key = f"lottery:result:{province_code}:{today}"
            
            # Layer 1: Redis cache (FASTEST)
            if not force_api:
                try:
                    cache_service = CacheService()
                    if cache_service.available:
                        cached_result = cache_service.get(cache_key)
                        if cached_result:
                            logger.info(f"⚡ Redis cache HIT for {province_code} (0.001s)")
                            return cached_result
                except Exception as e:
                    logger.warning(f"Redis cache failed: {e}")
            
            # Layer 2: Database cache (FAST)
            if not force_api and self.use_database and self.db_service:
                db_result = await self.db_service.get_latest_result(province_code)
                
                if db_result and db_result.draw_date == today:
                    result_dict = db_result.to_dict()
                    
                    # Save to Redis for next request
                    try:
                        cache_service = CacheService()
                        if cache_service.available:
                            cache_service.set(cache_key, result_dict, ttl=3600)
                            logger.info(f"💾 Saved to Redis cache: {province_code}")
                    except Exception as e:
                        logger.warning(f"Failed to cache: {e}")
                    
                    logger.info(f"🚀 DB cache HIT for {province_code} (0.02s)")
                    return result_dict
                elif db_result:
                    logger.info(f"🔄 DB has old result ({db_result.draw_date}), fetching from API...")

            # Layer 3: API fetch (SLOW)
            logger.info(f"📡 Fetching from API for {province_code}...")
            api_response = await self.api_client.fetch_results(province_code, limit=1)

            if api_response:
                results = self.transformer.transform_results(api_response)
                
                if results:
                    latest = results[0]
                    logger.info(f"✅ Got latest result from API for {province_code}: {latest.get('date')}")
                    
                    # Save to database
                    if self.use_database and self.db_service:
                        try:
                            from app.config import PROVINCES
                            province_info = PROVINCES.get(province_code, {})
                            latest["province_code"] = province_code
                            latest["region"] = province_info.get("region", "MN")
                            await self.db_service.save_result(latest)
                            logger.info(f"💾 Saved {province_code} result to DB: {latest.get('date')}")
                            
                            # Also save to Redis cache
                            try:
                                cache_service = CacheService()
                                if cache_service.available:
                                    cache_service.set(cache_key, latest, ttl=3600)
                                    logger.info(f"⚡ Saved to Redis: {province_code}")
                            except Exception as e:
                                logger.warning(f"Redis cache save failed: {e}")
                                
                        except Exception as e:
                            logger.warning(f"⚠️  Failed to save to DB: {e}")
                    
                    return latest

            # Fallback to DB (any date)
            logger.warning(f"⚠️ API failed for {province_code}, trying DB fallback...")
            if self.use_database and self.db_service:
                db_result = await self.db_service.get_latest_result(province_code)
                if db_result:
                    logger.info(f"✅ Got result from DB fallback: {db_result.draw_date}")
                    return db_result.to_dict()

            # Last resort: mock data
            logger.warning(f"⚠️ All sources failed for {province_code}, using mock data")
            return get_mock_lottery_result(province_code)

        except Exception as e:
            logger.exception(f"❌ Error getting latest result for {province_code}")
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

            # Check database first if enabled
            if self.use_database and self.db_service:
                db_results = await self.db_service.get_history(province_code, limit)
                
                # Only use DB if we have enough data
                if db_results and len(db_results) >= limit:
                    logger.info(f"✅ Got {len(db_results)} historical results from DB for {province_code}")
                    return [r.to_dict() for r in db_results]
                elif db_results:
                    logger.info(f"⚠️  DB only has {len(db_results)}/{limit} results, fetching from API...")

            # Fetch from API
            logger.info(f"📡 Fetching {limit} results from API for {province_code}...")
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
            logger.exception(f"❌ Error getting history for {province_code}")
            return []

    async def close(self):
        """Close resources"""
        pass