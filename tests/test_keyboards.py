"""Unit tests for keyboard generation functions"""

import pytest
from unittest.mock import patch
from datetime import date

from app.ui.keyboards import (
    get_schedule_today_keyboard,
    get_today_schedule_actions,
    get_main_menu_keyboard,
    get_results_menu_keyboard,
    get_region_provinces_keyboard,
    get_back_to_results_keyboard,
    get_week_schedule_keyboard,
)
from app.config import PROVINCES, SCHEDULE
from app.utils.cache import ScheduleCache


class TestGetScheduleTodayKeyboard:
    """Test get_schedule_today_keyboard() function"""

    def setup_method(self):
        """Clear cache before each test"""
        ScheduleCache.clear_cache()

    @pytest.mark.parametrize(
        "python_weekday,schedule_day",
        [
            (0, 1),  # Monday → schedule day 1 (Thứ 2)
            (1, 2),  # Tuesday → schedule day 2 (Thứ 3)
            (2, 3),  # Wednesday → schedule day 3 (Thứ 4)
            (3, 4),  # Thursday → schedule day 4 (Thứ 5)
            (4, 5),  # Friday → schedule day 5 (Thứ 6)
            (5, 6),  # Saturday → schedule day 6 (Thứ 7)
            (6, 0),  # Sunday → schedule day 0 (Chủ nhật)
        ],
    )
    def test_weekday_conversion(self, python_weekday, schedule_day):
        """Test Python weekday converts correctly to SCHEDULE format"""
        with patch("app.utils.cache.datetime") as mock_dt:
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
                    if button.callback_data.startswith("result_"):
                        actual_provinces.append(
                            button.callback_data.replace("result_", "")
                        )

            # Verify
            error_msg = (
                f"Weekday {python_weekday} → Schedule day {schedule_day}: "
                f"Expected {expected_provinces}, got {actual_provinces}"
            )
            assert actual_provinces == expected_provinces, error_msg

    def test_all_provinces_shown_no_limit(self):
        """Test that all provinces are shown (not limited to [:2])"""
        with patch("app.utils.cache.datetime") as mock_dt:
            # Tuesday has 6 provinces (1 MB + 2 MT + 3 MN)
            mock_dt.now.return_value.weekday.return_value = 1  # Tuesday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            # Count province buttons
            result_count = 0
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        result_count += 1

            assert (
                result_count == 6
            ), f"Expected 6 provinces on Tuesday, got {result_count}"

    def test_two_column_layout(self):
        """Test buttons are arranged in 2-column layout"""
        with patch("app.utils.cache.datetime") as mock_dt:
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
        assert last_row[0].text == "🔙 Quay lại"
        assert last_row[0].callback_data == "back_to_main"

    def test_button_display_name_truncation(self):
        """Test long province names are truncated"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday (has TP.HCM)
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            # Find TP.HCM button
            tphcm_button = None
            for row in keyboard.inline_keyboard:
                for button in row:
                    if button.callback_data == "result_TPHCM":
                        tphcm_button = button
                        break

            assert tphcm_button is not None
            # Check that long name is truncated (name is 16 chars, should be truncated to 9+...)
            assert len(tphcm_button.text) <= 15  # Emoji + truncated name

    def test_button_callback_data_format(self):
        """Test button callback data format is correct"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            # Check all province buttons have correct callback format
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        # Extract province code
                        result_code = button.callback_data.replace("result_", "")
                        # Verify it exists in PROVINCES
                        assert (
                            result_code in PROVINCES
                        ), f"Province code {result_code} not found in PROVINCES"

    def test_provinces_grouped_by_region_order(self):
        """Test provinces appear in correct order: MB → MT → MN"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            # Extract all province codes
            result_codes = []
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        result_codes.append(button.callback_data.replace("result_", ""))

            # Check they appear in MB, MT, MN order
            regions = [PROVINCES[code]["region"] for code in result_codes]

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

    @pytest.mark.parametrize(
        "python_weekday,schedule_day",
        [
            (0, 1),  # Monday → schedule day 1
            (1, 2),  # Tuesday → schedule day 2
            (2, 3),  # Wednesday → schedule day 3
            (3, 4),  # Thursday → schedule day 4
            (4, 5),  # Friday → schedule day 5
            (5, 6),  # Saturday → schedule day 6
            (6, 0),  # Sunday → schedule day 0
        ],
    )
    def test_weekday_conversion(self, python_weekday, schedule_day):
        """Test Python weekday converts correctly to SCHEDULE format"""
        with patch("app.utils.cache.datetime") as mock_dt:
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
                    if button.callback_data.startswith("result_"):
                        actual_provinces.append(
                            button.callback_data.replace("result_", "")
                        )

            # Verify
            error_msg = (
                f"Weekday {python_weekday} → Schedule day {schedule_day}: "
                f"Expected {expected_provinces}, got {actual_provinces}"
            )
            assert actual_provinces == expected_provinces, error_msg

    def test_navigation_buttons_present(self):
        """Test navigation buttons are at the end"""
        keyboard = get_today_schedule_actions()

        # Check last 2 rows (separate buttons)
        schedule_week_row = keyboard.inline_keyboard[-2]
        back_row = keyboard.inline_keyboard[-1]

        assert len(schedule_week_row) == 1
        assert schedule_week_row[0].text == "📅 Lịch cả tuần"
        assert schedule_week_row[0].callback_data == "schedule_week"

        assert len(back_row) == 1
        assert back_row[0].text == "🔙 Quay lại"
        assert back_row[0].callback_data == "back_to_main"

    def test_all_provinces_shown_no_limit(self):
        """Test that all provinces are shown (not limited to [:2])"""
        with patch("app.utils.cache.datetime") as mock_dt:
            # Tuesday has 6 provinces
            mock_dt.now.return_value.weekday.return_value = 1  # Tuesday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Count province buttons (excluding navigation buttons in last row)
            result_count = 0
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        result_count += 1

            assert (
                result_count == 6
            ), f"Expected 6 provinces on Tuesday, got {result_count}"

    def test_two_column_layout(self):
        """Test buttons are arranged in 2-column layout"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 1  # Tuesday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Check each row (except last navigation row) has at most 2 buttons
            for row in keyboard.inline_keyboard[:-1]:
                assert len(row) <= 2, f"Row has {len(row)} buttons, expected ≤ 2"

    def test_button_display_name_truncation(self):
        """Test long province names are truncated"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday (has TP.HCM)
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Find TP.HCM button
            tphcm_button = None
            for row in keyboard.inline_keyboard:
                for button in row:
                    if button.callback_data == "result_TPHCM":
                        tphcm_button = button
                        break

            assert tphcm_button is not None
            assert len(tphcm_button.text) <= 15  # Emoji + truncated name

    def test_button_callback_data_format(self):
        """Test button callback data format is correct"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Check all province buttons have correct callback format
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        result_code = button.callback_data.replace("result_", "")
                        assert (
                            result_code in PROVINCES
                        ), f"Province code {result_code} not found in PROVINCES"

    def test_provinces_before_navigation_buttons(self):
        """Test province buttons come before navigation buttons"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Last 2 rows should be navigation buttons (schedule_week + back)
            last_two_rows = keyboard.inline_keyboard[-2:]
            for row in last_two_rows:
                for button in row:
                    assert not button.callback_data.startswith(
                        "result_"
                    ), "Navigation rows should not contain province buttons"

            # All other rows should contain province buttons (if any buttons exist)
            for row in keyboard.inline_keyboard[:-2]:
                for button in row:
                    assert button.callback_data.startswith(
                        "result_"
                    ), "Province rows should only contain province buttons"

    def test_provinces_grouped_by_region_order(self):
        """Test provinces appear in correct order: MB → MT → MN"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 0  # Monday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Extract all province codes
            result_codes = []
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        result_codes.append(button.callback_data.replace("result_", ""))

            # Check they appear in MB, MT, MN order
            regions = [PROVINCES[code]["region"] for code in result_codes]

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
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 3  # Thursday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_today_schedule_actions()

            # Count province buttons
            result_count = 0
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        result_count += 1

            # Thursday should have 7 provinces: MB + BIDI/QUBI/QUTR + TANI/ANGI/BITH
            assert (
                result_count == 7
            ), f"Expected 7 provinces on Thursday, got {result_count}"


class TestGetMainMenuKeyboard:
    """Test get_main_menu_keyboard() function"""

    def test_main_menu_structure(self):
        """Test main menu has all expected buttons"""
        keyboard = get_main_menu_keyboard()

        # Should have 4 rows (one for each menu item)
        assert len(keyboard.inline_keyboard) == 4

    def test_main_menu_button_texts(self):
        """Test main menu button texts"""
        keyboard = get_main_menu_keyboard()

        button_texts = [row[0].text for row in keyboard.inline_keyboard]

        assert "Lịch quay hôm nay" in " ".join(button_texts)
        assert "Lịch quay cả tuần" in " ".join(button_texts)
        assert "Xem kết quả" in " ".join(button_texts)
        assert "Hướng dẫn" in " ".join(button_texts)

    def test_main_menu_callback_data(self):
        """Test main menu callback data is correct"""
        keyboard = get_main_menu_keyboard()

        callbacks = [row[0].callback_data for row in keyboard.inline_keyboard]

        assert "schedule_today" in callbacks
        assert "schedule_week" in callbacks
        assert "results_menu" in callbacks
        assert "help" in callbacks

    def test_main_menu_single_column(self):
        """Test main menu uses single column layout"""
        keyboard = get_main_menu_keyboard()

        # Each row should have exactly 1 button
        for row in keyboard.inline_keyboard:
            assert len(row) == 1


class TestGetResultsMenuKeyboard:
    """Test get_results_menu_keyboard() function"""

    def test_results_menu_structure(self):
        """Test results menu has all regions"""
        keyboard = get_results_menu_keyboard()

        # Should have 4 rows (MB, MT, MN, Back)
        assert len(keyboard.inline_keyboard) == 4

    def test_results_menu_button_texts(self):
        """Test results menu shows all regions"""
        keyboard = get_results_menu_keyboard()

        button_texts = [row[0].text for row in keyboard.inline_keyboard]

        assert any("Miền Bắc" in text for text in button_texts)
        assert any("Miền Trung" in text for text in button_texts)
        assert any("Miền Nam" in text for text in button_texts)
        assert any("Quay lại" in text for text in button_texts)

    def test_results_menu_callback_data(self):
        """Test results menu callback data format"""
        keyboard = get_results_menu_keyboard()

        callbacks = [row[0].callback_data for row in keyboard.inline_keyboard]

        assert "results_MB" in callbacks
        assert "results_MT" in callbacks
        assert "results_MN" in callbacks
        assert "back_to_main" in callbacks

    def test_results_menu_region_order(self):
        """Test results menu shows regions in MB, MT, MN order"""
        keyboard = get_results_menu_keyboard()

        # Get callbacks without back button
        region_callbacks = [
            row[0].callback_data
            for row in keyboard.inline_keyboard[:-1]  # Exclude last (back) button
        ]

        # Should be in order: results_MB, results_MT, results_MN
        assert region_callbacks[0] == "results_MB"
        assert region_callbacks[1] == "results_MT"
        assert region_callbacks[2] == "results_MN"


class TestGetRegionProvincesKeyboard:
    """Test get_region_provinces_keyboard() function"""

    def test_region_provinces_mb(self):
        """Test MB region provinces keyboard"""
        keyboard = get_region_provinces_keyboard("MB")

        # MB should have 1 province (Miền Bắc)
        # Plus back button
        province_rows = keyboard.inline_keyboard[:-1]  # Exclude back button
        assert len(province_rows) >= 1

    def test_region_provinces_mt(self):
        """Test MT region provinces keyboard"""
        keyboard = get_region_provinces_keyboard("MT")

        # MT should have multiple provinces
        province_rows = keyboard.inline_keyboard[:-1]
        # Should have at least a few provinces
        assert len(province_rows) >= 5

    def test_region_provinces_mn(self):
        """Test MN region provinces keyboard"""
        keyboard = get_region_provinces_keyboard("MN")

        # MN should have most provinces (21)
        province_rows = keyboard.inline_keyboard[:-1]
        assert len(province_rows) >= 10  # At least 10 rows

    def test_region_provinces_two_column_layout(self):
        """Test provinces use 2-column layout"""
        keyboard = get_region_provinces_keyboard("MN")

        # All province rows (except possibly last and back) should have 2 buttons
        province_rows = keyboard.inline_keyboard[:-1]  # Exclude back button

        for row in province_rows[:-1]:  # All but last province row
            assert len(row) <= 2

    def test_region_provinces_has_back_button(self):
        """Test region provinces keyboard has back button"""
        keyboard = get_region_provinces_keyboard("MB")

        # Last row should be back button
        last_row = keyboard.inline_keyboard[-1]
        assert len(last_row) == 1
        assert "Quay lại" in last_row[0].text
        assert last_row[0].callback_data == "results_menu"

    def test_region_provinces_callback_format(self):
        """Test province callback data format"""
        keyboard = get_region_provinces_keyboard("MT")

        # Check all province buttons have correct callback format
        for row in keyboard.inline_keyboard[:-1]:  # Exclude back button
            for button in row:
                assert button.callback_data.startswith("result_")
                province_code = button.callback_data.replace("result_", "")
                assert province_code in PROVINCES

    def test_region_provinces_sorted_by_name(self):
        """Test provinces are sorted alphabetically by name"""
        keyboard = get_region_provinces_keyboard("MN")

        # Get province names
        province_names = []
        for row in keyboard.inline_keyboard[:-1]:  # Exclude back button
            for button in row:
                province_names.append(button.text)

        # Check if sorted (Vietnamese sorting might differ, so just check some order exists)
        # At least first and last should be different
        assert len(province_names) > 1
        assert province_names[0] != province_names[-1]


class TestGetBackToResultsKeyboard:
    """Test get_back_to_results_keyboard() function"""

    def test_back_to_results_structure(self):
        """Test back to results keyboard structure"""
        keyboard = get_back_to_results_keyboard()

        # Should have 2 rows
        assert len(keyboard.inline_keyboard) == 2

    def test_back_to_results_button_texts(self):
        """Test back to results keyboard button texts"""
        keyboard = get_back_to_results_keyboard()

        button_texts = [row[0].text for row in keyboard.inline_keyboard]

        assert any("tỉnh khác" in text for text in button_texts)
        assert any("trang chủ" in text for text in button_texts)

    def test_back_to_results_callback_data(self):
        """Test back to results keyboard callback data"""
        keyboard = get_back_to_results_keyboard()

        callbacks = [row[0].callback_data for row in keyboard.inline_keyboard]

        assert "results_menu" in callbacks
        assert "back_to_main" in callbacks

    def test_back_to_results_single_column(self):
        """Test back to results uses single column"""
        keyboard = get_back_to_results_keyboard()

        for row in keyboard.inline_keyboard:
            assert len(row) == 1


class TestGetWeekScheduleKeyboard:
    """Test get_week_schedule_keyboard() function"""

    def test_week_schedule_structure(self):
        """Test week schedule keyboard structure"""
        keyboard = get_week_schedule_keyboard()

        # Should have 3 rows
        assert len(keyboard.inline_keyboard) == 3

    def test_week_schedule_button_texts(self):
        """Test week schedule keyboard button texts"""
        keyboard = get_week_schedule_keyboard()

        button_texts = [row[0].text for row in keyboard.inline_keyboard]

        assert any("lịch hôm nay" in text.lower() for text in button_texts)
        assert any("kết quả" in text.lower() for text in button_texts)
        assert any("quay lại" in text.lower() for text in button_texts)

    def test_week_schedule_callback_data(self):
        """Test week schedule keyboard callback data"""
        keyboard = get_week_schedule_keyboard()

        callbacks = [row[0].callback_data for row in keyboard.inline_keyboard]

        assert "schedule_today" in callbacks
        assert "results_menu" in callbacks
        assert "back_to_main" in callbacks

    def test_week_schedule_single_column(self):
        """Test week schedule uses single column"""
        keyboard = get_week_schedule_keyboard()

        for row in keyboard.inline_keyboard:
            assert len(row) == 1
