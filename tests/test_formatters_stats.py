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
    def sample_gan_data_mb(self):
        """Sample Lô Gan data for Miền Bắc (daily draws)"""
        return [
            {
                "number": "00",
                "gan_value": 25,
                "days_since_last": 25,
                "periods_since_last": 25,
                "last_seen_date": "15/09/2025",
                "max_cycle": 30,
                "is_daily": True,
                "category": "cuc_gan"
            },
            {
                "number": "99",
                "gan_value": 20,
                "days_since_last": 20,
                "periods_since_last": 20,
                "last_seen_date": "20/09/2025",
                "max_cycle": 22,
                "is_daily": True,
                "category": "gan_lon"
            },
            {
                "number": "55",
                "gan_value": 15,
                "days_since_last": 15,
                "periods_since_last": 15,
                "last_seen_date": "25/09/2025",
                "max_cycle": 18,
                "is_daily": True,
                "category": "gan_thuong"
            },
        ]

    @pytest.fixture
    def sample_gan_data_mn(self):
        """Sample Lô Gan data for Miền Nam (periodic draws)"""
        return [
            {
                "number": "35",
                "gan_value": 7,
                "days_since_last": 48,
                "periods_since_last": 7,
                "last_seen_date": "28/08/2025",
                "max_cycle": 10,
                "is_daily": False,
                "category": "gan_lon"
            },
            {
                "number": "42",
                "gan_value": 5,
                "days_since_last": 35,
                "periods_since_last": 5,
                "last_seen_date": "05/09/2025",
                "max_cycle": 6,
                "is_daily": False,
                "category": "gan_thuong"
            },
        ]

    def test_format_lo_gan_basic_mb(self, sample_gan_data_mb):
        """Test basic formatting for MB"""
        result = format_lo_gan(sample_gan_data_mb, "Miền Bắc")

        assert isinstance(result, str)
        assert "LÔ GAN" in result
        assert "MIỀN BẮC" in result
        assert "50 ngày" in result
        assert "chỉ số đã từng về" in result

    def test_format_lo_gan_basic_mn(self, sample_gan_data_mn):
        """Test basic formatting for MN"""
        result = format_lo_gan(sample_gan_data_mn, "An Giang")

        assert isinstance(result, str)
        assert "LÔ GAN" in result
        assert "AN GIANG" in result
        assert "50 kỳ quay" in result
        assert "chỉ số đã từng về" in result

    def test_format_lo_gan_shows_numbers_mb(self, sample_gan_data_mb):
        """Test that gan numbers are shown for MB with days"""
        result = format_lo_gan(sample_gan_data_mb, "Miền Bắc")

        assert "00" in result
        assert "25" in result
        assert "ngày" in result
        assert "99" in result
        assert "20" in result

    def test_format_lo_gan_shows_numbers_mn(self, sample_gan_data_mn):
        """Test that gan numbers are shown for MN with periods"""
        result = format_lo_gan(sample_gan_data_mn, "An Giang")

        assert "35" in result
        assert "7" in result
        assert "kỳ" in result
        assert "42" in result
        assert "5" in result

    def test_format_lo_gan_shows_database_note(self, sample_gan_data_mb):
        """Test that database note is shown"""
        result = format_lo_gan(sample_gan_data_mb, "Miền Bắc")

        assert "Dữ liệu từ database" in result or "database" in result.lower()

    def test_format_lo_gan_with_province_name(self, sample_gan_data_mb):
        """Test with province name"""
        result = format_lo_gan(sample_gan_data_mb, "Miền Nam")

        assert "MIỀN NAM" in result

    def test_format_lo_gan_empty_data(self):
        """Test with empty data"""
        result = format_lo_gan([], "Miền Bắc")

        assert "Chưa có dữ liệu" in result

    def test_format_lo_gan_html_formatting(self, sample_gan_data_mb):
        """Test that HTML tags are used"""
        result = format_lo_gan(sample_gan_data_mb, "Miền Bắc")

        assert "<b>" in result
        assert "</b>" in result
        assert "<i>" in result
        assert "</i>" in result

    def test_format_lo_gan_category_thresholds_mb(self, sample_gan_data_mb):
        """Test MB category thresholds in legend"""
        result = format_lo_gan(sample_gan_data_mb, "Miền Bắc")

        assert "10-15 ngày" in result
        assert "16-20 ngày" in result
        assert "21+ ngày" in result

    def test_format_lo_gan_category_thresholds_mn(self, sample_gan_data_mn):
        """Test MN category thresholds in legend"""
        result = format_lo_gan(sample_gan_data_mn, "An Giang")

        assert "3-5 kỳ" in result
        assert "6-8 kỳ" in result
        assert "9+ kỳ" in result


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

        gan_data = [
            {
                "number": "00",
                "gan_value": 15,
                "days_since_last": 15,
                "periods_since_last": 15,
                "last_seen_date": "01/10/2025",
                "max_cycle": 20,
                "is_daily": True,
                "category": "gan_thuong"
            }
        ]

        result1 = format_lo_2_so_stats(stats_2d)
        result2 = format_lo_3_so_stats(stats_3d)
        result3 = format_lo_gan(gan_data, "Test Province")

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

        empty_gan = []

        # Should not crash
        result1 = format_lo_2_so_stats(empty_stats)
        result2 = format_lo_3_so_stats(empty_stats)
        result3 = format_lo_gan(empty_gan, "Test Province")

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

        gan_data = [
            {
                "number": "00",
                "gan_value": 15,
                "days_since_last": 15,
                "periods_since_last": 15,
                "last_seen_date": "01/10/2025",
                "max_cycle": 20,
                "is_daily": True,
                "category": "gan_thuong"
            }
        ]

        result1 = format_lo_2_so_stats(stats)
        result2 = format_lo_3_so_stats(stats)
        result3 = format_lo_gan(gan_data, "Test Province")

        # Each should have at least one emoji
        assert any(char in result1 for char in "📊🎯📈")
        assert any(char in result2 for char in "📊🎯📈")
        assert any(char in result3 for char in "🔢📝🔴🟠🟢")

    def test_formatters_output_not_empty(self):
        """Test that formatters produce non-empty output"""
        stats = {
            "date": "2025-10-15",
            "province": "Test",
            "all_numbers": ["12"],
            "frequency": {"12": 1},
        }

        gan_data = [
            {
                "number": "00",
                "gan_value": 15,
                "days_since_last": 15,
                "periods_since_last": 15,
                "last_seen_date": "01/10/2025",
                "max_cycle": 20,
                "is_daily": True,
                "category": "gan_thuong"
            }
        ]

        result1 = format_lo_2_so_stats(stats)
        result2 = format_lo_3_so_stats(stats)
        result3 = format_lo_gan(gan_data, "Test Province")

        assert len(result1) > 50
        assert len(result2) > 50
        assert len(result3) > 50
