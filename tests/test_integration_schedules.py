"""Integration tests for schedule keyboard functions - Testing all 7 days of the week"""

import pytest
from unittest.mock import patch
from datetime import datetime, date

from app.ui.keyboards import (
    get_schedule_today_keyboard,
    get_today_schedule_actions,
)
from app.ui.messages import get_today_schedule_message
from app.config import PROVINCES, SCHEDULE
from app.utils.cache import ScheduleCache


class TestCompleteWeekIntegration:
    """Integration tests for all 7 days of the week"""

    def setup_method(self):
        """Clear cache before each test"""
        ScheduleCache.clear_cache()

    @pytest.mark.parametrize(
        "python_weekday,day_name,schedule_day",
        [
            (0, "Thứ Hai", 1),
            (1, "Thứ Ba", 2),
            (2, "Thứ Tư", 3),
            (3, "Thứ Năm", 4),
            (4, "Thứ Sáu", 5),
            (5, "Thứ Bảy", 6),
            (6, "Chủ Nhật", 0),
        ],
    )
    def test_complete_day_flow(self, python_weekday, day_name, schedule_day):
        """Test complete flow: message generation + button generation for each day"""
        with patch("app.utils.cache.datetime") as mock_kb_dt, patch("app.ui.messages.datetime") as mock_msg_dt:

            # Mock datetime for both modules
            mock_kb_dt.now.return_value.weekday.return_value = python_weekday
            mock_kb_dt.now.return_value.date.return_value = date(2025, 10, 14)
            mock_msg_dt.now.return_value.weekday.return_value = python_weekday
            mock_msg_dt.now.return_value.strftime.return_value = "14/10/2025"

            # Get message and keyboard
            message = get_today_schedule_message()
            keyboard = get_schedule_today_keyboard()

            # Extract provinces from buttons
            button_provinces = []
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        button_provinces.append(button.callback_data.replace("result_", ""))

            # Get expected provinces for this day
            expected_provinces = []
            for region in ["MB", "MT", "MN"]:
                expected_provinces.extend(SCHEDULE[region].get(schedule_day, []))

            # Verify
            assert button_provinces == expected_provinces, f"{day_name}: Button provinces don't match schedule"

            # Verify message contains day name
            assert day_name in message, f"Message doesn't contain '{day_name}'"

            # Verify message contains all province names
            for prov_code in expected_provinces:
                if prov_code in PROVINCES:
                    prov_name = PROVINCES[prov_code]["name"]
                    assert prov_name in message, f"{day_name}: Province '{prov_name}' not in message"

    def test_thursday_has_most_provinces(self):
        """Thursday should have 7 provinces (most in the week)"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 3  # Thursday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            result_count = sum(
                1
                for row in keyboard.inline_keyboard[:-1]
                for button in row
                if button.callback_data.startswith("result_")
            )

            assert result_count == 7, "Thursday should have 7 provinces"

    def test_saturday_has_most_mn_provinces(self):
        """Saturday should have 4 MN provinces (most MN in the week)"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 5  # Saturday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            button_provinces = []
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        code = button.callback_data.replace("result_", "")
                        button_provinces.append(code)

            mn_provinces = [p for p in button_provinces if PROVINCES.get(p, {}).get("region") == "MN"]

            assert len(mn_provinces) == 4, f"Saturday should have 4 MN provinces, got {len(mn_provinces)}"

    @pytest.mark.parametrize("python_weekday", range(7))
    def test_message_button_result_consistency(self, python_weekday):
        """Verify provinces in message exactly match provinces in buttons"""
        with patch("app.utils.cache.datetime") as mock_kb_dt, patch("app.ui.messages.datetime") as mock_msg_dt:

            mock_kb_dt.now.return_value.weekday.return_value = python_weekday
            mock_kb_dt.now.return_value.date.return_value = date(2025, 10, 14)
            mock_msg_dt.now.return_value.weekday.return_value = python_weekday
            mock_msg_dt.now.return_value.strftime.return_value = "14/10/2025"

            message = get_today_schedule_message()
            keyboard = get_schedule_today_keyboard()

            # Extract province codes from buttons
            button_codes = []
            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        button_codes.append(button.callback_data.replace("result_", ""))

            # Verify each province in buttons is mentioned in message
            for code in button_codes:
                if code in PROVINCES:
                    prov_name = PROVINCES[code]["name"]
                    assert prov_name in message, (
                        f"Weekday {python_weekday}: " f"Province '{prov_name}' in button but not in message"
                    )

    def test_region_order_consistent(self):
        """Verify provinces are always ordered MB → MT → MN"""
        for weekday in range(7):
            with patch("app.utils.cache.datetime") as mock_dt:
                mock_dt.now.return_value.weekday.return_value = weekday
                mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

                keyboard = get_schedule_today_keyboard()

                # Extract provinces in order
                provinces_in_order = []
                for row in keyboard.inline_keyboard[:-1]:
                    for button in row:
                        if button.callback_data.startswith("result_"):
                            code = button.callback_data.replace("result_", "")
                            if code in PROVINCES:
                                region = PROVINCES[code]["region"]
                                provinces_in_order.append(region)

                # Verify order: all MB first, then MT, then MN
                if provinces_in_order:
                    # Find indices of last MB, MT
                    mb_indices = [i for i, r in enumerate(provinces_in_order) if r == "MB"]
                    mt_indices = [i for i, r in enumerate(provinces_in_order) if r == "MT"]
                    mn_indices = [i for i, r in enumerate(provinces_in_order) if r == "MN"]

                    if mb_indices and mt_indices:
                        assert max(mb_indices) < min(mt_indices), f"Weekday {weekday}: MB should come before MT"

                    if mt_indices and mn_indices:
                        assert max(mt_indices) < min(mn_indices), f"Weekday {weekday}: MT should come before MN"


class TestScheduleActionsIntegration:
    """Integration tests for get_today_schedule_actions()"""

    def setup_method(self):
        """Clear cache before each test"""
        ScheduleCache.clear_cache()

    @pytest.mark.parametrize("python_weekday", range(7))
    def test_actions_match_schedule_keyboard(self, python_weekday):
        """Verify get_today_schedule_actions() returns same provinces
        as get_schedule_today_keyboard()"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = python_weekday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard1 = get_schedule_today_keyboard()
            keyboard2 = get_today_schedule_actions()

            # Extract provinces from both
            provinces1 = []
            for row in keyboard1.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        provinces1.append(button.callback_data)

            provinces2 = []
            for row in keyboard2.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        provinces2.append(button.callback_data)

            assert provinces1 == provinces2, (
                f"Weekday {python_weekday}: " f"Province lists don't match between functions"
            )

    def test_navigation_buttons_present_all_days(self):
        """Verify navigation buttons are present for all 7 days"""
        for weekday in range(7):
            with patch("app.utils.cache.datetime") as mock_dt:
                mock_dt.now.return_value.weekday.return_value = weekday
                mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

                keyboard = get_today_schedule_actions()

                # Check last 2 rows (separate navigation buttons)
                schedule_week_row = keyboard.inline_keyboard[-2]
                back_row = keyboard.inline_keyboard[-1]

                assert len(schedule_week_row) == 1, f"Weekday {weekday}: Schedule week row should have 1 button"
                assert schedule_week_row[0].callback_data == "schedule_week"

                assert len(back_row) == 1, f"Weekday {weekday}: Back row should have 1 button"
                assert back_row[0].callback_data == "back_to_main"


class TestButtonCallbackDataIntegration:
    """Integration tests for button callback data"""

    def setup_method(self):
        """Clear cache before each test"""
        ScheduleCache.clear_cache()

    @pytest.mark.parametrize("python_weekday", range(7))
    def test_all_callback_data_valid(self, python_weekday):
        """Verify all button callback_data references valid province codes"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = python_weekday
            mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

            keyboard = get_schedule_today_keyboard()

            for row in keyboard.inline_keyboard[:-1]:
                for button in row:
                    if button.callback_data.startswith("result_"):
                        code = button.callback_data.replace("result_", "")
                        assert code in PROVINCES, f"Weekday {python_weekday}: " f"Invalid province code '{code}'"

    def test_callback_format_consistency(self):
        """Verify callback_data format is consistent across all days"""
        for weekday in range(7):
            with patch("app.utils.cache.datetime") as mock_dt:
                mock_dt.now.return_value.weekday.return_value = weekday
                mock_dt.now.return_value.date.return_value = date(2025, 10, 14)

                keyboard = get_schedule_today_keyboard()

                for row in keyboard.inline_keyboard[:-1]:
                    for button in row:
                        if button.callback_data != "back_to_main":
                            assert button.callback_data.startswith("result_"), (
                                f"Weekday {weekday}: " f"Invalid callback format: {button.callback_data}"
                            )

                            code = button.callback_data.replace("result_", "")
                            assert code.isupper(), f"Weekday {weekday}: " f"Province code should be uppercase: {code}"
