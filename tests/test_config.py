"""Unit tests for configuration"""

import pytest
from app.config import PROVINCES, SCHEDULE, DRAW_TIMES


class TestProvinces:
    """Test PROVINCES configuration"""

    def test_provinces_not_empty(self):
        """Test that PROVINCES dict is not empty"""
        assert len(PROVINCES) > 0

    def test_provinces_has_mb(self):
        """Test that MB province exists"""
        assert "MB" in PROVINCES
        assert PROVINCES["MB"]["region"] == "MB"

    def test_provinces_has_mn_provinces(self):
        """Test that MN provinces exist"""
        mn_provinces = [p for p in PROVINCES.values() if p["region"] == "MN"]
        assert len(mn_provinces) > 0

    def test_provinces_has_mt_provinces(self):
        """Test that MT provinces exist"""
        mt_provinces = [p for p in PROVINCES.values() if p["region"] == "MT"]
        assert len(mt_provinces) > 0

    def test_province_structure(self):
        """Test that each province has required fields"""
        for code, province in PROVINCES.items():
            assert "name" in province
            assert "code" in province
            assert "region" in province
            assert "emoji" in province

    def test_province_regions_valid(self):
        """Test that all provinces have valid regions"""
        valid_regions = ["MB", "MN", "MT"]
        for province in PROVINCES.values():
            assert province["region"] in valid_regions


class TestSchedule:
    """Test SCHEDULE configuration"""

    def test_schedule_has_all_regions(self):
        """Test that schedule has MB, MN, MT"""
        assert "MB" in SCHEDULE
        assert "MN" in SCHEDULE
        assert "MT" in SCHEDULE

    def test_schedule_has_all_days(self):
        """Test that each region has all 7 days"""
        for region in ["MB", "MN", "MT"]:
            assert len(SCHEDULE[region]) == 7
            for day in range(7):
                assert day in SCHEDULE[region]

    def test_schedule_mb_daily(self):
        """Test that MB has entries every day"""
        for day in range(7):
            assert "MB" in SCHEDULE["MB"][day]

    def test_schedule_provinces_exist(self):
        """Test that all scheduled provinces exist in PROVINCES"""
        for region in SCHEDULE.values():
            for day_provinces in region.values():
                for province_code in day_provinces:
                    assert province_code in PROVINCES


class TestDrawTimes:
    """Test DRAW_TIMES configuration"""

    def test_draw_times_has_all_regions(self):
        """Test that draw times exist for all regions"""
        assert "MB" in DRAW_TIMES
        assert "MN" in DRAW_TIMES
        assert "MT" in DRAW_TIMES

    def test_draw_times_have_start_end(self):
        """Test that each region has start and end times"""
        for region in DRAW_TIMES.values():
            assert "start" in region
            assert "end" in region

    def test_draw_times_format(self):
        """Test that draw times are in HH:MM format"""
        for region in DRAW_TIMES.values():
            # Basic check for format
            start = region["start"]
            end = region["end"]
            assert ":" in start
            assert ":" in end
            assert len(start.split(":")) == 2
            assert len(end.split(":")) == 2

    def test_draw_times_order(self):
        """Test that MN draws first, then MT, then MB"""
        # Convert to minutes for comparison
        def to_minutes(time_str):
            h, m = map(int, time_str.split(":"))
            return h * 60 + m

        mn_start = to_minutes(DRAW_TIMES["MN"]["start"])
        mt_start = to_minutes(DRAW_TIMES["MT"]["start"])
        mb_start = to_minutes(DRAW_TIMES["MB"]["start"])

        # MN should start before MT, MT before MB
        assert mn_start < mt_start < mb_start
