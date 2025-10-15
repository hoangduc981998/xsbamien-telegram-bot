# app/handlers/admin.py (nếu có)
from app.utils.cache import ScheduleCache


def show_cache_status():
    """Hiển thị status của cache"""
    info = ScheduleCache.get_cache_info()

    message = f"""
📊 **Cache Status**

🗓️ Last Update: {info['last_update']}
📅 Schedule Day: {info['cached_data'].get('schedule_day')}
📆 Weekday: {info['cached_data'].get('weekday')}
✅ Valid: {info['is_valid']}
    """

    return message
