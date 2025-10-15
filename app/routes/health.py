"""
Health check endpoints for monitoring and Cloud Run
These endpoints can be used for liveness and readiness probes
"""

import os
import subprocess
import time
from datetime import datetime
from typing import Dict, Any

import psutil


class HealthCheckService:
    """Health check service with multiple probe endpoints"""

    def __init__(self):
        self.start_time = time.time()
        self.version = self._get_version()

    @staticmethod
    def _get_version() -> str:
        """Get version from git tag or default to 1.0.0"""
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--always"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "1.0.0"

    def get_uptime(self) -> float:
        """Get service uptime in seconds"""
        return time.time() - self.start_time

    def check_bot_status(self) -> str:
        """Check if bot token is configured"""
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if token and len(token) > 10:
            return "configured"
        return "not_configured"

    def check_cache(self) -> str:
        """Check cache availability"""
        cache_type = os.getenv("CACHE_TYPE", "memory")
        cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"

        if not cache_enabled:
            return "disabled"

        if cache_type == "redis":
            redis_url = os.getenv("REDIS_URL", "")
            if redis_url:
                return "configured"
            return "not_configured"

        return "memory"

    def check_database(self) -> str:
        """Check database status (placeholder for future implementation)"""
        # For now, the bot doesn't use a database
        return "not_applicable"

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system resource statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory.percent, 2),
                "memory_available_mb": round(memory.available / 1024 / 1024, 2),
                "disk_percent": round(disk.percent, 2),
                "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
            }
        except Exception:
            return {}

    def health_check(self) -> Dict[str, Any]:
        """
        Basic health check endpoint
        Returns: Status and basic info
        """
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": round(self.get_uptime(), 2),
            "version": self.version,
            "environment": os.getenv("ENVIRONMENT", "development"),
        }

    def liveness_probe(self) -> Dict[str, Any]:
        """
        Liveness probe - checks if the service is running
        Used by Cloud Run to determine if the service should be restarted
        """
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": round(self.get_uptime(), 2),
        }

    def readiness_probe(self) -> Dict[str, Any]:
        """
        Readiness probe - checks if the service is ready to accept traffic
        Used by Cloud Run to determine if traffic should be routed to this instance
        """
        bot_status = self.check_bot_status()
        is_ready = bot_status == "configured"

        return {
            "status": "ready" if is_ready else "not_ready",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {
                "bot_token": bot_status,
                "cache": self.check_cache(),
                "database": self.check_database(),
            },
        }

    def full_status(self) -> Dict[str, Any]:
        """
        Comprehensive status endpoint with all details
        """
        bot_status = self.check_bot_status()
        is_healthy = bot_status == "configured"

        return {
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": round(self.get_uptime(), 2),
            "version": self.version,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "services": {
                "telegram_bot": bot_status,
                "cache": self.check_cache(),
                "database": self.check_database(),
            },
            "system": self.get_system_stats(),
            "config": {
                "log_level": os.getenv("LOG_LEVEL", "INFO"),
                "cache_enabled": os.getenv("CACHE_ENABLED", "true"),
                "cache_ttl": int(os.getenv("CACHE_TTL", "3600")),
            },
        }


# Global instance
_health_service = None


def get_health_service() -> HealthCheckService:
    """Get or create health service instance"""
    global _health_service
    if _health_service is None:
        _health_service = HealthCheckService()
    return _health_service


# Convenience functions for easy import
def health_check() -> Dict[str, Any]:
    """Basic health check"""
    return get_health_service().health_check()


def liveness_probe() -> Dict[str, Any]:
    """Liveness probe"""
    return get_health_service().liveness_probe()


def readiness_probe() -> Dict[str, Any]:
    """Readiness probe"""
    return get_health_service().readiness_probe()


def full_status() -> Dict[str, Any]:
    """Full status"""
    return get_health_service().full_status()
