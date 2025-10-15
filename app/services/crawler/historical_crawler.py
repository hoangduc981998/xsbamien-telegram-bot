"""Historical lottery data crawler using MU88 API"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime

from app.services.api.client import MU88APIClient
from app.services.api.transformer import DataTransformer
from app.services.db.lottery_db_service import LotteryDBService
from app.config import PROVINCES

logger = logging.getLogger(__name__)


class HistoricalDataCrawler:
    """Crawler for fetching and storing historical lottery data"""

    def __init__(self):
        self.api_client = MU88APIClient()
        self.transformer = DataTransformer()
        self.db_service = LotteryDBService()

    async def crawl_province(
        self,
        province_code: str,
        limit: int = 100,
        skip_existing: bool = True
    ) -> Dict:
        """
        Crawl historical data for a single province
        
        Args:
            province_code: Province code (MB, TPHCM, etc.)
            limit: Number of results to fetch (max 100)
            skip_existing: Skip if data already exists in DB
            
        Returns:
            Dict with crawl statistics
        """
        try:
            logger.info(f"🔍 Starting crawl for {province_code} (limit: {limit})")
            
            # Check if we should skip
            if skip_existing:
                existing_count = await self.db_service.get_results_count(province_code)
                if existing_count >= limit:
                    logger.info(f"⏭️  Skipping {province_code}: {existing_count} results already exist")
                    return {
                        "province_code": province_code,
                        "status": "skipped",
                        "existing_count": existing_count,
                        "fetched": 0,
                        "saved": 0
                    }
            
            # Fetch from API
            logger.info(f"📡 Fetching {limit} results for {province_code}")
            api_response = await self.api_client.fetch_results(province_code, limit)
            
            if not api_response:
                logger.warning(f"⚠️  API failed for {province_code}")
                return {
                    "province_code": province_code,
                    "status": "error",
                    "error": "API failed"
                }
            
            # Transform results
            results = self.transformer.transform_results(api_response)
            logger.info(f"✅ Transformed {len(results)} results for {province_code}")
            
            # Get province info
            province_info = PROVINCES.get(province_code, {})
            region = province_info.get("region", "MN")
            
            # Save to database
            saved_count = 0
            for result in results:
                # Add metadata
                result["province_code"] = province_code
                result["region"] = region
                
                # Save to DB
                saved = await self.db_service.save_result(result)
                if saved:
                    saved_count += 1
            
            logger.info(f"✅ Saved {saved_count}/{len(results)} results for {province_code}")
            
            return {
                "province_code": province_code,
                "status": "success",
                "fetched": len(results),
                "saved": saved_count
            }

        except Exception as e:
            logger.error(f"❌ Error crawling {province_code}: {e}")
            return {
                "province_code": province_code,
                "status": "error",
                "error": str(e)
            }

    async def crawl_all_provinces(
        self,
        limit: int = 100,
        skip_existing: bool = True,
        delay: float = 1.0
    ) -> Dict:
        """
        Crawl historical data for all provinces
        
        Args:
            limit: Number of results per province
            skip_existing: Skip provinces that already have data
            delay: Delay between requests (seconds)
            
        Returns:
            Dict with overall crawl statistics
        """
        logger.info(f"🚀 Starting crawl for all provinces (limit: {limit})")
        
        start_time = datetime.now()
        results = []
        
        for province_code in PROVINCES.keys():
            result = await self.crawl_province(province_code, limit, skip_existing)
            results.append(result)
            
            # Add delay to avoid rate limiting
            if delay > 0:
                await asyncio.sleep(delay)
        
        # Calculate statistics
        total_fetched = sum(r.get("fetched", 0) for r in results)
        total_saved = sum(r.get("saved", 0) for r in results)
        success_count = sum(1 for r in results if r.get("status") == "success")
        error_count = sum(1 for r in results if r.get("status") == "error")
        skipped_count = sum(1 for r in results if r.get("status") == "skipped")
        
        duration = (datetime.now() - start_time).total_seconds()
        
        summary = {
            "start_time": start_time.isoformat(),
            "duration_seconds": duration,
            "total_provinces": len(PROVINCES),
            "success": success_count,
            "errors": error_count,
            "skipped": skipped_count,
            "total_fetched": total_fetched,
            "total_saved": total_saved,
            "results": results
        }
        
        logger.info(f"✅ Crawl completed: {success_count} success, {error_count} errors, {skipped_count} skipped")
        logger.info(f"📊 Total: {total_saved} results saved in {duration:.2f}s")
        
        return summary

    async def crawl_region(
        self,
        region: str,
        limit: int = 100,
        skip_existing: bool = True,
        delay: float = 1.0
    ) -> Dict:
        """
        Crawl historical data for all provinces in a region
        
        Args:
            region: Region code (MB, MN, MT)
            limit: Number of results per province
            skip_existing: Skip provinces that already have data
            delay: Delay between requests (seconds)
            
        Returns:
            Dict with crawl statistics
        """
        logger.info(f"🚀 Starting crawl for region {region} (limit: {limit})")
        
        start_time = datetime.now()
        results = []
        
        # Filter provinces by region
        region_provinces = [
            code for code, info in PROVINCES.items()
            if info.get("region") == region
        ]
        
        for province_code in region_provinces:
            result = await self.crawl_province(province_code, limit, skip_existing)
            results.append(result)
            
            # Add delay to avoid rate limiting
            if delay > 0:
                await asyncio.sleep(delay)
        
        # Calculate statistics
        total_fetched = sum(r.get("fetched", 0) for r in results)
        total_saved = sum(r.get("saved", 0) for r in results)
        success_count = sum(1 for r in results if r.get("status") == "success")
        error_count = sum(1 for r in results if r.get("status") == "error")
        skipped_count = sum(1 for r in results if r.get("status") == "skipped")
        
        duration = (datetime.now() - start_time).total_seconds()
        
        summary = {
            "region": region,
            "start_time": start_time.isoformat(),
            "duration_seconds": duration,
            "total_provinces": len(region_provinces),
            "success": success_count,
            "errors": error_count,
            "skipped": skipped_count,
            "total_fetched": total_fetched,
            "total_saved": total_saved,
            "results": results
        }
        
        logger.info(f"✅ Region {region} crawl completed: {success_count} success, {error_count} errors")
        logger.info(f"📊 Total: {total_saved} results saved in {duration:.2f}s")
        
        return summary

    async def update_latest(self, province_codes: Optional[List[str]] = None) -> Dict:
        """
        Update with latest results for specified provinces
        
        Args:
            province_codes: List of province codes (if None, update all)
            
        Returns:
            Dict with update statistics
        """
        if province_codes is None:
            province_codes = list(PROVINCES.keys())
        
        logger.info(f"🔄 Updating latest results for {len(province_codes)} provinces")
        
        results = []
        for province_code in province_codes:
            result = await self.crawl_province(province_code, limit=1, skip_existing=False)
            results.append(result)
        
        success_count = sum(1 for r in results if r.get("status") == "success")
        
        logger.info(f"✅ Update completed: {success_count}/{len(province_codes)} successful")
        
        return {
            "updated_count": success_count,
            "total_requested": len(province_codes),
            "results": results
        }
