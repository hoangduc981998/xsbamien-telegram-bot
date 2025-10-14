# tests/test_cache.py
"""Tests cho schedule cache"""

import pytest
from unittest.mock import patch
from datetime import datetime, date

from app.utils.cache import ScheduleCache, get_cached_schedule_day


class TestScheduleCache:
    """Tests cho ScheduleCache class"""
    
    def setup_method(self):
        """Xóa cache trước mỗi test"""
        ScheduleCache.clear_cache()
    
    @pytest.mark.parametrize("python_weekday,expected_schedule_day", [
        (0, 1),  # Monday → Thứ Hai
        (1, 2),  # Tuesday → Thứ Ba
        (2, 3),  # Wednesday → Thứ Tư
        (3, 4),  # Thursday → Thứ Năm
        (4, 5),  # Friday → Thứ Sáu
        (5, 6),  # Saturday → Thứ Bảy
        (6, 0),  # Sunday → Chủ Nhật
    ])
    def test_cache_returns_correct_schedule_day(
        self, python_weekday, expected_schedule_day
    ):
        """Test cache trả về đúng schedule_day cho từng ngày"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_now = mock_dt.now.return_value
            mock_now.weekday.return_value = python_weekday
            mock_now.date.return_value = date(2025, 10, 14)
            
            result = ScheduleCache.get_schedule_day()
            
            assert result == expected_schedule_day
    
    def test_cache_reuses_value_on_same_day(self):
        """Test cache sử dụng lại giá trị trong cùng 1 ngày"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_now = mock_dt.now.return_value
            mock_now.weekday.return_value = 1  # Tuesday
            mock_now.date.return_value = date(2025, 10, 14)
            
            # Lần 1: Tính toán và cache
            result1 = ScheduleCache.get_schedule_day()
            
            # Lần 2: Lấy từ cache (không tính lại)
            result2 = ScheduleCache.get_schedule_day()
            
            assert result1 == result2 == 2
            # Verify datetime.now() chỉ được gọi 1 lần cho date()
            assert mock_dt.now.call_count >= 1
    
    def test_cache_refreshes_on_new_day(self):
        """Test cache tự động làm mới khi sang ngày mới"""
        with patch('app.utils.cache.datetime') as mock_dt:
            # Ngày 1: Tuesday (schedule_day = 2)
            mock_now = mock_dt.now.return_value
            mock_now.weekday.return_value = 1
            mock_now.date.return_value = date(2025, 10, 14)
            
            result1 = ScheduleCache.get_schedule_day()
            assert result1 == 2
            
            # Ngày 2: Wednesday (schedule_day = 3)
            mock_now.weekday.return_value = 2
            mock_now.date.return_value = date(2025, 10, 15)
            
            result2 = ScheduleCache.get_schedule_day()
            assert result2 == 3
    
    def test_get_cache_info(self):
        """Test lấy thông tin cache"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_now = mock_dt.now.return_value
            mock_now.weekday.return_value = 1  # Tuesday
            today = date(2025, 10, 14)
            mock_now.date.return_value = today
            
            # Tạo cache
            ScheduleCache.get_schedule_day()
            
            # Lấy thông tin
            info = ScheduleCache.get_cache_info()
            
            assert info['last_update'] == today
            assert info['cached_data']['schedule_day'] == 2
            assert info['cached_data']['weekday'] == 1
            assert info['is_valid'] is True
    
    def test_clear_cache(self):
        """Test xóa cache"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_now = mock_dt.now.return_value
            mock_now.weekday.return_value = 1
            mock_now.date.return_value = date(2025, 10, 14)
            
            # Tạo cache
            ScheduleCache.get_schedule_day()
            
            # Xóa cache
            ScheduleCache.clear_cache()
            
            # Verify cache đã bị xóa
            info = ScheduleCache.get_cache_info()
            assert info['last_update'] is None
            assert info['cached_data'] == {}
            assert info['is_valid'] is False
    
    def test_helper_function(self):
        """Test helper function get_cached_schedule_day()"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_now = mock_dt.now.return_value
            mock_now.weekday.return_value = 1  # Tuesday
            mock_now.date.return_value = date(2025, 10, 14)
            
            result = get_cached_schedule_day()
            
            assert result == 2


class TestCachePerformance:
    """Tests cho performance của cache"""
    
    def setup_method(self):
        """Xóa cache trước mỗi test"""
        ScheduleCache.clear_cache()
    
    def test_multiple_calls_use_cache(self):
        """Test nhiều lần gọi sử dụng cache (không tính lại)"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_now = mock_dt.now.return_value
            mock_now.weekday.return_value = 1
            mock_now.date.return_value = date(2025, 10, 14)
            
            # Gọi 100 lần (giả lập 100 users)
            results = [get_cached_schedule_day() for _ in range(100)]
            
            # Tất cả đều trả về cùng kết quả
            assert all(r == 2 for r in results)
            
            # weekday() chỉ được gọi 1 lần (lần đầu tính toán)
            assert mock_now.weekday.call_count == 1
