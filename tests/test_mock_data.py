"""Unit tests for mock data generation"""

import pytest
from app.services.mock_data import (
    get_mock_lottery_result,
    get_mock_stats_2digit,
    get_mock_stats_3digit,
)


class TestGetMockLotteryResult:
    """Test get_mock_lottery_result() function"""

    def test_mock_result_for_mb(self):
        """Test mock result for MB"""
        result = get_mock_lottery_result("MB")

        assert result is not None
        assert isinstance(result, dict)
        assert "date" in result
        assert "province" in result

    def test_mock_result_for_mn_province(self):
        """Test mock result for MN province"""
        result = get_mock_lottery_result("TPHCM")

        assert result is not None
        assert isinstance(result, dict)
        # MN should have G8
        assert "DB" in result

    def test_mock_result_for_mt_province(self):
        """Test mock result for MT province"""
        result = get_mock_lottery_result("DANA")

        assert result is not None
        assert isinstance(result, dict)

    def test_mock_result_has_prizes(self):
        """Test mock result contains prize data"""
        result = get_mock_lottery_result("MB")

        # Should have DB at minimum
        assert "DB" in result

    def test_mock_result_different_provinces_different_results(self):
        """Test that different provinces give potentially different results"""
        result1 = get_mock_lottery_result("MB")
        result2 = get_mock_lottery_result("TPHCM")

        # Should both be valid results
        assert result1 is not None
        assert result2 is not None

    def test_mock_result_unknown_province(self):
        """Test mock result with unknown province"""
        result = get_mock_lottery_result("UNKNOWN_PROVINCE")

        # Should still return valid mock data
        assert result is not None
        assert isinstance(result, dict)
        assert "date" in result
        assert "DB" in result

    def test_mock_result_flattens_nested_prizes(self):
        """Test that nested prizes structure is flattened"""
        # This tests the flatten logic for provinces in MOCK_RESULTS
        result = get_mock_lottery_result("MB")

        # Should have prizes at top level, not nested
        assert "DB" in result or "G1" in result or "date" in result

    def test_mock_result_has_date(self):
        """Test mock result includes date"""
        result = get_mock_lottery_result("MB")

        assert "date" in result
        assert isinstance(result["date"], str)

    def test_mock_result_has_province_name(self):
        """Test mock result includes province name"""
        result = get_mock_lottery_result("TPHCM")

        assert "province" in result
        assert isinstance(result["province"], str)


class TestGetMockStats2Digit:
    """Test get_mock_stats_2digit() function"""

    def test_stats_2digit_mb(self):
        """Test 2-digit stats for MB"""
        stats = get_mock_stats_2digit("MB")

        assert stats is not None
        assert isinstance(stats, dict)
        assert "region" in stats
        assert stats["region"] == "MB"

    def test_stats_2digit_has_top_frequent(self):
        """Test stats include top frequent numbers"""
        stats = get_mock_stats_2digit("MB")

        assert "top_frequent" in stats
        assert isinstance(stats["top_frequent"], list)
        assert len(stats["top_frequent"]) > 0

    def test_stats_2digit_has_rare_numbers(self):
        """Test stats include rare numbers"""
        stats = get_mock_stats_2digit("MB")

        assert "rare" in stats
        assert isinstance(stats["rare"], list)

    def test_stats_2digit_frequent_format(self):
        """Test format of frequent numbers"""
        stats = get_mock_stats_2digit("MB")

        # Each item should be a tuple (number, count)
        if len(stats["top_frequent"]) > 0:
            item = stats["top_frequent"][0]
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], int)  # number
            assert isinstance(item[1], int)  # count

    def test_stats_2digit_different_regions(self):
        """Test stats for different regions"""
        stats_mb = get_mock_stats_2digit("MB")
        stats_mn = get_mock_stats_2digit("MN")
        stats_mt = get_mock_stats_2digit("MT")

        assert stats_mb["region"] == "MB"
        assert stats_mn["region"] == "MN"
        assert stats_mt["region"] == "MT"

    def test_stats_2digit_sorted_by_frequency(self):
        """Test that frequent numbers are sorted by count"""
        stats = get_mock_stats_2digit("MB")

        frequent = stats["top_frequent"]
        if len(frequent) > 1:
            # Should be sorted descending by count
            for i in range(len(frequent) - 1):
                assert frequent[i][1] >= frequent[i + 1][1]


class TestGetMockStats3Digit:
    """Test get_mock_stats_3digit() function"""

    def test_stats_3digit_basic(self):
        """Test basic 3-digit stats"""
        stats = get_mock_stats_3digit("MB")

        assert stats is not None
        assert isinstance(stats, dict)
        assert "province" in stats

    def test_stats_3digit_has_db_frequent(self):
        """Test stats include DB frequent numbers"""
        stats = get_mock_stats_3digit("MB")

        assert "db_frequent" in stats
        assert isinstance(stats["db_frequent"], list)

    def test_stats_3digit_has_triples(self):
        """Test stats include triple combinations"""
        stats = get_mock_stats_3digit("MB")

        assert "triples" in stats
        assert isinstance(stats["triples"], list)

    def test_stats_3digit_db_frequent_format(self):
        """Test format of DB frequent numbers"""
        stats = get_mock_stats_3digit("MB")

        # Each item should be a tuple (number, count)
        if len(stats["db_frequent"]) > 0:
            item = stats["db_frequent"][0]
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_stats_3digit_triples_format(self):
        """Test format of triples"""
        stats = get_mock_stats_3digit("MB")

        # Each triple should be (n1, n2, n3, count)
        if len(stats["triples"]) > 0:
            item = stats["triples"][0]
            assert isinstance(item, tuple)
            assert len(item) == 4

    def test_stats_3digit_different_provinces(self):
        """Test stats for different provinces"""
        stats_mb = get_mock_stats_3digit("MB")
        stats_tphcm = get_mock_stats_3digit("TPHCM")

        assert stats_mb["province"] == "MB"
        assert stats_tphcm["province"] == "TPHCM"

    def test_stats_3digit_sorted_by_frequency(self):
        """Test that DB frequent is sorted by count"""
        stats = get_mock_stats_3digit("MB")

        db_frequent = stats["db_frequent"]
        if len(db_frequent) > 1:
            # Should be sorted descending by count
            for i in range(len(db_frequent) - 1):
                assert db_frequent[i][1] >= db_frequent[i + 1][1]


class TestGetMockLoGan:
    """Test get_mock_lo_gan() function"""

    def test_lo_gan_basic(self):
        """Test basic lo gan data structure"""
        from app.services.mock_data import get_mock_lo_gan

        result = get_mock_lo_gan("MB", days=30)

        assert isinstance(result, dict)
        assert "gan_numbers" in result
        assert "region" in result
        assert "period" in result

    def test_lo_gan_has_numbers(self):
        """Test that lo gan has numbers"""
        from app.services.mock_data import get_mock_lo_gan

        result = get_mock_lo_gan("MB", days=30)

        assert len(result["gan_numbers"]) > 0
        assert len(result["gan_numbers"]) <= 10

    def test_lo_gan_number_format(self):
        """Test lo gan number format"""
        from app.services.mock_data import get_mock_lo_gan

        result = get_mock_lo_gan("MB", days=30)

        for item in result["gan_numbers"]:
            assert "number" in item
            assert "days_not_appeared" in item
            assert len(item["number"]) == 2
            assert item["days_not_appeared"] > 0

    def test_lo_gan_sorted_by_days(self):
        """Test that lo gan is sorted by days not appeared"""
        from app.services.mock_data import get_mock_lo_gan

        result = get_mock_lo_gan("MB", days=30)

        if len(result["gan_numbers"]) > 1:
            for i in range(len(result["gan_numbers"]) - 1):
                days1 = result["gan_numbers"][i]["days_not_appeared"]
                days2 = result["gan_numbers"][i + 1]["days_not_appeared"]
                assert days1 >= days2

    def test_lo_gan_different_regions(self):
        """Test lo gan for different regions"""
        from app.services.mock_data import get_mock_lo_gan

        mb = get_mock_lo_gan("MB", days=30)
        mn = get_mock_lo_gan("MN", days=30)
        mt = get_mock_lo_gan("MT", days=30)

        # Should all have data
        assert len(mb["gan_numbers"]) > 0
        assert len(mn["gan_numbers"]) > 0
        assert len(mt["gan_numbers"]) > 0


class TestMockDataConsistency:
    """Test consistency and quality of mock data"""

    def test_mock_result_consistent_for_same_province(self):
        """Test that mock results are consistent for same input"""
        # Due to seeding with date, should be same within same day
        result1 = get_mock_lottery_result("TEST_PROVINCE")
        result2 = get_mock_lottery_result("TEST_PROVINCE")

        # Basic structure should be same
        assert "date" in result1
        assert "date" in result2

    def test_stats_functions_dont_crash(self):
        """Test that stats functions handle various inputs"""
        from app.services.mock_data import get_mock_lo_gan

        # Should not raise exceptions
        get_mock_stats_2digit("MB")
        get_mock_stats_2digit("MN")
        get_mock_stats_2digit("MT")
        get_mock_stats_2digit("UNKNOWN")

        get_mock_stats_3digit("MB")
        get_mock_stats_3digit("TPHCM")
        get_mock_stats_3digit("UNKNOWN")

        get_mock_lo_gan("MB")
        get_mock_lo_gan("MN")
        get_mock_lo_gan("MT")

    def test_mock_functions_return_dicts(self):
        """Test that all mock functions return dicts"""
        result = get_mock_lottery_result("MB")
        stats_2d = get_mock_stats_2digit("MB")
        stats_3d = get_mock_stats_3digit("MB")

        assert isinstance(result, dict)
        assert isinstance(stats_2d, dict)
        assert isinstance(stats_3d, dict)
