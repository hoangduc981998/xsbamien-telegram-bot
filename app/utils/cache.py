# app/utils/cache.py
"""Cache helper để tối ưu performance"""

from datetime import datetime
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class ScheduleCache:
    """Cache cho schedule_day với auto-refresh mỗi ngày"""
    
    _cache = {}
    _last_update_date = None
    
    @classmethod
    def get_schedule_day(cls) -> int:
        """
        Lấy schedule_day từ cache hoặc tính toán mới nếu cần
        
        Returns:
            int: Schedule day (0=Chủ Nhật, 1=Thứ Hai, ..., 6=Thứ Bảy)
        """
        today = datetime.now().date()
        
        # Kiểm tra nếu đã sang ngày mới thì làm mới cache
        if cls._last_update_date != today:
            cls._refresh_cache(today)
        
        return cls._cache.get('schedule_day')
    
    @classmethod
    def _refresh_cache(cls, today):
        """Làm mới cache với dữ liệu ngày mới"""
        weekday = datetime.now().weekday()
        schedule_day = (weekday + 1) % 7
        
        cls._cache['schedule_day'] = schedule_day
        cls._cache['weekday'] = weekday
        cls._cache['date'] = today
        cls._last_update_date = today
        
        logger.info(
            f"✅ Cache refreshed: date={today}, "
            f"weekday={weekday}, schedule_day={schedule_day}"
        )
    
    @classmethod
    def get_cache_info(cls) -> dict:
        """Lấy thông tin cache để debug"""
        return {
            'last_update': cls._last_update_date,
            'cached_data': cls._cache.copy(),
            'is_valid': cls._last_update_date == datetime.now().date()
        }
    
    @classmethod
    def clear_cache(cls):
        """Xóa cache (dùng cho testing)"""
        cls._cache.clear()
        cls._last_update_date = None
        logger.info("🗑️ Cache cleared")


# Hàm helper đơn giản để sử dụng
def get_cached_schedule_day() -> int:
    """
    Lấy schedule_day đã được cache
    
    Returns:
        int: Schedule day (0-6)
    """
    return ScheduleCache.get_schedule_day()
