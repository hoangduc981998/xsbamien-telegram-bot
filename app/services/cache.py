# app/services/cache.py
from functools import lru_cache
import redis


class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

    def get_lottery_result(self, region: str, date: str):
        key = f"lottery:{region}:{date}"
        cached = self.redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None

    def set_lottery_result(self, region: str, date: str, data: dict):
        key = f"lottery:{region}:{date}"
        self.redis_client.setex(key, 3600, json.dumps(data))  # 1 hour TTL
