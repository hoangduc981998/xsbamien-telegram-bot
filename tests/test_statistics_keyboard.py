"""Unit tests for statistics keyboard functions"""

import pytest
from telegram import InlineKeyboardMarkup

from app.ui.keyboards import (
    get_statistics_menu_keyboard,
    get_result_display_keyboard,
)


class TestStatisticsMenuKeyboard:
    """Test get_statistics_menu_keyboard() function"""

    def test_keyboard_structure(self):
        """Test keyboard has correct 2x2 structure"""
        keyboard = get_statistics_menu_keyboard("MB")
        assert len(keyboard.inline_keyboard) == 2  # 2 rows
        assert len(keyboard.inline_keyboard[0]) == 2  # Row 1: 2 buttons
        assert len(keyboard.inline_keyboard[1]) == 2  # Row 2: 2 buttons

    def test_button_labels(self):
        """Test button labels are correct"""
        keyboard = get_statistics_menu_keyboard("MB")
        
        # Row 1
        assert keyboard.inline_keyboard[0][0].text == "📊 Lô 2 số"
        assert keyboard.inline_keyboard[0][1].text == "🎰 Lô 3 số"
        
        # Row 2
        assert keyboard.inline_keyboard[1][0].text == "🔢 Đầu Lô"
        assert keyboard.inline_keyboard[1][1].text == "🔢 Đuôi Lô"

    def test_callback_data_format_mb(self):
        """Test callback data includes province code for MB"""
        keyboard = get_statistics_menu_keyboard("MB")
        
        assert keyboard.inline_keyboard[0][0].callback_data == "stats_lo2_MB"
        assert keyboard.inline_keyboard[0][1].callback_data == "stats_lo3_MB"
        assert keyboard.inline_keyboard[1][0].callback_data == "stats_dau_MB"
        assert keyboard.inline_keyboard[1][1].callback_data == "stats_duoi_MB"

    def test_callback_data_format_tphcm(self):
        """Test callback data includes province code for TPHCM"""
        keyboard = get_statistics_menu_keyboard("TPHCM")
        
        assert keyboard.inline_keyboard[0][0].callback_data == "stats_lo2_TPHCM"
        assert keyboard.inline_keyboard[0][1].callback_data == "stats_lo3_TPHCM"
        assert keyboard.inline_keyboard[1][0].callback_data == "stats_dau_TPHCM"
        assert keyboard.inline_keyboard[1][1].callback_data == "stats_duoi_TPHCM"

    def test_callback_data_format_danang(self):
        """Test callback data includes province code for DANA"""
        keyboard = get_statistics_menu_keyboard("DANA")
        
        assert keyboard.inline_keyboard[0][0].callback_data == "stats_lo2_DANA"
        assert keyboard.inline_keyboard[0][1].callback_data == "stats_lo3_DANA"
        assert keyboard.inline_keyboard[1][0].callback_data == "stats_dau_DANA"
        assert keyboard.inline_keyboard[1][1].callback_data == "stats_duoi_DANA"


class TestResultDisplayKeyboard:
    """Test get_result_display_keyboard() function"""

    def test_keyboard_has_all_sections(self):
        """Test keyboard includes both new and old buttons"""
        keyboard = get_result_display_keyboard("MB")
        
        # Should have at least:
        # - 2 rows for new stats menu (2x2)
        # - 1 row for old Lô 2 số / Lô 3 số
        # - 1 row for Lô Gan
        # - 2 rows for navigation
        assert len(keyboard.inline_keyboard) >= 6

    def test_new_statistics_buttons_at_top(self):
        """Test new statistics buttons are in first two rows"""
        keyboard = get_result_display_keyboard("TPHCM")
        
        # First row should be new Lô 2 số / Lô 3 số
        assert keyboard.inline_keyboard[0][0].text == "📊 Lô 2 số"
        assert keyboard.inline_keyboard[0][1].text == "🎰 Lô 3 số"
        assert keyboard.inline_keyboard[0][0].callback_data == "stats_lo2_TPHCM"
        assert keyboard.inline_keyboard[0][1].callback_data == "stats_lo3_TPHCM"
        
        # Second row should be new Đầu Lô / Đuôi Lô
        assert keyboard.inline_keyboard[1][0].text == "🔢 Đầu Lô"
        assert keyboard.inline_keyboard[1][1].text == "🔢 Đuôi Lô"
        assert keyboard.inline_keyboard[1][0].callback_data == "stats_dau_TPHCM"
        assert keyboard.inline_keyboard[1][1].callback_data == "stats_duoi_TPHCM"

    def test_old_statistics_buttons_preserved(self):
        """Test old statistics buttons are still present"""
        keyboard = get_result_display_keyboard("MB")
        
        # Find the old buttons (should be after new ones)
        button_texts = []
        for row in keyboard.inline_keyboard:
            for button in row:
                button_texts.append(button.text)
        
        # Old buttons should exist
        assert "📊 Thống kê Lô 2 số" in button_texts
        assert "📊 Thống kê Lô 3 số" in button_texts
        assert "🔥 Lô Gan" in button_texts

    def test_navigation_buttons_preserved(self):
        """Test navigation buttons are still present"""
        keyboard = get_result_display_keyboard("DANA")
        
        # Last two rows should be navigation
        button_texts = []
        for row in keyboard.inline_keyboard[-2:]:
            for button in row:
                button_texts.append(button.text)
        
        assert "🔙 Quay lại" in button_texts
        assert "🏠 Về trang chủ" in button_texts

    def test_callback_data_consistency(self):
        """Test all callback data includes correct province code"""
        province_code = "ANGI"
        keyboard = get_result_display_keyboard(province_code)
        
        # Check all buttons have correct province code
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data.startswith("stats"):
                    # All stats buttons should end with province code
                    assert button.callback_data.endswith(province_code), \
                        f"Button '{button.text}' callback '{button.callback_data}' doesn't end with {province_code}"


class TestKeyboardTypes:
    """Test that keyboards return correct types"""

    def test_statistics_menu_returns_keyboard_markup(self):
        """Test get_statistics_menu_keyboard returns InlineKeyboardMarkup"""
        result = get_statistics_menu_keyboard("MB")
        assert isinstance(result, InlineKeyboardMarkup)

    def test_result_display_returns_keyboard_markup(self):
        """Test get_result_display_keyboard returns InlineKeyboardMarkup"""
        result = get_result_display_keyboard("TPHCM")
        assert isinstance(result, InlineKeyboardMarkup)


class TestEdgeCases:
    """Test edge cases for keyboard functions"""

    def test_empty_province_code(self):
        """Test keyboard handles empty province code"""
        keyboard = get_statistics_menu_keyboard("")
        assert keyboard.inline_keyboard[0][0].callback_data == "stats_lo2_"

    def test_special_characters_in_province_code(self):
        """Test keyboard handles special characters"""
        keyboard = get_statistics_menu_keyboard("TEST_123")
        assert keyboard.inline_keyboard[0][0].callback_data == "stats_lo2_TEST_123"

    def test_very_long_province_code(self):
        """Test keyboard handles very long province code"""
        long_code = "A" * 100
        keyboard = get_statistics_menu_keyboard(long_code)
        assert keyboard.inline_keyboard[0][0].callback_data == f"stats_lo2_{long_code}"
