"""Unit tests for statistics formatters"""

import pytest
from app.ui.formatters import (
    format_lo_2_so_stats,
    format_lo_3_so_stats,
    format_lo_gan,
)


class TestFormatLo2SoStats:
    """Test format_lo_2_so_stats() function"""

    @pytest.fixture
    def sample_stats(self):
        """Sample statistics data"""
        return {
            "date": "2025-10-15",
            "province": "TP. Hồ Chí Minh",
            "all_numbers": ["12", "23", "34", "45", "56"],
            "frequency": {"12": 2, "23": 1, "34": 3, "45": 1, "56": 1},
            "by_head": {
                0: [],
                1: ["12"],
                2: ["23"],
                3: ["34"],
                4: ["45"],
                5: ["56"],
                6: [],
                7: [],
                8: [],
                9: [],
            },
            "by_tail": {
                0: [],
                1: [],
                2: ["12"],
                3: ["23"],
                4: ["34"],
                5: ["45"],
                6: ["56"],
                7: [],
                8: [],
                9: [],
            },
        }

    def test_format_lo_2_so_basic(self, sample_stats):
        """Test basic formatting"""
        result = format_lo_2_so_stats(sample_stats)

        assert isinstance(result, str)
        assert "📊" in result
        assert "THỐNG KÊ LÔ 2 SỐ" in result
        assert "2025-10-15" in result

    def test_format_lo_2_so_shows_numbers(self, sample_stats):
        """Test that all numbers are shown"""
        result = format_lo_2_so_stats(sample_stats)

        assert "12" in result
        assert "23" in result
        assert "34" in result
        assert "45" in result
        assert "56" in result

    def test_format_lo_2_so_shows_frequency(self, sample_stats):
        """Test that frequency is shown"""
        result = format_lo_2_so_stats(sample_stats)

        # Should show numbers with frequency > 1
        assert "34" in result  # frequency 3
        assert "3 lần" in result
        assert "12" in result  # frequency 2
        assert "2 lần" in result

    def test_format_lo_2_so_with_province_override(self, sample_stats):
        """Test with province name override"""
        result = format_lo_2_so_stats(sample_stats, "Miền Bắc")

        assert "MIỀN BẮC" in result

    def test_format_lo_2_so_empty_data(self):
        """Test with empty data"""
        empty_stats = {
            "date": "2025-10-15",
            "province": "Test",
            "all_numbers": [],
            "frequency": {},
        }

        result = format_lo_2_so_stats(empty_stats)

        assert "Chưa có dữ liệu" in result

    def test_format_lo_2_so_html_formatting(self, sample_stats):
        """Test that HTML tags are used"""
        result = format_lo_2_so_stats(sample_stats)

        assert "<b>" in result
        assert "</b>" in result
        assert "<i>" in result
        assert "</i>" in result


class TestFormatLo3SoStats:
    """Test format_lo_3_so_stats() function"""

    @pytest.fixture
    def sample_stats_3d(self):
        """Sample 3-digit statistics data"""
        return {
            "date": "2025-10-15",
            "province": "TP. Hồ Chí Minh",
            "all_numbers": ["123", "456", "789"],
            "frequency": {"123": 2, "456": 1, "789": 1},
        }

    def test_format_lo_3_so_basic(self, sample_stats_3d):
        """Test basic formatting"""
        result = format_lo_3_so_stats(sample_stats_3d)

        assert isinstance(result, str)
        assert "📊" in result
        assert "THỐNG KÊ LÔ 3 SỐ" in result
        assert "BA CÀNG" in result
        assert "2025-10-15" in result

    def test_format_lo_3_so_shows_numbers(self, sample_stats_3d):
        """Test that 3-digit numbers are shown"""
        result = format_lo_3_so_stats(sample_stats_3d)

        assert "123" in result
        assert "456" in result
        assert "789" in result

    def test_format_lo_3_so_shows_frequency(self, sample_stats_3d):
        """Test that frequency is shown"""
        result = format_lo_3_so_stats(sample_stats_3d)

        # Should show numbers with frequency > 1
        assert "123" in result
        assert "2 lần" in result

    def test_format_lo_3_so_empty_data(self):
        """Test with empty data"""
        empty_stats = {
            "date": "2025-10-15",
            "province": "Test",
            "all_numbers": [],
            "frequency": {},
        }

        result = format_lo_3_so_stats(empty_stats)

        assert "Chưa có dữ liệu" in result

    def test_format_lo_3_so_html_formatting(self, sample_stats_3d):
        """Test that HTML tags are used"""
        result = format_lo_3_so_stats(sample_stats_3d)

        assert "<b>" in result
        assert "</b>" in result
        assert "<i>" in result
        assert "</i>" in result


class TestFormatLoGan:
    """Test format_lo_gan() function"""

    @pytest.fixture
    def sample_gan_data(self):
        """Sample Lô Gan data"""
        return {
            "region": "MB",
            "period": "30 ngày",
            "gan_numbers": [
                {"number": "00", "days_not_appeared": 25},
                {"number": "99", "days_not_appeared": 20},
                {"number": "55", "days_not_appeared": 15},
            ],
        }

    def test_format_lo_gan_basic(self, sample_gan_data):
        """Test basic formatting"""
        result = format_lo_gan(sample_gan_data)

        assert isinstance(result, str)
        assert "❄️" in result
        assert "LÔ GAN" in result
        assert "30 ngày" in result

    def test_format_lo_gan_shows_numbers(self, sample_gan_data):
        """Test that gan numbers are shown"""
        result = format_lo_gan(sample_gan_data)

        assert "00" in result
        assert "25 ngày" in result
        assert "99" in result
        assert "20 ngày" in result

    def test_format_lo_gan_shows_beta_note(self, sample_gan_data):
        """Test that beta/mock data note is shown"""
        result = format_lo_gan(sample_gan_data)

        assert "Dữ liệu mẫu" in result or "beta" in result.lower()
        assert "phiên bản tiếp theo" in result.lower()

    def test_format_lo_gan_with_province_override(self, sample_gan_data):
        """Test with province name override"""
        result = format_lo_gan(sample_gan_data, "Miền Nam")

        assert "MIỀN NAM" in result

    def test_format_lo_gan_empty_data(self):
        """Test with empty data"""
        empty_gan = {
            "region": "MB",
            "period": "30 ngày",
            "gan_numbers": [],
        }

        result = format_lo_gan(empty_gan)

        assert "Chưa có dữ liệu" in result

    def test_format_lo_gan_html_formatting(self, sample_gan_data):
        """Test that HTML tags are used"""
        result = format_lo_gan(sample_gan_data)

        assert "<b>" in result
        assert "</b>" in result
        assert "<i>" in result
        assert "</i>" in result


class TestFormatterIntegration:
    """Integration tests for statistics formatters"""

    def test_all_formatters_return_strings(self):
        """Test that all formatters return strings"""
        # Sample data
        stats_2d = {
            "date": "2025-10-15",
            "province": "Test",
            "all_numbers": ["12"],
            "frequency": {"12": 1},
        }

        stats_3d = {
            "date": "2025-10-15",
            "province": "Test",
            "all_numbers": ["123"],
            "frequency": {"123": 1},
        }

        gan_data = {
            "region": "MB",
            "period": "30 ngày",
            "gan_numbers": [{"number": "00", "days_not_appeared": 15}],
        }

        result1 = format_lo_2_so_stats(stats_2d)
        result2 = format_lo_3_so_stats(stats_3d)
        result3 = format_lo_gan(gan_data)

        assert isinstance(result1, str)
        assert isinstance(result2, str)
        assert isinstance(result3, str)

    def test_formatters_handle_empty_gracefully(self):
        """Test that all formatters handle empty data"""
        empty_stats = {
            "date": "",
            "province": "",
            "all_numbers": [],
            "frequency": {},
        }

        empty_gan = {"region": "", "period": "", "gan_numbers": []}

        # Should not crash
        result1 = format_lo_2_so_stats(empty_stats)
        result2 = format_lo_3_so_stats(empty_stats)
        result3 = format_lo_gan(empty_gan)

        assert isinstance(result1, str)
        assert isinstance(result2, str)
        assert isinstance(result3, str)

    def test_formatters_use_emojis(self):
        """Test that formatters use emojis"""
        stats = {
            "date": "2025-10-15",
            "province": "Test",
            "all_numbers": ["12"],
            "frequency": {"12": 2},
        }

        gan_data = {
            "region": "MB",
            "period": "30 ngày",
            "gan_numbers": [{"number": "00", "days_not_appeared": 15}],
        }

        result1 = format_lo_2_so_stats(stats)
        result2 = format_lo_3_so_stats(stats)
        result3 = format_lo_gan(gan_data)

        # Each should have at least one emoji
        assert any(char in result1 for char in "📊🎯📈")
        assert any(char in result2 for char in "📊🎯📈")
        assert any(char in result3 for char in "❄️🔢📝")

    def test_formatters_output_not_empty(self):
        """Test that formatters produce non-empty output"""
        stats = {
            "date": "2025-10-15",
            "province": "Test",
            "all_numbers": ["12"],
            "frequency": {"12": 1},
        }

        gan_data = {
            "region": "MB",
            "period": "30 ngày",
            "gan_numbers": [{"number": "00", "days_not_appeared": 15}],
        }

        result1 = format_lo_2_so_stats(stats)
        result2 = format_lo_3_so_stats(stats)
        result3 = format_lo_gan(gan_data)

        assert len(result1) > 50
        assert len(result2) > 50
        assert len(result3) > 50
