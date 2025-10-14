"""Unit tests for cache module - schedule_day optimization"""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock

from app.utils.cache import ScheduleCache, get_cached_schedule_day


class TestScheduleCache:
    """Test ScheduleCache class functionality"""

    def setup_method(self):
        """Clear cache before each test"""
        ScheduleCache.clear_cache()

    @pytest.mark.parametrize("python_weekday,expected_schedule_day", [
        (0, 1),  # Monday → schedule day 1
        (1, 2),  # Tuesday → schedule day 2
        (2, 3),  # Wednesday → schedule day 3
        (3, 4),  # Thursday → schedule day 4
        (4, 5),  # Friday → schedule day 5
        (5, 6),  # Saturday → schedule day 6
        (6, 0),  # Sunday → schedule day 0
    ])
    def test_cache_returns_correct_schedule_day(self, python_weekday, expected_schedule_day):
        """Test cache returns correct schedule_day for all 7 days"""
        with patch('app.utils.cache.datetime') as mock_dt:
            # Mock both date() and now() calls
            mock_today = date(2025, 10, 14)  # A Tuesday
            mock_now = MagicMock()
            mock_now.weekday.return_value = python_weekday
            mock_now.date.return_value = mock_today

            mock_dt.now.return_value = mock_now

            # Call function
            result = ScheduleCache.get_schedule_day()

            # Verify result
            assert result == expected_schedule_day, \
                f"Python weekday {python_weekday} should convert to schedule_day {expected_schedule_day}, got {result}"

    def test_cache_reuses_value_on_same_day(self):
        """Test cache reuses value when called multiple times on the same day"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_today = date(2025, 10, 14)  # Tuesday
            mock_now = MagicMock()
            mock_now.weekday.return_value = 1  # Tuesday
            mock_now.date.return_value = mock_today

            mock_dt.now.return_value = mock_now

            # Call twice
            result1 = ScheduleCache.get_schedule_day()
            result2 = ScheduleCache.get_schedule_day()

            # Both should return same value
            assert result1 == result2 == 2, "Cache should return same value on same day"

            # datetime.now() should be called for both calls (2 for date check, 1 for weekday)
            # But the important thing is the result is the same
            assert mock_dt.now.call_count >= 2, "datetime.now() should be called at least twice"

    def test_cache_refreshes_on_new_day(self):
        """Test cache automatically refreshes when a new day begins"""
        with patch('app.utils.cache.datetime') as mock_dt:
            # First call - Tuesday
            mock_tuesday = date(2025, 10, 14)
            mock_now_tue = MagicMock()
            mock_now_tue.weekday.return_value = 1  # Tuesday
            mock_now_tue.date.return_value = mock_tuesday

            mock_dt.now.return_value = mock_now_tue

            result1 = ScheduleCache.get_schedule_day()
            assert result1 == 2, "Tuesday should be schedule_day 2"

            # Second call - Wednesday (new day)
            mock_wednesday = date(2025, 10, 15)
            mock_now_wed = MagicMock()
            mock_now_wed.weekday.return_value = 2  # Wednesday
            mock_now_wed.date.return_value = mock_wednesday

            mock_dt.now.return_value = mock_now_wed

            result2 = ScheduleCache.get_schedule_day()
            assert result2 == 3, "Wednesday should be schedule_day 3"

            # Verify cache was refreshed
            assert result1 != result2, "Cache should refresh with new day"

    def test_get_cache_info(self):
        """Test get_cache_info returns correct information"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_today = date(2025, 10, 14)  # Tuesday
            mock_now = MagicMock()
            mock_now.weekday.return_value = 1  # Tuesday
            mock_now.date.return_value = mock_today

            mock_dt.now.return_value = mock_now

            # Create cache
            ScheduleCache.get_schedule_day()

            # Get cache info
            info = ScheduleCache.get_cache_info()

            # Verify structure
            assert 'last_update' in info, "Cache info should contain last_update"
            assert 'cached_data' in info, "Cache info should contain cached_data"
            assert 'is_valid' in info, "Cache info should contain is_valid"

            # Verify content
            assert info['last_update'] == mock_today, "Last update should match today"
            assert info['cached_data']['schedule_day'] == 2, "Cached schedule_day should be 2"
            assert info['cached_data']['weekday'] == 1, "Cached weekday should be 1"
            assert info['cached_data']['date'] == mock_today, "Cached date should match"
            assert info['is_valid'] is True, "Cache should be valid"

    def test_clear_cache(self):
        """Test clear_cache properly clears all cache data"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_today = date(2025, 10, 14)
            mock_now = MagicMock()
            mock_now.weekday.return_value = 1
            mock_now.date.return_value = mock_today

            mock_dt.now.return_value = mock_now

            # Create cache
            ScheduleCache.get_schedule_day()

            # Verify cache exists
            assert ScheduleCache._cache != {}, "Cache should have data"
            assert ScheduleCache._last_update_date is not None, "Last update date should be set"

            # Clear cache
            ScheduleCache.clear_cache()

            # Verify cache is cleared
            assert ScheduleCache._cache == {}, "Cache should be empty"
            assert ScheduleCache._last_update_date is None, "Last update date should be None"

    def test_helper_function(self):
        """Test helper function get_cached_schedule_day works correctly"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_today = date(2025, 10, 14)  # Tuesday
            mock_now = MagicMock()
            mock_now.weekday.return_value = 1  # Tuesday
            mock_now.date.return_value = mock_today

            mock_dt.now.return_value = mock_now

            # Call helper function
            result = get_cached_schedule_day()

            # Verify result
            assert result == 2, "Helper function should return correct schedule_day"


class TestCachePerformance:
    """Test cache performance and efficiency"""

    def setup_method(self):
        """Clear cache before each test"""
        ScheduleCache.clear_cache()

    def test_multiple_calls_use_cache(self):
        """Test that multiple calls reuse cached value (simulating 100 users)"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_today = date(2025, 10, 14)  # Tuesday
            mock_now = MagicMock()
            mock_now.weekday.return_value = 1  # Tuesday
            mock_now.date.return_value = mock_today

            mock_dt.now.return_value = mock_now

            # Simulate 100 user requests
            results = []
            for _ in range(100):
                results.append(ScheduleCache.get_schedule_day())

            # Verify all results are the same
            assert all(r == 2 for r in results), "All calls should return same value"
            assert len(set(results)) == 1, "All results should be identical"

            # Verify weekday() was only called once (on first cache miss)
            # Note: datetime.now() is called for date checking on each call,
            # but weekday() is only called when cache is refreshed
            assert mock_now.weekday.call_count == 1, \
                "weekday() should only be called once (cache working)"
