# app/services/health.py
from typing import Dict
import time


class HealthCheck:
    def __init__(self):
        self.start_time = time.time()

    def get_status(self) -> Dict[str, any]:
        return {
            "status": "healthy",
            "uptime": time.time() - self.start_time,
            "version": "1.0.0",
            "services": {"telegram_bot": "running", "cache": self._check_redis(), "database": self._check_db()},
        }
