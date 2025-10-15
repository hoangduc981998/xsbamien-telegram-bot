"""Cache helper để tối ưu performance với comprehensive logging"""

from datetime import datetime
import logging

logger = logging.getLogger('app.utils.cache')


class ScheduleCache:
    """Cache cho schedule_day với auto-refresh và logging"""
    
    _cache = {}
    _last_update_date = None
    _cache_hits = 0
    _cache_misses = 0
    
    @classmethod
    def get_schedule_day(cls) -> int:
        """
        Lấy schedule_day từ cache hoặc tính toán mới nếu cần
        
        Returns:
            int: Schedule day (0=Chủ Nhật, 1=Thứ Hai, ..., 6=Thứ Bảy)
        """
        today = datetime.now().date()
        
        # Log cache check
        logger.debug(
            f"Cache check: today={today}, last_update={cls._last_update_date}"
        )
        
        # Kiểm tra nếu đã sang ngày mới thì làm mới cache
        if cls._last_update_date != today:
            cls._cache_misses += 1
            logger.info(
                f"🔄 Cache MISS: Date changed from "
                f"{cls._last_update_date} to {today}"
            )
            cls._refresh_cache(today)
        else:
            cls._cache_hits += 1
            logger.debug(
                f"✅ Cache HIT: Using cached value "
                f"(hits={cls._cache_hits}, misses={cls._cache_misses})"
            )
        
        return cls._cache.get('schedule_day')
    
    @classmethod
    def _refresh_cache(cls, today):
        """Làm mới cache với logging chi tiết"""
        weekday = datetime.now().weekday()
        schedule_day = (weekday + 1) % 7
        
        # Weekday names for logging
        weekday_names = [
            'Monday', 'Tuesday', 'Wednesday', 'Thursday',
            'Friday', 'Saturday', 'Sunday'
        ]
        schedule_names = [
            'Chủ Nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư',
            'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'
        ]
        
        cls._cache['schedule_day'] = schedule_day
        cls._cache['weekday'] = weekday
        cls._cache['date'] = today
        cls._last_update_date = today
        
        # Detailed logging
        logger.info(
            f"✅ Cache refreshed: "
            f"date={today}, "
            f"weekday={weekday} ({weekday_names[weekday]}), "
            f"schedule_day={schedule_day} ({schedule_names[schedule_day]}), "
            f"timezone=UTC"
        )
        
        # Log conversion formula
        logger.debug(
            f"📐 Conversion: Python weekday {weekday} "
            f"→ (weekday + 1) % 7 "
            f"→ SCHEDULE day {schedule_day}"
        )
    
    @classmethod
    def get_cache_info(cls) -> dict:
        """Lấy thông tin cache để debug với stats"""
        total_requests = cls._cache_hits + cls._cache_misses
        hit_rate = (
            cls._cache_hits / total_requests * 100
            if total_requests > 0 else 0
        )
        
        info = {
            'last_update': cls._last_update_date,
            'cached_data': cls._cache.copy(),
            'is_valid': cls._last_update_date == datetime.now().date(),
            'stats': {
                'cache_hits': cls._cache_hits,
                'cache_misses': cls._cache_misses,
                'total_requests': total_requests,
                'hit_rate': hit_rate
            }
        }
        
        logger.debug(f"📊 Cache info requested: {info}")
        return info
    
    @classmethod
    def clear_cache(cls):
        """Xóa cache (dùng cho testing) với logging"""
        old_cache = cls._cache.copy()
        old_stats = {
            'hits': cls._cache_hits,
            'misses': cls._cache_misses
        }
        
        cls._cache.clear()
        cls._last_update_date = None
        cls._cache_hits = 0
        cls._cache_misses = 0
        
        logger.warning(
            f"🗑️ Cache cleared: "
            f"Previous data={old_cache}, "
            f"Previous stats={old_stats}"
        )


# Hàm helper đơn giản để sử dụng
def get_cached_schedule_day() -> int:
    """
    Lấy schedule_day đã được cache
    
    Returns:
        int: Schedule day (0-6)
    """
    return ScheduleCache.get_schedule_day()
