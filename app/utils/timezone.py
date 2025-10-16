"""Timezone utilities for Vietnam (UTC+7)"""

from datetime import datetime, date, timezone, timedelta

# Vietnam timezone (UTC+7)
VIETNAM_TZ = timezone(timedelta(hours=7))


def get_vietnam_now() -> datetime:
    """Get current datetime in Vietnam timezone (UTC+7)"""
    return datetime.now(VIETNAM_TZ)


def get_vietnam_today() -> date:
    """Get current date in Vietnam timezone (UTC+7)"""
    return get_vietnam_now().date()


def get_vietnam_time_str() -> str:
    """Get current time string in Vietnam timezone"""
    return get_vietnam_now().strftime("%Y-%m-%d %H:%M:%S")


def to_vietnam_date(dt: datetime) -> date:
    """Convert datetime to Vietnam date"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(VIETNAM_TZ).date()
