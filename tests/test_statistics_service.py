"""Unit tests for statistics service"""

import pytest
from app.services.statistics_service import StatisticsService


class TestStatisticsServiceInit:
    """Test StatisticsService initialization"""

    def test_service_initialization(self):
        """Test that service can be initialized"""
        service = StatisticsService()
        assert service is not None
        assert isinstance(service, StatisticsService)


class TestAnalyzeLo2So:
    """Test analyze_lo_2_so() method"""

    @pytest.fixture
    def service(self):
        return StatisticsService()

    @pytest.fixture
    def sample_mb_data(self):
        """Sample MB data with prizes"""
        return {
            "date": "2025-10-15",
            "province": "Miền Bắc",
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
    def sample_mn_data(self):
        """Sample MN/MT data with prizes"""
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

    def test_analyze_lo_2_so_mb(self, service, sample_mb_data):
        """Test 2-digit analysis for MB"""
        result = service.analyze_lo_2_so(sample_mb_data)

        assert "all_numbers" in result
        assert "frequency" in result
        assert "by_head" in result
        assert "by_tail" in result
        assert "date" in result
        assert "province" in result

        # Check that we extracted 2-digit numbers
        assert len(result["all_numbers"]) > 0
        assert isinstance(result["all_numbers"], list)

        # All numbers should be 2 digits
        for num in result["all_numbers"]:
            assert len(num) == 2
            assert num.isdigit()

    def test_analyze_lo_2_so_mn_mt(self, service, sample_mn_data):
        """Test 2-digit analysis for MN/MT"""
        result = service.analyze_lo_2_so(sample_mn_data)

        assert len(result["all_numbers"]) > 0
        assert "12" in result["all_numbers"]  # From G8
        assert result["date"] == "2025-10-15"
        assert result["province"] == "TP. Hồ Chí Minh"

    def test_frequency_calculation(self, service):
        """Test frequency counting"""
        data = {
            "date": "2025-10-15",
            "province": "Test",
            "DB": ["1111"],  # Last 2 digits: 11
            "G1": ["2211"],  # Last 2 digits: 11 (duplicate)
            "G2": ["3322"],  # Last 2 digits: 22
        }

        result = service.analyze_lo_2_so(data)

        # "11" should appear 2 times
        assert result["frequency"]["11"] == 2
        # "22" should appear 1 time
        assert result["frequency"]["22"] == 1

    def test_group_by_head_tail(self, service):
        """Test grouping by tens/units digit"""
        data = {
            "date": "2025-10-15",
            "province": "Test",
            "DB": ["1234"],  # 34
            "G1": ["3045"],  # 45
            "G2": ["3756"],  # 56
        }

        result = service.analyze_lo_2_so(data)

        # by_head: numbers grouped by tens digit
        assert "34" in result["by_head"][3]
        assert "45" in result["by_head"][4]
        assert "56" in result["by_head"][5]

        # by_tail: numbers grouped by units digit
        assert "34" in result["by_tail"][4]
        assert "45" in result["by_tail"][5]
        assert "56" in result["by_tail"][6]

    def test_empty_data(self, service):
        """Test with empty data"""
        data = {"date": "2025-10-15", "province": "Test"}

        result = service.analyze_lo_2_so(data)

        assert result["all_numbers"] == []
        assert result["frequency"] == {}
        assert len(result["by_head"]) == 10
        assert len(result["by_tail"]) == 10

    def test_prizes_nested_format(self, service):
        """Test with prizes nested under 'prizes' key"""
        data = {
            "date": "2025-10-15",
            "province": "Test",
            "prizes": {
                "DB": ["1234"],
                "G1": ["5678"],
            },
        }

        result = service.analyze_lo_2_so(data)

        assert "34" in result["all_numbers"]
        assert "78" in result["all_numbers"]


class TestAnalyzeLo3So:
    """Test analyze_lo_3_so() method"""

    @pytest.fixture
    def service(self):
        return StatisticsService()

    @pytest.fixture
    def sample_data(self):
        return {
            "date": "2025-10-15",
            "province": "Test",
            "DB": ["123456"],
            "G1": ["789012"],
            "G2": ["345678"],
        }

    def test_analyze_lo_3_so(self, service, sample_data):
        """Test 3-digit analysis"""
        result = service.analyze_lo_3_so(sample_data)

        assert "all_numbers" in result
        assert "frequency" in result
        assert "date" in result
        assert "province" in result

        # Check 3-digit extraction
        assert "456" in result["all_numbers"]
        assert "012" in result["all_numbers"]
        assert "678" in result["all_numbers"]

        # All numbers should be 3 digits
        for num in result["all_numbers"]:
            assert len(num) == 3
            assert num.isdigit()

    def test_frequency_3_digit(self, service):
        """Test 3-digit frequency calculation"""
        data = {
            "date": "2025-10-15",
            "province": "Test",
            "DB": ["123456"],  # 456
            "G1": ["789456"],  # 456 (duplicate)
            "G2": ["111222"],  # 222
        }

        result = service.analyze_lo_3_so(data)

        assert result["frequency"]["456"] == 2
        assert result["frequency"]["222"] == 1

    def test_empty_data_3digit(self, service):
        """Test with empty data for 3-digit"""
        data = {"date": "2025-10-15", "province": "Test"}

        result = service.analyze_lo_3_so(data)

        assert result["all_numbers"] == []
        assert result["frequency"] == {}


class TestGetFrequencyStats:
    """Test get_frequency_stats() method"""

    @pytest.fixture
    def service(self):
        return StatisticsService(use_database=False)

    @pytest.mark.asyncio
    async def test_frequency_stats_returns_dict(self, service):
        """Test that frequency stats returns dict"""
        result = await service.get_frequency_stats("MB", days=30)

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_frequency_stats_mock_data(self, service):
        """Test that mock data is reasonable"""
        result = await service.get_frequency_stats("TPHCM", days=30)

        # Should have some data
        assert len(result) > 0

        # Values should be reasonable counts
        for num, count in result.items():
            assert count > 0
            assert count < 100  # Mock should be reasonable


class TestFormatFrequencyTable:
    """Test format_frequency_table() method"""

    @pytest.fixture
    def service(self):
        return StatisticsService()

    def test_format_frequency_table(self, service):
        """Test formatting frequency data"""
        freq_data = {"12": 5, "34": 3, "56": 8, "78": 2}

        result = service.format_frequency_table(freq_data)

        assert isinstance(result, str)
        assert "56" in result  # Highest frequency
        assert "8 lần" in result
        assert "<b>" in result  # HTML formatting

    def test_format_frequency_table_empty(self, service):
        """Test with empty frequency data"""
        result = service.format_frequency_table({})

        assert "Không có dữ liệu" in result

    def test_format_frequency_table_sorted(self, service):
        """Test that results are sorted by frequency"""
        freq_data = {"12": 5, "34": 10, "56": 3}

        result = service.format_frequency_table(freq_data)

        # 34 (10) should appear before 12 (5)
        pos_34 = result.find("34")
        pos_12 = result.find("12")

        assert pos_34 < pos_12


class TestStatisticsServiceIntegration:
    """Integration tests for StatisticsService"""

    def test_service_handles_various_data_formats(self):
        """Test that service handles both flat and nested data"""
        service = StatisticsService()

        # Flat format
        flat_data = {
            "date": "2025-10-15",
            "province": "Test",
            "DB": ["12345"],
        }

        # Nested format
        nested_data = {
            "date": "2025-10-15",
            "province": "Test",
            "prizes": {"DB": ["12345"]},
        }

        flat_result = service.analyze_lo_2_so(flat_data)
        nested_result = service.analyze_lo_2_so(nested_data)

        # Should produce same results
        assert flat_result["all_numbers"] == nested_result["all_numbers"]
        assert flat_result["frequency"] == nested_result["frequency"]

    def test_service_doesnt_crash_on_bad_data(self):
        """Test that service handles invalid data gracefully"""
        service = StatisticsService()

        # Missing keys
        result1 = service.analyze_lo_2_so({})
        assert "all_numbers" in result1

        # Invalid prize values
        result2 = service.analyze_lo_2_so({"DB": ["invalid"]})
        assert isinstance(result2, dict)

        # None values
        result3 = service.analyze_lo_2_so({"DB": None})
        assert isinstance(result3, dict)
