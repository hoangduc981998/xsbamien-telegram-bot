"""
Cache module for schedule_day optimization.

This module provides in-memory caching for schedule_day calculation
to avoid repetitive date/weekday computation across multiple user requests.
"""

from datetime import datetime
from typing import Dict, Optional, Any


class ScheduleCache:
    """
    In-memory cache for schedule_day calculation.

    Caches the schedule_day value and automatically refreshes when a new day begins.
    This significantly reduces CPU usage when multiple users access the bot simultaneously.
    """

    _cache: Dict[str, Any] = {}
    _last_update_date: Optional[datetime] = None

    @classmethod
    def get_schedule_day(cls) -> int:
        """
        Get the current schedule_day from cache or calculate it.

        Automatically refreshes cache when a new day begins.

        Returns:
            int: Schedule day (0=Sunday, 1=Monday, ..., 6=Saturday)
        """
        today = datetime.now().date()

        # Refresh cache if it's a new day
        if cls._last_update_date != today:
            cls._refresh_cache(today)

        return cls._cache.get('schedule_day')

    @classmethod
    def _refresh_cache(cls, today) -> None:
        """
        Refresh the cache with current date information.

        Args:
            today: The current date
        """
        weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday
        schedule_day = (weekday + 1) % 7  # Convert to 0=Sunday, 1=Monday, ..., 6=Saturday

        cls._cache['schedule_day'] = schedule_day
        cls._cache['weekday'] = weekday
        cls._cache['date'] = today
        cls._last_update_date = today

    @classmethod
    def get_cache_info(cls) -> Dict[str, Any]:
        """
        Get cache information for debugging/monitoring.

        Returns:
            Dict containing cache status and data
        """
        today = datetime.now().date()
        is_valid = cls._last_update_date == today

        return {
            'last_update': cls._last_update_date,
            'cached_data': cls._cache.copy(),
            'is_valid': is_valid
        }

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear the cache. Primarily used for testing.
        """
        cls._cache = {}
        cls._last_update_date = None


def get_cached_schedule_day() -> int:
    """
    Helper function to get cached schedule_day.

    Returns:
        int: Schedule day (0=Sunday, 1=Monday, ..., 6=Saturday)
    """
    return ScheduleCache.get_schedule_day()
