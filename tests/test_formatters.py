"""Unit tests for lottery result formatters"""

import pytest
from app.ui.formatters import (
    format_result_mb_full,
    format_result_mn_mt_full,
    format_lo_2_so_mb,
    format_lo_2_so_mn_mt,
    format_lo_3_so_mb,
    format_lo_3_so_mn_mt,
    format_dau_lo,
    format_duoi_lo,
    format_lottery_result,
)


@pytest.fixture
def sample_mb_data():
    """Sample Miền Bắc lottery data (27 prizes)"""
    return {
        "date": "2025-10-14",
        "DB": ["12345"],
        "G1": ["67890"],
        "G2": ["11111", "22222"],
        "G3": ["33333", "44444", "55555", "66666", "77777", "88888"],
        "G4": ["1234", "5678", "9012", "3456"],
        "G5": ["1111", "2222", "3333", "4444", "5555", "6666"],
        "G6": ["111", "222", "333"],
        "G7": ["11", "22", "33", "44"],
    }


@pytest.fixture
def sample_mb_data_with_prizes_key():
    """Sample MB data with prizes nested under 'prizes' key"""
    return {
        "date": "2025-10-14",
        "prizes": {
            "DB": ["12345"],
            "G1": ["67890"],
            "G2": ["11111", "22222"],
            "G3": ["33333", "44444", "55555", "66666", "77777", "88888"],
            "G4": ["1234", "5678", "9012", "3456"],
            "G5": ["1111", "2222", "3333", "4444", "5555", "6666"],
            "G6": ["111", "222", "333"],
            "G7": ["11", "22", "33", "44"],
        },
    }


@pytest.fixture
def sample_mn_mt_data():
    """Sample Miền Nam/Trung lottery data (18 prizes)"""
    return {
        "date": "2025-10-15",
        "province": "TP. Hồ Chí Minh",
        "G8": ["12"],
        "G7": ["123"],
        "G6": ["1234", "5678", "9012"],
        "G5": ["4567"],
        "G4": ["12345", "67890", "11111", "22222", "33333", "44444", "55555"],
        "G3": ["123456", "789012"],
        "G2": ["234567"],
        "G1": ["890123"],
        "DB": ["456789"],
    }


@pytest.fixture
def sample_mn_mt_data_with_prizes_key():
    """Sample MN/MT data with prizes nested under 'prizes' key"""
    return {
        "date": "2025-10-15",
        "province": "TP. Hồ Chí Minh",
        "prizes": {
            "G8": ["12"],
            "G7": ["123"],
            "G6": ["1234", "5678", "9012"],
            "G5": ["4567"],
            "G4": ["12345", "67890", "11111", "22222", "33333", "44444", "55555"],
            "G3": ["123456", "789012"],
            "G2": ["234567"],
            "G1": ["890123"],
            "DB": ["456789"],
        },
    }


@pytest.fixture
def empty_data():
    """Empty lottery data"""
    return {"date": "2025-10-14"}


class TestFormatResultMBFull:
    """Test format_result_mb_full() function"""

    def test_format_with_valid_data(self, sample_mb_data):
        """Test formatting with valid MB data"""
        result = format_result_mb_full(sample_mb_data)

        assert "🎰 <b>KẾT QUẢ XỔ SỐ MIỀN BẮC 27 GIẢI</b>" in result
        assert "📅 Ngày: 2025-10-14" in result
        assert "🏆 <b>Đặc Biệt:</b> 12345" in result
        assert "🥇 <b>Giải Nhất:</b> 67890" in result
        assert "🥈 <b>Giải Nhì:</b> 11111,22222" in result
        assert "🥉 <b>Giải Ba:</b>" in result
        assert "33333" in result
        assert "🎪 <b>Giải Bảy:</b> 11,22,33,44" in result

    def test_format_with_prizes_key(self, sample_mb_data_with_prizes_key):
        """Test formatting with data using 'prizes' key"""
        result = format_result_mb_full(sample_mb_data_with_prizes_key)

        assert "🏆 <b>Đặc Biệt:</b> 12345" in result
        assert "🥇 <b>Giải Nhất:</b> 67890" in result
        assert "📅 Ngày: 2025-10-14" in result

    def test_format_with_empty_data(self, empty_data):
        """Test formatting with empty prize data"""
        result = format_result_mb_full(empty_data)

        assert "🎰 <b>KẾT QUẢ XỔ SỐ MIỀN BẮC 27 GIẢI</b>" in result
        assert "📅 Ngày: 2025-10-14" in result
        # Should not contain any prize values
        assert "🏆 <b>Đặc Biệt:</b>" not in result

    def test_format_with_missing_date(self):
        """Test formatting with missing date"""
        data = {"DB": ["12345"]}
        result = format_result_mb_full(data)

        assert "📅 Ngày: " in result
        assert "🏆 <b>Đặc Biệt:</b> 12345" in result

    def test_format_with_partial_prizes(self):
        """Test formatting with only some prizes"""
        data = {
            "date": "2025-10-14",
            "DB": ["12345"],
            "G1": ["67890"],
            # Missing other prizes
        }
        result = format_result_mb_full(data)

        assert "🏆 <b>Đặc Biệt:</b> 12345" in result
        assert "🥇 <b>Giải Nhất:</b> 67890" in result
        # Should not contain missing prizes
        assert "🥈 <b>Giải Nhì:</b>" not in result


class TestFormatResultMNMTFull:
    """Test format_result_mn_mt_full() function"""

    def test_format_with_valid_data(self, sample_mn_mt_data):
        """Test formatting with valid MN/MT data"""
        result = format_result_mn_mt_full(sample_mn_mt_data)

        assert "🎰 <b>KẾT QUẢ XỔ SỐ TP. HỒ CHÍ MINH 18 GIẢI</b>" in result
        assert "📅 Ngày: 2025-10-15" in result
        assert "🎊 <b>Giải Tám:</b> 12" in result
        assert "🎪 <b>Giải Bảy:</b> 123" in result
        assert "🏆 <b>Đặc Biệt:</b> 456789" in result

    def test_format_with_prizes_key(self, sample_mn_mt_data_with_prizes_key):
        """Test formatting with data using 'prizes' key"""
        result = format_result_mn_mt_full(sample_mn_mt_data_with_prizes_key)

        assert "🏆 <b>Đặc Biệt:</b> 456789" in result
        assert "🎊 <b>Giải Tám:</b> 12" in result

    def test_format_with_missing_province(self):
        """Test formatting with missing province name"""
        data = {
            "date": "2025-10-15",
            "DB": ["456789"],
        }
        result = format_result_mn_mt_full(data)

        # Should use default province name
        assert "🎰 <b>KẾT QUẢ XỔ SỐ MIỀN NAM 18 GIẢI</b>" in result

    def test_format_with_empty_data(self, empty_data):
        """Test formatting with empty prize data"""
        result = format_result_mn_mt_full(empty_data)

        assert "🎰 <b>KẾT QUẢ XỔ SỐ MIỀN NAM 18 GIẢI</b>" in result
        assert "📅 Ngày: 2025-10-14" in result

    def test_format_province_name_uppercase(self):
        """Test that province name is converted to uppercase"""
        data = {
            "date": "2025-10-15",
            "province": "Đà Nẵng",
            "DB": ["123456"],
        }
        result = format_result_mn_mt_full(data)

        assert "ĐÀ NẴNG" in result


class TestFormatLo2SoMB:
    """Test format_lo_2_so_mb() function"""

    def test_format_with_valid_data(self, sample_mb_data):
        """Test Lô 2 số MB formatting"""
        result = format_lo_2_so_mb(sample_mb_data)

        assert "🎯 <b>KẾT QUẢ LÔ 2 SỐ</b>" in result
        assert "📅 Ngày: 2025-10-14" in result
        # Last 2 digits of DB: 12345 -> 45
        assert "🏆 <b>ĐB:</b> 45" in result
        # Last 2 digits of G1: 67890 -> 90
        assert "🥇 <b>G1:</b> 90" in result
        # G7 should remain as-is (already 2 digits)
        assert "🎪 <b>G7:</b> 11 22 33 44" in result

    def test_format_lo2_extracts_last_2_digits(self):
        """Test that Lô 2 số correctly extracts last 2 digits"""
        data = {
            "date": "2025-10-14",
            "DB": ["12345"],  # -> 45
            "G2": ["11111", "22222"],  # -> 11, 22
        }
        result = format_lo_2_so_mb(data)

        assert "45" in result
        assert "11 22" in result

    def test_format_with_prizes_key(self, sample_mb_data_with_prizes_key):
        """Test Lô 2 số with 'prizes' key"""
        result = format_lo_2_so_mb(sample_mb_data_with_prizes_key)

        assert "🏆 <b>ĐB:</b> 45" in result
        assert "🥇 <b>G1:</b> 90" in result


class TestFormatLo2SoMNMT:
    """Test format_lo_2_so_mn_mt() function"""

    def test_format_with_valid_data(self, sample_mn_mt_data):
        """Test Lô 2 số MN/MT formatting"""
        result = format_lo_2_so_mn_mt(sample_mn_mt_data)

        assert "🎯 <b>KẾT QUẢ LÔ 2 SỐ</b>" in result
        assert "📅 Ngày: 2025-10-15" in result
        # G8: 12 -> 12 (already 2 digits)
        assert "🎊 <b>G8:</b> 12" in result
        # G7: 123 -> 23
        assert "🎪 <b>G7:</b> 23" in result
        # DB: 456789 -> 89
        assert "🏆 <b>ĐB:</b> 89" in result

    def test_format_order_g8_to_db(self, sample_mn_mt_data):
        """Test that prizes are formatted in order G8 → ĐB"""
        result = format_lo_2_so_mn_mt(sample_mn_mt_data)

        # Check order by finding indices
        g8_idx = result.find("G8")
        g7_idx = result.find("G7")
        db_idx = result.find("ĐB")

        assert g8_idx < g7_idx < db_idx


class TestFormatLo3SoMB:
    """Test format_lo_3_so_mb() function"""

    def test_format_with_valid_data(self, sample_mb_data):
        """Test Lô 3 số MB formatting"""
        result = format_lo_3_so_mb(sample_mb_data)

        assert "🎯 <b>KẾT QUẢ LÔ 3 SỐ</b>" in result
        # Last 3 digits of DB: 12345 -> 345
        assert "🏆 <b>ĐB:</b> 345" in result
        # Last 3 digits of G1: 67890 -> 890
        assert "🥇 <b>G1:</b> 890" in result
        # G6 should remain as-is (already 3 digits)
        assert "🎗️ <b>G6:</b> 111 222 333" in result
        # G7 should show "không có"
        assert "🎪 <b>G7:</b> không có" in result

    def test_format_g7_not_available(self, sample_mb_data):
        """Test that G7 shows 'không có' for Lô 3 số MB"""
        result = format_lo_3_so_mb(sample_mb_data)

        assert "🎪 <b>G7:</b> không có" in result


class TestFormatLo3SoMNMT:
    """Test format_lo_3_so_mn_mt() function"""

    def test_format_with_valid_data(self, sample_mn_mt_data):
        """Test Lô 3 số MN/MT formatting"""
        result = format_lo_3_so_mn_mt(sample_mn_mt_data)

        assert "🎯 <b>KẾT QUẢ LÔ 3 SỐ</b>" in result
        # G8 should show "Không có"
        assert "🎊 <b>G8:</b> Không có" in result
        # G7: 123 -> 123 (already 3 digits)
        assert "🎪 <b>G7:</b> 123" in result
        # DB: 456789 -> 789
        assert "🏆 <b>ĐB:</b> 789" in result

    def test_format_g8_not_available(self, sample_mn_mt_data):
        """Test that G8 shows 'Không có' for Lô 3 số MN/MT"""
        result = format_lo_3_so_mn_mt(sample_mn_mt_data)

        assert "🎊 <b>G8:</b> Không có" in result


class TestFormatDauLo:
    """Test format_dau_lo() function"""

    def test_format_with_valid_data(self):
        """Test Đầu Lô formatting"""
        data = {
            "date": "2025-10-14",
            "DB": ["12345"],  # -> 45 (đầu 4, đuôi 5)
            "G1": ["67890"],  # -> 90 (đầu 9, đuôi 0)
            "G2": ["11111", "22222"],  # -> 11, 22
        }
        result = format_dau_lo(data)

        assert "📊 <b>THỐNG KÊ ĐẦU LÔ</b>" in result
        assert "📅 Ngày: 2025-10-14" in result
        # Đầu 1 should have: 1 (from 11)
        assert "🔢 <b>1</b> : 1" in result
        # Đầu 2 should have: 2 (from 22)
        assert "🔢 <b>2</b> : 2" in result
        # Đầu 4 should have: 5 (from 45)
        assert "🔢 <b>4</b> : 5" in result
        # Đầu 9 should have: 0 (from 90)
        assert "🔢 <b>9</b> : 0" in result

    def test_format_groups_by_first_digit(self):
        """Test that numbers are grouped by first digit"""
        data = {
            "date": "2025-10-14",
            "DB": ["10", "11", "12"],  # All start with 1
            "G1": ["20", "21"],  # All start with 2
        }
        result = format_dau_lo(data)

        # Đầu 1 should have all second digits: 0, 1, 2
        assert "🔢 <b>1</b> : 0,1,2" in result
        # Đầu 2 should have: 0, 1
        assert "🔢 <b>2</b> : 0,1" in result

    def test_format_with_no_numbers_for_digit(self):
        """Test formatting when some digits have no numbers"""
        data = {
            "date": "2025-10-14",
            "DB": ["12"],  # Only đầu 1
        }
        result = format_dau_lo(data)

        # Đầu 1 has value
        assert "🔢 <b>1</b> : 2" in result
        # Other đầu should show "không có"
        assert "🔢 <b>0</b> : không có" in result
        assert "🔢 <b>3</b> : không có" in result

    def test_format_with_prizes_key(self):
        """Test with prizes nested under key"""
        data = {
            "date": "2025-10-14",
            "prizes": {"DB": ["12"], "G1": ["34"]},
        }
        result = format_dau_lo(data)

        assert "🔢 <b>1</b> : 2" in result
        assert "🔢 <b>3</b> : 4" in result


class TestFormatDuoiLo:
    """Test format_duoi_lo() function"""

    def test_format_with_valid_data(self):
        """Test Đuôi Lô formatting"""
        data = {
            "date": "2025-10-14",
            "DB": ["12345"],  # -> 45 (đầu 4, đuôi 5)
            "G1": ["67890"],  # -> 90 (đầu 9, đuôi 0)
            "G2": ["11111", "22222"],  # -> 11, 22
        }
        result = format_duoi_lo(data)

        assert "📊 <b>THỐNG KÊ ĐUÔI LÔ</b>" in result
        assert "📅 Ngày: 2025-10-14" in result
        # Đuôi 0 should have: 9 (from 90)
        assert "🔢 <b>0</b> : 9" in result
        # Đuôi 1 should have: 1 (from 11)
        assert "🔢 <b>1</b> : 1" in result
        # Đuôi 2 should have: 2 (from 22)
        assert "🔢 <b>2</b> : 2" in result
        # Đuôi 5 should have: 4 (from 45)
        assert "🔢 <b>5</b> : 4" in result

    def test_format_groups_by_last_digit(self):
        """Test that numbers are grouped by last digit"""
        data = {
            "date": "2025-10-14",
            "DB": ["10", "20", "30"],  # All end with 0
            "G1": ["11", "21"],  # All end with 1
        }
        result = format_duoi_lo(data)

        # Đuôi 0 should have all first digits: 1, 2, 3
        assert "🔢 <b>0</b> : 1,2,3" in result
        # Đuôi 1 should have: 1, 2
        assert "🔢 <b>1</b> : 1,2" in result

    def test_format_with_no_numbers_for_digit(self):
        """Test formatting when some digits have no numbers"""
        data = {
            "date": "2025-10-14",
            "DB": ["12"],  # Only đuôi 2
        }
        result = format_duoi_lo(data)

        # Đuôi 2 has value
        assert "🔢 <b>2</b> : 1" in result
        # Other đuôi should show "không có"
        assert "🔢 <b>0</b> : không có" in result
        assert "🔢 <b>5</b> : không có" in result


class TestFormatLotteryResult:
    """Test format_lottery_result() legacy function"""

    def test_format_mb_region(self, sample_mb_data):
        """Test legacy function with MB region"""
        result = format_lottery_result(sample_mb_data, region="MB")

        # Should call format_result_mb_full
        assert "🎰 <b>KẾT QUẢ XỔ SỐ MIỀN BẮC 27 GIẢI</b>" in result
        assert "🏆 <b>Đặc Biệt:</b> 12345" in result

    def test_format_mn_region(self, sample_mn_mt_data):
        """Test legacy function with MN region"""
        result = format_lottery_result(sample_mn_mt_data, region="MN")

        # Should call format_result_mn_mt_full
        assert "🎰 <b>KẾT QUẢ XỔ SỐ TP. HỒ CHÍ MINH 18 GIẢI</b>" in result

    def test_format_mt_region(self, sample_mn_mt_data):
        """Test legacy function with MT region"""
        result = format_lottery_result(sample_mn_mt_data, region="MT")

        # Should call format_result_mn_mt_full (same as MN)
        assert "🎰 <b>KẾT QUẢ XỔ SỐ TP. HỒ CHÍ MINH 18 GIẢI</b>" in result

    def test_format_default_region(self, sample_mn_mt_data):
        """Test legacy function with default region (should be MN)"""
        result = format_lottery_result(sample_mn_mt_data)

        # Should call format_result_mn_mt_full by default
        assert "🎰 <b>KẾT QUẢ XỔ SỐ TP. HỒ CHÍ MINH 18 GIẢI</b>" in result
