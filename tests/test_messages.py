"""Unit tests for message templates"""

import pytest
from unittest.mock import patch
from datetime import datetime, date, timezone, timedelta

from app.ui.messages import (
    WELCOME_MESSAGE,
    HELP_MESSAGE,
    LOADING_MESSAGE,
    ERROR_MESSAGE,
    NO_DATA_MESSAGE,
    get_schedule_message,
    get_today_schedule_message,
    get_tomorrow_schedule_message,
    get_full_week_schedule_message,
    get_region_message,
)


class TestMessageConstants:
    """Test static message templates"""

    def test_welcome_message_content(self):
        """Test welcome message contains key content"""
        assert "🎰" in WELCOME_MESSAGE
        assert "Chào mừng" in WELCOME_MESSAGE
        assert "XS Ba Miền Bot" in WELCOME_MESSAGE
        assert "Miền Bắc" in WELCOME_MESSAGE
        assert "Miền Trung" in WELCOME_MESSAGE
        assert "Miền Nam" in WELCOME_MESSAGE
        assert "Kết quả trực tiếp hàng ngày" in WELCOME_MESSAGE

    def test_help_message_content(self):
        """Test help message contains commands and instructions"""
        assert "Hướng Dẫn Sử Dụng Bot" in HELP_MESSAGE
        assert "/start" in HELP_MESSAGE
        assert "/help" in HELP_MESSAGE
        assert "/mb" in HELP_MESSAGE
        assert "/mt" in HELP_MESSAGE
        assert "/mn" in HELP_MESSAGE
        assert "16:15 - 16:45" in HELP_MESSAGE  # MN draw time
        assert "17:15 - 17:45" in HELP_MESSAGE  # MT draw time
        assert "18:15 - 18:30" in HELP_MESSAGE  # MB draw time

    def test_loading_message_content(self):
        """Test loading message"""
        assert "⏳" in LOADING_MESSAGE
        assert "tải dữ liệu" in LOADING_MESSAGE or "chờ" in LOADING_MESSAGE

    def test_error_message_content(self):
        """Test error message"""
        assert "❌" in ERROR_MESSAGE
        assert "lỗi" in ERROR_MESSAGE

    def test_no_data_message_content(self):
        """Test no data message"""
        assert "😔" in NO_DATA_MESSAGE
        assert "Chưa có dữ liệu" in NO_DATA_MESSAGE or "không có" in NO_DATA_MESSAGE.lower()

    def test_message_constants_are_strings(self):
        """Test all message constants are strings"""
        assert isinstance(WELCOME_MESSAGE, str)
        assert isinstance(HELP_MESSAGE, str)
        assert isinstance(LOADING_MESSAGE, str)
        assert isinstance(ERROR_MESSAGE, str)
        assert isinstance(NO_DATA_MESSAGE, str)

    def test_messages_have_content(self):
        """Test messages are not empty"""
        assert len(WELCOME_MESSAGE) > 0
        assert len(HELP_MESSAGE) > 0
        assert len(LOADING_MESSAGE) > 0
        assert len(ERROR_MESSAGE) > 0
        assert len(NO_DATA_MESSAGE) > 0


class TestGetScheduleMessage:
    """Test get_schedule_message() function"""

    @patch('app.ui.messages.datetime')
    def test_schedule_message_structure(self, mock_datetime):
        """Test schedule message has proper structure"""
        mock_datetime.now.return_value.weekday.return_value = 0  # Monday

        result = get_schedule_message()

        assert "📅 <b>LỊCH QUAY THƯỞNG TRONG TUẦN</b>" in result
        assert "⏰ <b>Giờ Quay:</b>" in result
        assert "🟢 Miền Nam:" in result
        assert "🟠 Miền Trung:" in result
        assert "🔴 Miền Bắc:" in result

    @patch('app.ui.messages.datetime')
    def test_schedule_shows_all_days(self, mock_datetime):
        """Test schedule message includes all days of week"""
        mock_datetime.now.return_value.weekday.return_value = 2  # Wednesday

        result = get_schedule_message()

        # All Vietnamese day names should appear
        assert "Chủ Nhật" in result
        assert "Thứ Hai" in result
        assert "Thứ Ba" in result
        assert "Thứ Tư" in result
        assert "Thứ Năm" in result
        assert "Thứ Sáu" in result
        assert "Thứ Bảy" in result

    @patch('app.ui.messages.datetime')
    def test_schedule_highlights_today(self, mock_datetime):
        """Test schedule message highlights current day"""
        mock_datetime.now.return_value.weekday.return_value = 3  # Thursday

        result = get_schedule_message()

        # Thursday should be marked as HÔM NAY
        assert "Thứ Năm" in result
        assert "HÔM NAY" in result

    @patch('app.ui.messages.datetime')
    def test_schedule_includes_draw_times(self, mock_datetime):
        """Test schedule message includes draw times"""
        mock_datetime.now.return_value.weekday.return_value = 0

        result = get_schedule_message()

        # Should contain draw time information
        assert "16:15" in result or "16:30" in result  # MN time
        assert "17:15" in result or "17:30" in result  # MT time
        assert "18:15" in result or "18:30" in result  # MB time


class TestGetTodayScheduleMessage:
    """Test get_today_schedule_message() function"""

    @patch('app.ui.messages.datetime')
    def test_today_schedule_structure(self, mock_datetime):
        """Test today's schedule has proper structure"""
        mock_now = mock_datetime.now.return_value
        mock_now.weekday.return_value = 0  # Monday
        mock_now.strftime.return_value = "14/10/2025"

        result = get_today_schedule_message()

        assert "🔥 <b>HÔM NAY" in result
        assert "Thứ Hai" in result
        assert "14/10/2025" in result
        assert "🟢 <b>Miền Nam</b>" in result
        assert "🟠 <b>Miền Trung</b>" in result
        assert "🔴 <b>Miền Bắc</b>" in result

    @patch('app.ui.messages.datetime')
    def test_today_schedule_shows_provinces(self, mock_datetime):
        """Test today's schedule shows province names"""
        mock_now = mock_datetime.now.return_value
        mock_now.weekday.return_value = 0  # Monday (schedule_day=1)
        mock_now.strftime.return_value = "14/10/2025"

        result = get_today_schedule_message()

        # Monday should have TPHCM, DOTH, CAMA for MN
        # and THTH, PHYE for MT
        assert "TP.HCM" in result or "HCM" in result or "Hồ Chí Minh" in result
        assert "Phú Yên" in result or "PHYE" in result

    @patch('app.ui.messages.datetime')
    def test_today_schedule_always_shows_mb(self, mock_datetime):
        """Test today's schedule always shows Miền Bắc"""
        mock_now = mock_datetime.now.return_value
        mock_now.weekday.return_value = 5  # Saturday
        mock_now.strftime.return_value = "18/10/2025"

        result = get_today_schedule_message()

        assert "🔴 <b>Miền Bắc</b>" in result
        assert "hàng ngày" in result

    @patch('app.ui.messages.datetime')
    def test_today_schedule_shows_draw_times(self, mock_datetime):
        """Test today's schedule shows specific draw times"""
        mock_now = mock_datetime.now.return_value
        mock_now.weekday.return_value = 2
        mock_now.strftime.return_value = "16/10/2025"

        result = get_today_schedule_message()

        assert "16:15 - 16:45" in result  # MN
        assert "17:15 - 17:45" in result  # MT
        assert "18:15 - 18:30" in result  # MB


class TestGetTomorrowScheduleMessage:
    """Test get_tomorrow_schedule_message() function"""

    @patch('app.ui.messages.datetime')
    def test_tomorrow_schedule_structure(self, mock_datetime):
        """Test tomorrow's schedule has proper structure"""
        # Today is Monday, tomorrow is Tuesday
        mock_now = mock_datetime.now.return_value
        mock_tomorrow = mock_now + timedelta(days=1)
        mock_tomorrow.weekday.return_value = 1  # Tuesday
        mock_tomorrow.strftime.return_value = "15/10/2025"

        result = get_tomorrow_schedule_message()

        assert "📆 <b>NGÀY MAI" in result
        assert "Thứ Ba" in result
        assert "15/10/2025" in result

    @patch('app.ui.messages.datetime')
    def test_tomorrow_schedule_shows_regions(self, mock_datetime):
        """Test tomorrow's schedule shows all regions"""
        mock_now = mock_datetime.now.return_value
        mock_tomorrow = mock_now + timedelta(days=1)
        mock_tomorrow.weekday.return_value = 2
        mock_tomorrow.strftime.return_value = "16/10/2025"

        result = get_tomorrow_schedule_message()

        assert "🟢 <b>Miền Nam</b>" in result
        assert "🟠 <b>Miền Trung</b>" in result
        assert "🔴 <b>Miền Bắc</b>" in result

    @patch('app.ui.messages.datetime')
    def test_tomorrow_schedule_encouragement(self, mock_datetime):
        """Test tomorrow's schedule has encouragement message"""
        mock_now = mock_datetime.now.return_value
        mock_tomorrow = mock_now + timedelta(days=1)
        mock_tomorrow.weekday.return_value = 3
        mock_tomorrow.strftime.return_value = "17/10/2025"

        result = get_tomorrow_schedule_message()

        assert "may mắn" in result or "Chuẩn bị" in result


class TestGetFullWeekScheduleMessage:
    """Test get_full_week_schedule_message() function"""

    def test_full_week_schedule_structure(self):
        """Test full week schedule has proper structure"""
        result = get_full_week_schedule_message()

        assert "📅 <b>LỊCH QUAY THƯỞNG CẢ TUẦN</b>" in result
        assert "🟢 Miền Nam" in result
        assert "🟠 Miền Trung" in result
        assert "🔴 Miền Bắc" in result

    def test_full_week_schedule_shows_all_days(self):
        """Test full week schedule shows all days"""
        result = get_full_week_schedule_message()

        # All days should be present
        assert "Chủ Nhật" in result
        assert "Thứ Hai" in result
        assert "Thứ Ba" in result
        assert "Thứ Tư" in result
        assert "Thứ Năm" in result
        assert "Thứ Sáu" in result
        assert "Thứ Bảy" in result

    def test_full_week_schedule_shows_draw_times(self):
        """Test full week schedule includes draw times"""
        result = get_full_week_schedule_message()

        assert "16:15 - 16:45" in result  # MN
        assert "17:15 - 17:45" in result  # MT
        assert "18:15 - 18:30" in result  # MB

    def test_full_week_schedule_mb_daily(self):
        """Test full week schedule shows MB as daily"""
        result = get_full_week_schedule_message()

        assert "Hàng ngày" in result or "hàng ngày" in result

    def test_full_week_schedule_includes_provinces(self):
        """Test full week schedule includes some province names"""
        result = get_full_week_schedule_message()

        # Check for some well-known provinces
        assert "TP.HCM" in result or "HCM" in result or "Hồ Chí Minh" in result
        assert "Đà Nẵng" in result or "Da Nang" in result
        # Check for at least one Southern province
        assert any(
            province in result
            for province in [
                "Tiền Giang",
                "Kiên Giang",
                "Đồng Tháp",
                "Bến Tre",
                "Vũng Tàu",
            ]
        )


class TestGetRegionMessage:
    """Test get_region_message() function"""

    def test_region_message_mb(self):
        """Test region message for Miền Bắc"""
        result = get_region_message("MB")

        assert "🔴 Miền Bắc" in result
        assert "Giờ quay" in result
        assert "18:15" in result or "18:30" in result
        assert "Chọn tỉnh" in result

    def test_region_message_mt(self):
        """Test region message for Miền Trung"""
        result = get_region_message("MT")

        assert "🟠 Miền Trung" in result
        assert "Giờ quay" in result
        assert "17:15" in result or "17:45" in result

    def test_region_message_mn(self):
        """Test region message for Miền Nam"""
        result = get_region_message("MN")

        assert "🟢 Miền Nam" in result
        assert "Giờ quay" in result
        assert "16:15" in result or "16:45" in result

    def test_region_message_shows_province_count(self):
        """Test region message shows province count"""
        result = get_region_message("MB")

        assert "Tổng số" in result
        assert "tỉnh" in result

    def test_region_message_all_valid_regions(self):
        """Test region message works for all valid region codes"""
        # Test all valid regions don't crash
        for region in ["MB", "MT", "MN"]:
            result = get_region_message(region)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_region_message_has_selection_prompt(self):
        """Test region message has selection prompt"""
        result = get_region_message("MN")

        assert "Chọn" in result or "chọn" in result


class TestMessageFormatting:
    """Test message formatting and special characters"""

    def test_messages_use_html_formatting(self):
        """Test messages use HTML bold tags"""
        assert "<b>" in WELCOME_MESSAGE
        assert "</b>" in WELCOME_MESSAGE
        assert "<b>" in HELP_MESSAGE

    def test_messages_use_emojis(self):
        """Test messages use emojis appropriately"""
        result = get_today_schedule_message()

        # Check for emoji usage
        assert "🔥" in result or "📅" in result
        assert "🟢" in result
        assert "🟠" in result
        assert "🔴" in result

    def test_schedule_functions_return_strings(self):
        """Test all schedule functions return strings"""
        assert isinstance(get_schedule_message(), str)
        assert isinstance(get_today_schedule_message(), str)
        assert isinstance(get_tomorrow_schedule_message(), str)
        assert isinstance(get_full_week_schedule_message(), str)
        assert isinstance(get_region_message("MB"), str)

    def test_messages_not_empty(self):
        """Test generated messages are not empty"""
        assert len(get_schedule_message()) > 50
        assert len(get_today_schedule_message()) > 50
        assert len(get_tomorrow_schedule_message()) > 50
        assert len(get_full_week_schedule_message()) > 50
        assert len(get_region_message("MB")) > 20
