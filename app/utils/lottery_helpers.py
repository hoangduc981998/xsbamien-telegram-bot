"""Helper functions for lottery calculations"""

from datetime import date, timedelta
from app.constants.draw_schedules import PROVINCE_DRAW_SCHEDULE


def count_draw_periods(
    province_code: str,
    start_date: date,
    end_date: date,
    exclude_start: bool = True,
    exclude_end: bool = False
) -> int:
    """
    Count number of draw periods for a province between two dates.

    Args:
        province_code: Province code (e.g., 'ANGI', 'MB')
        start_date: Start date
        end_date: End date
        exclude_start: Don't count start_date even if it's a draw day (default: True)
        exclude_end: Don't count end_date even if it's a draw day (default: False)

    Returns:
        Number of draw periods

    Examples:
        >>> # An Giang draws on Thursday (weekday 3)
        >>> count_draw_periods('ANGI', date(2025, 8, 28), date(2025, 10, 16))
        7  # 7 Thursdays between these dates
    """
    # Get draw schedule for province, default to daily if not found
    schedule = PROVINCE_DRAW_SCHEDULE.get(province_code, [0, 1, 2, 3, 4, 5, 6])

    count = 0
    current = start_date + timedelta(days=1) if exclude_start else start_date

    while current <= end_date:
        if exclude_end and current == end_date:
            break

        if current.weekday() in schedule:
            count += 1

        current += timedelta(days=1)

    return count


def is_daily_draw_province(province_code: str) -> bool:
    """
    Check if province draws daily (Miền Bắc).

    Args:
        province_code: Province code

    Returns:
        True if province draws daily, False otherwise
    """
    return province_code in ['MB']


def categorize_gan(value: int, is_daily: bool) -> str:
    """
    Categorize gan level based on value and draw frequency.

    Args:
        value: Days or periods since last appearance
        is_daily: Whether the province draws daily

    Returns:
        Category string: "cuc_gan", "gan_lon", or "gan_thuong"
    """
    if is_daily:
        # Days threshold (MB)
        if value >= 21:
            return "cuc_gan"
        elif value >= 16:
            return "gan_lon"
        else:
            return "gan_thuong"
    else:
        # Periods threshold (MN/MT)
        if value >= 9:
            return "cuc_gan"
        elif value >= 6:
            return "gan_lon"
        else:
            return "gan_thuong"
