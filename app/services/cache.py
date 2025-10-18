"""Cache service using Redis"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache service with graceful fallback"""
    
    def __init__(self):
        """Initialize Redis connection with error handling"""
        self.available = False
        self.redis_client = None
        
        try:
            import redis
            self.redis_client = redis.Redis(
                host="localhost",
                port=6379,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            
            # Test connection
            self.redis_client.ping()
            self.available = True
            logger.info("✅ Redis cache initialized and available")
            
        except ImportError:
            logger.warning("⚠️ Redis package not installed, cache disabled")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available, cache disabled: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.available:
            return None
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.warning(f"Redis get error for key '{key}': {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 3600 = 1 hour)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            return False
        
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)  # default=str for datetime objects
            )
            return True
        except Exception as e:
            logger.warning(f"Redis set error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis delete error for key '{key}': {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern
        
        Args:
            pattern: Key pattern (e.g., 'lottery:*')
            
        Returns:
            Number of keys deleted
        """
        if not self.available:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis clear_pattern error for pattern '{pattern}': {e}")
            return 0
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dict with cache stats
        """
        if not self.available:
            return {"available": False, "keys": 0}
        
        try:
            info = self.redis_client.info()
            return {
                "available": True,
                "keys": info.get("db0", {}).get("keys", 0),
                "memory": info.get("used_memory_human", "N/A"),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            logger.warning(f"Redis get_stats error: {e}")
            return {"available": False, "error": str(e)}
