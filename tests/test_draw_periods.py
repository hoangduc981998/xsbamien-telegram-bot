"""Test draw periods calculation for lottery provinces"""

import pytest
from datetime import date, timedelta
from app.utils.lottery_helpers import (
    count_draw_periods,
    is_daily_draw_province,
    categorize_gan
)


class TestCountDrawPeriods:
    """Test count_draw_periods function"""
    
    def test_angi_thursday_only(self):
        """Test An Giang (draws on Thursday only)"""
        # 28/08/2025 is Thursday, 16/10/2025 is Thursday
        # Thursdays: 04/09, 11/09, 18/09, 25/09, 02/10, 09/10, 16/10 = 7 draws
        start = date(2025, 8, 28)
        end = date(2025, 10, 16)
        
        count = count_draw_periods('ANGI', start, end)
        assert count == 7
    
    def test_tphcm_monday_saturday(self):
        """Test TPHCM (draws on Monday and Saturday)"""
        # One week: Monday (1 draw) + Saturday (1 draw) = 2 draws
        start = date(2025, 10, 6)  # Monday
        end = date(2025, 10, 13)    # Monday
        
        # Should count: 11 Oct (Sat), 13 Oct (Mon) = 2 draws
        count = count_draw_periods('TPHCM', start, end, exclude_start=True)
        assert count == 2
    
    def test_mb_daily(self):
        """Test Miền Bắc (draws daily)"""
        start = date(2025, 10, 1)
        end = date(2025, 10, 7)
        
        # 7 days = 6 draws (excluding start)
        count = count_draw_periods('MB', start, end, exclude_start=True)
        assert count == 6
    
    def test_exclude_start_and_end(self):
        """Test excluding both start and end dates"""
        # ANGI: Thursday only
        start = date(2025, 10, 2)   # Thursday
        end = date(2025, 10, 9)     # Thursday
        
        # With exclude_start=True, exclude_end=True: no draws
        count = count_draw_periods('ANGI', start, end, exclude_start=True, exclude_end=True)
        assert count == 0
    
    def test_single_day_window(self):
        """Test single day window"""
        start = date(2025, 10, 2)  # Thursday
        end = date(2025, 10, 2)    # Same Thursday
        
        # ANGI draws on Thursday, but exclude_start=True means 0
        count = count_draw_periods('ANGI', start, end, exclude_start=True)
        assert count == 0
        
        # With exclude_start=False, should count 1
        count = count_draw_periods('ANGI', start, end, exclude_start=False)
        assert count == 1
    
    def test_unknown_province_defaults_daily(self):
        """Test unknown province defaults to daily draws"""
        start = date(2025, 10, 1)
        end = date(2025, 10, 7)
        
        count = count_draw_periods('UNKNOWN', start, end, exclude_start=True)
        assert count == 6  # 6 days (every day)
    
    def test_bali_wednesday_saturday(self):
        """Test Bạc Liêu (draws on Wednesday and Saturday)"""
        # Week starting Monday Oct 6, 2025
        start = date(2025, 10, 6)  # Monday
        end = date(2025, 10, 12)   # Sunday
        
        # Should count: Wed (8th) and Sat (11th) = 2 draws
        count = count_draw_periods('BALI', start, end, exclude_start=True)
        assert count == 2


class TestIsDailyDrawProvince:
    """Test is_daily_draw_province function"""
    
    def test_mb_is_daily(self):
        """Test MB is recognized as daily"""
        assert is_daily_draw_province('MB') is True
    
    def test_angi_is_not_daily(self):
        """Test ANGI is not daily"""
        assert is_daily_draw_province('ANGI') is False
    
    def test_tphcm_is_not_daily(self):
        """Test TPHCM is not daily"""
        assert is_daily_draw_province('TPHCM') is False
    
    def test_unknown_province_is_not_daily(self):
        """Test unknown province is not daily"""
        assert is_daily_draw_province('UNKNOWN') is False


class TestCategorizeGan:
    """Test categorize_gan function"""
    
    def test_daily_categories(self):
        """Test categorization for daily draws (MB)"""
        assert categorize_gan(25, is_daily=True) == "cuc_gan"
        assert categorize_gan(21, is_daily=True) == "cuc_gan"
        assert categorize_gan(20, is_daily=True) == "gan_lon"
        assert categorize_gan(16, is_daily=True) == "gan_lon"
        assert categorize_gan(15, is_daily=True) == "gan_thuong"
        assert categorize_gan(10, is_daily=True) == "gan_thuong"
    
    def test_periodic_categories(self):
        """Test categorization for periodic draws (MN/MT)"""
        assert categorize_gan(10, is_daily=False) == "cuc_gan"
        assert categorize_gan(9, is_daily=False) == "cuc_gan"
        assert categorize_gan(8, is_daily=False) == "gan_lon"
        assert categorize_gan(6, is_daily=False) == "gan_lon"
        assert categorize_gan(5, is_daily=False) == "gan_thuong"
        assert categorize_gan(3, is_daily=False) == "gan_thuong"


class TestRealWorldScenarios:
    """Test real-world scenarios from the problem statement"""
    
    def test_angi_example_from_issue(self):
        """Test the exact example from the issue"""
        # Last appeared: 28/08/2025 (Thursday)
        # Today: 16/10/2025 (Thursday)
        # Should show: 7 draws gan
        
        last_appeared = date(2025, 8, 28)
        today = date(2025, 10, 16)
        
        # Count periods (excluding the day it last appeared)
        periods = count_draw_periods('ANGI', last_appeared, today, exclude_start=True)
        
        # Should be 7 Thursdays between these dates
        assert periods == 7
        
        # Days would be 48 (incorrect metric)
        days = (today - last_appeared).days - 1
        assert days == 48
        
        # Verify we're using the right metric
        assert periods != days
        assert periods < days
    
    def test_tphcm_two_draws_per_week(self):
        """Test TPHCM with 2 draws per week"""
        # TPHCM draws Monday and Saturday
        # One month should have ~8-9 draws
        start = date(2025, 9, 1)
        end = date(2025, 9, 30)
        
        count = count_draw_periods('TPHCM', start, end, exclude_start=True)
        
        # September 2025 has 4 Mondays and 4 Saturdays = 8 draws
        # (might be 9 depending on which day Sept 1 falls on)
        assert 8 <= count <= 9
    
    def test_mb_no_change(self):
        """Test MB continues working with days (no change)"""
        # MB draws daily, so periods = days
        start = date(2025, 10, 1)
        end = date(2025, 10, 10)
        
        periods = count_draw_periods('MB', start, end, exclude_start=True)
        days = (end - start).days
        
        # For MB, periods should equal days (excluding start)
        assert periods == days


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_same_day_start_end(self):
        """Test when start and end are the same day"""
        same_day = date(2025, 10, 2)  # Thursday
        
        # ANGI draws on Thursday
        count = count_draw_periods('ANGI', same_day, same_day, exclude_start=False)
        assert count == 1
        
        count = count_draw_periods('ANGI', same_day, same_day, exclude_start=True)
        assert count == 0
    
    def test_no_draws_in_period(self):
        """Test period with no draws"""
        # ANGI draws on Thursday only
        # Monday to Wednesday = no draws
        start = date(2025, 10, 6)  # Monday
        end = date(2025, 10, 8)    # Wednesday
        
        count = count_draw_periods('ANGI', start, end)
        assert count == 0
    
    def test_leap_year_february(self):
        """Test handling of leap year"""
        # 2024 is a leap year
        start = date(2024, 2, 1)
        end = date(2024, 2, 29)
        
        count = count_draw_periods('MB', start, end, exclude_start=True)
        assert count == 28  # 28 days (29 - 1)
    
    def test_year_boundary(self):
        """Test crossing year boundary"""
        start = date(2024, 12, 28)  # Saturday
        end = date(2025, 1, 4)      # Saturday
        
        # LOAN draws on Saturday
        count = count_draw_periods('LOAN', start, end, exclude_start=True)
        assert count == 1  # Only Jan 4


class TestDrawScheduleAccuracy:
    """Verify draw schedules match actual lottery schedules"""
    
    def test_province_schedules_exist(self):
        """Test that all major provinces have schedules defined"""
        from app.constants.draw_schedules import PROVINCE_DRAW_SCHEDULE
        
        # Check major provinces
        major_provinces = ['MB', 'ANGI', 'TPHCM', 'DANA', 'KHHO']
        for province in major_provinces:
            assert province in PROVINCE_DRAW_SCHEDULE
            assert len(PROVINCE_DRAW_SCHEDULE[province]) > 0
    
    def test_weekday_values_valid(self):
        """Test that all weekday values are valid (0-6)"""
        from app.constants.draw_schedules import PROVINCE_DRAW_SCHEDULE
        
        for province, days in PROVINCE_DRAW_SCHEDULE.items():
            for day in days:
                assert 0 <= day <= 6, f"Invalid weekday {day} for {province}"
    
    def test_mb_draws_all_days(self):
        """Test that MB draws every day"""
        from app.constants.draw_schedules import PROVINCE_DRAW_SCHEDULE
        
        assert PROVINCE_DRAW_SCHEDULE['MB'] == [0, 1, 2, 3, 4, 5, 6]
