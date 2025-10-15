
"""Unit tests for keyboard generation functions"""

import pytest
from unittest.mock import patch
from datetime import date

from app.ui.keyboards import (
    get_schedule_today_keyboard,
    get_today_schedule_actions,
)
from app.config import PROVINCES, SCHEDULE
from app.utils.cache import ScheduleCache


class TestGetScheduleTodayKeyboard:
    """Test get_schedule_today_keyboard() function"""

    def setup_method(self):
        """Clear cache before each test"""
        ScheduleCache.clear_cache()

    @pytest.mark.parametrize("python_weekday,schedule_day", [
        (0, 1),  # Monday → schedule day 1 (Thứ 2)
        (1, 2),  # Tuesday → schedule day 2 (Thứ 3)
        (2, 3),  # Wednesday → schedule day 3 (Thứ 4)
        (3, 4),  # Thursday → schedule day 4 (Thứ 5)
        (4, 5),  # Friday → schedule day 5 (Thứ 6)
        (5, 6),  # Saturday → schedule day 6 (Thứ 7)
        (6, 0),  # Sunday → schedule day 0 (Chủ nhật)
    ])
    def test_weekday_conversion(self, python_weekday, schedule_day):
        """Test Python weekday converts correctly to SCHEDULE format"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = python_weekday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            # Get expected provinces for this schedule day
            expected_provinces = []
            for region in ["MB", "MT", "MN"]:
                expected_provinces.extend(SCHEDULE[region].get(schedule_day, []))

            # Call function
            keyboard = get_schedule_today_keyboard()

            # Extract province codes from buttons
            actual_provinces = []
            for row in keyboard.inline_keyboard[:-1]:  # Exclude last row (Back button)
                for button in row:
                    if button.callback_data.startswith("province_"):
                        actual_provinces.append(button.callback_data.replace("province_", ""))

            # Verify
            error_msg = (f"Weekday {python_weekday} → Schedule day {schedule_day}: "
                         f"Expected {expected_provinces}, got {actual_provinces}")
            assert actual_provinces == expected_provinces, error_msg

    def test_all_provinces_shown_no_limit(self):
        """Test that all provinces are shown (not limited to [:2])"""
        with patch('app.utils.cache.datetime') as mock_dt:
            # Tuesday has 6 provinces (1 MB + 2 MT + 3 MN)
            mock_dt.now.return_value.weekday.return_value = 1  # Tuesday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            # Count province buttons
            province_count = 0
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("province_"):
                        province_count += 1

            assert province_count == 6, f"Expected 6 provinces on Tuesday, got {province_count}"

    def test_two_column_layout(self):
        """Test buttons are arranged in 2-column layout"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 1  # Tuesday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            # Check each row (except last) has at most 2 buttons
            for row in keyboard.inline_keyboard[:-1]:
                assert len(row) <= 2, f"Row has {len(row)} buttons, expected ≤ 2"

    def test_back_button_present(self):
        """Test 'Quay Lại' button is present"""
        keyboard = get_schedule_today_keyboard()

        last_row = keyboard.inline_keyboard[-1]
        assert len(last_row) == 1
        assert last_row[0].text == "◀️ Quay Lại"
        assert last_row[0].callback_data == "main_menu"

    def test_button_display_name_truncation(self):
        """Test long province names are truncated"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday (has TP.HCM)
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            # Find TP.HCM button
            tphcm_button = None
            for row in keyboard.inline_keyboard:
                for button in row:
                    if button.callback_data == "province_TPHCM":
                        tphcm_button = button
                        break

            assert tphcm_button is not None
            # Check that long name is truncated (name is 16 chars, should be truncated to 9+...)
            assert len(tphcm_button.text) <= 15  # Emoji + truncated name

    def test_button_callback_data_format(self):
        """Test button callback data format is correct"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            # Check all province buttons have correct callback format
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("province_"):
                        # Extract province code
                        province_code = button.callback_data.replace("province_", "")
                        # Verify it exists in PROVINCES
                        assert province_code in PROVINCES, \
                            f"Province code {province_code} not found in PROVINCES"

    def test_provinces_grouped_by_region_order(self):
        """Test provinces appear in correct order: MB → MT → MN"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            # Extract all province codes
            province_codes = []
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("province_"):
                        province_codes.append(button.callback_data.replace("province_", ""))

            # Check they appear in MB, MT, MN order
            regions = [PROVINCES[code]["region"] for code in province_codes]

            # MB should come first
            if "MB" in regions:
                mb_indices = [i for i, r in enumerate(regions) if r == "MB"]
                mt_indices = [i for i, r in enumerate(regions) if r == "MT"]
                mn_indices = [i for i, r in enumerate(regions) if r == "MN"]

                # All MB should come before MT and MN
                if mt_indices:
                    assert max(mb_indices) < min(mt_indices), "MB should come before MT"
                if mn_indices:
                    assert max(mb_indices) < min(mn_indices), "MB should come before MN"

                # All MT should come before MN
                if mt_indices and mn_indices:
                    assert max(mt_indices) < min(mn_indices), "MT should come before MN"


class TestGetTodayScheduleActions:
    """Test get_today_schedule_actions() function"""

    def setup_method(self):
        """Clear cache before each test"""
        ScheduleCache.clear_cache()

    @pytest.mark.parametrize("python_weekday,schedule_day", [
        (0, 1),  # Monday → schedule day 1
        (1, 2),  # Tuesday → schedule day 2
        (2, 3),  # Wednesday → schedule day 3
        (3, 4),  # Thursday → schedule day 4
        (4, 5),  # Friday → schedule day 5
        (5, 6),  # Saturday → schedule day 6
        (6, 0),  # Sunday → schedule day 0
    ])
    def test_weekday_conversion(self, python_weekday, schedule_day):
        """Test Python weekday converts correctly to SCHEDULE format"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = python_weekday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            # Get expected provinces for this schedule day
            expected_provinces = []
            for region in ["MB", "MT", "MN"]:
                expected_provinces.extend(SCHEDULE[region].get(schedule_day, []))

            # Call function
            keyboard = get_today_schedule_actions()

            # Extract province codes from buttons (excluding last row with navigation buttons)
            actual_provinces = []
            for row in keyboard.inline_keyboard[:-1]:  # Exclude last row
                for button in row:
                    if button.callback_data.startswith("province_"):
                        actual_provinces.append(button.callback_data.replace("province_", ""))

            # Verify
            error_msg = (f"Weekday {python_weekday} → Schedule day {schedule_day}: "
                         f"Expected {expected_provinces}, got {actual_provinces}")
            assert actual_provinces == expected_provinces, error_msg

    def test_navigation_buttons_present(self):
        """Test navigation buttons are at the end"""
        keyboard = get_today_schedule_actions()

        last_row = keyboard.inline_keyboard[-1]
        assert len(last_row) == 2
        assert last_row[0].text == "📅 Xem Lịch Cả Tuần"
        assert last_row[0].callback_data == "schedule_week"
        assert last_row[1].text == "◀️ Quay Lại"
        assert last_row[1].callback_data == "main_menu"

    def test_all_provinces_shown_no_limit(self):
        """Test that all provinces are shown (not limited to [:2])"""
        with patch('app.utils.cache.datetime') as mock_dt:
            # Tuesday has 6 provinces
            mock_dt.now.return_value.weekday.return_value = 1  # Tuesday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Count province buttons (excluding navigation buttons in last row)
            province_count = 0
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("province_"):
                        province_count += 1

            assert province_count == 6, f"Expected 6 provinces on Tuesday, got {province_count}"

    def test_two_column_layout(self):
        """Test buttons are arranged in 2-column layout"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 1  # Tuesday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Check each row (except last navigation row) has at most 2 buttons
            for row in keyboard.inline_keyboard[:-1]:
                assert len(row) <= 2, f"Row has {len(row)} buttons, expected ≤ 2"

    def test_button_display_name_truncation(self):
        """Test long province names are truncated"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday (has TP.HCM)
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Find TP.HCM button
            tphcm_button = None
            for row in keyboard.inline_keyboard:
                for button in row:
                    if button.callback_data == "province_TPHCM":
                        tphcm_button = button
                        break

            assert tphcm_button is not None
            assert len(tphcm_button.text) <= 15  # Emoji + truncated name

    def test_button_callback_data_format(self):
        """Test button callback data format is correct"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Check all province buttons have correct callback format
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("province_"):
                        province_code = button.callback_data.replace("province_", "")
                        assert province_code in PROVINCES, \
                            f"Province code {province_code} not found in PROVINCES"

    def test_provinces_before_navigation_buttons(self):
        """Test province buttons come before navigation buttons"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Last row should be navigation buttons
            last_row = keyboard.inline_keyboard[-1]
            for button in last_row:
                assert not button.callback_data.startswith("province_"), \
                    "Navigation row should not contain province buttons"

            # All other rows should contain province buttons (if any buttons exist)
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    assert button.callback_data.startswith("province_"), \
                        "Province rows should only contain province buttons"

    def test_provinces_grouped_by_region_order(self):
        """Test provinces appear in correct order: MB → MT → MN"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Extract all province codes
            province_codes = []
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("province_"):
                        province_codes.append(button.callback_data.replace("province_", ""))

            # Check they appear in MB, MT, MN order
            regions = [PROVINCES[code]["region"] for code in province_codes]

            # MB should come first
            if "MB" in regions:
                mb_indices = [i for i, r in enumerate(regions) if r == "MB"]
                mt_indices = [i for i, r in enumerate(regions) if r == "MT"]
                mn_indices = [i for i, r in enumerate(regions) if r == "MN"]

                # All MB should come before MT and MN
                if mt_indices:
                    assert max(mb_indices) < min(mt_indices), "MB should come before MT"
                if mn_indices:
                    assert max(mb_indices) < min(mn_indices), "MB should come before MN"

                # All MT should come before MN
                if mt_indices and mn_indices:
                    assert max(mt_indices) < min(mn_indices), "MT should come before MN"

    def test_thursday_has_7_provinces(self):
        """Test Thursday has 7 provinces (edge case with most provinces)"""
        with patch('app.utils.cache.datetime') as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 3  # Thursday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Count province buttons
            province_count = 0
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("province_"):
                        province_count += 1

            # Thursday should have 7 provinces: MB + BIDI/QUBI/QUTR + TANI/ANGI/BITH
            assert province_count == 7, f"Expected 7 provinces on Thursday, got {province_count}"
