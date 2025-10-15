"""Unit tests for lottery service"""

import pytest
from unittest.mock import AsyncMock, Mock
from app.services.lottery_service import LotteryService


@pytest.fixture
def lottery_service():
    """Create lottery service instance"""
    return LotteryService()


@pytest.fixture
def sample_api_response():
    """Sample API response"""
    return {
        "success": True,
        "t": {
            "name": "Miền Bắc",
            "navCate": "MB",
            "issueList": [
                {
                    "turnNum": "2025-10-14",
                    "detail": '["12345","67890","11111,22222"]',
                }
            ],
        },
    }


@pytest.fixture
def sample_transformed_result():
    """Sample transformed result"""
    return {
        "date": "2025-10-14",
        "province": "Miền Bắc",
        "DB": ["12345"],
        "G1": ["67890"],
        "G2": ["11111", "22222"],
    }


class TestLotteryServiceInit:
    """Test LotteryService initialization"""

    def test_service_initialization(self):
        """Test service can be initialized"""
        service = LotteryService()
        assert service.api_client is not None
        assert service.transformer is not None

    def test_service_has_api_client(self, lottery_service):
        """Test service has api_client attribute"""
        assert hasattr(lottery_service, "api_client")

    def test_service_has_transformer(self, lottery_service):
        """Test service has transformer attribute"""
        assert hasattr(lottery_service, "transformer")


class TestGetLatestResult:
    """Test get_latest_result() method"""

    @pytest.mark.asyncio
    async def test_get_latest_result_success(
        self, lottery_service, sample_api_response, sample_transformed_result, mocker
    ):
        """Test successful fetch of latest result"""
        # Mock API client
        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )

        # Mock transformer
        lottery_service.transformer.transform_results = Mock(
            return_value=[sample_transformed_result]
        )

        result = await lottery_service.get_latest_result("MB")

        assert result is not None
        assert result["date"] == "2025-10-14"
        assert result["province"] == "Miền Bắc"
        assert "DB" in result

    @pytest.mark.asyncio
    async def test_get_latest_result_calls_api_with_limit_1(
        self, lottery_service, sample_api_response, sample_transformed_result, mocker
    ):
        """Test that API is called with limit=1 for latest result"""
        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )
        lottery_service.transformer.transform_results = Mock(
            return_value=[sample_transformed_result]
        )

        await lottery_service.get_latest_result("MB")

        # Verify API was called with limit=1
        lottery_service.api_client.fetch_results.assert_called_once_with("MB", limit=1)

    @pytest.mark.asyncio
    async def test_get_latest_result_api_failure_returns_mock(
        self, lottery_service, mocker
    ):
        """Test that mock data is returned when API fails"""
        # Mock API client to return None (failure)
        lottery_service.api_client.fetch_results = AsyncMock(return_value=None)

        result = await lottery_service.get_latest_result("MB")

        # Should return mock data, not None
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_latest_result_empty_results_returns_mock(
        self, lottery_service, sample_api_response, mocker
    ):
        """Test that mock data is returned when transformer returns empty list"""
        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )
        # Transformer returns empty list
        lottery_service.transformer.transform_results = Mock(return_value=[])

        result = await lottery_service.get_latest_result("MB")

        # Should return mock data
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_latest_result_exception_returns_mock(
        self, lottery_service, mocker
    ):
        """Test that mock data is returned when exception occurs"""
        # Mock API client to raise exception
        lottery_service.api_client.fetch_results = AsyncMock(
            side_effect=Exception("API Error")
        )

        result = await lottery_service.get_latest_result("MB")

        # Should return mock data, not raise exception
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_latest_result_multiple_results_returns_first(
        self, lottery_service, sample_api_response, mocker
    ):
        """Test that first result is returned when multiple exist"""
        results = [
            {"date": "2025-10-14", "province": "Test1"},
            {"date": "2025-10-13", "province": "Test2"},
            {"date": "2025-10-12", "province": "Test3"},
        ]

        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )
        lottery_service.transformer.transform_results = Mock(return_value=results)

        result = await lottery_service.get_latest_result("MB")

        # Should return first result (latest)
        assert result["date"] == "2025-10-14"
        assert result["province"] == "Test1"

    @pytest.mark.asyncio
    async def test_get_latest_result_different_provinces(
        self, lottery_service, sample_api_response, sample_transformed_result, mocker
    ):
        """Test fetching latest result for different provinces"""
        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )
        lottery_service.transformer.transform_results = Mock(
            return_value=[sample_transformed_result]
        )

        # Test MB
        result_mb = await lottery_service.get_latest_result("MB")
        assert result_mb is not None

        # Test TPHCM
        result_tphcm = await lottery_service.get_latest_result("TPHCM")
        assert result_tphcm is not None

        # Verify API was called for both
        assert lottery_service.api_client.fetch_results.call_count == 2


class TestGetHistory:
    """Test get_history() method"""

    @pytest.mark.asyncio
    async def test_get_history_success(
        self, lottery_service, sample_api_response, mocker
    ):
        """Test successful fetch of history"""
        results = [
            {"date": "2025-10-14", "province": "Test"},
            {"date": "2025-10-13", "province": "Test"},
        ]

        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )
        lottery_service.transformer.transform_results = Mock(return_value=results)

        history = await lottery_service.get_history("MB", limit=60)

        assert history is not None
        assert isinstance(history, list)
        assert len(history) == 2

    @pytest.mark.asyncio
    async def test_get_history_default_limit(self, lottery_service, mocker):
        """Test that default limit is 60"""
        lottery_service.api_client.fetch_results = AsyncMock(
            return_value={"success": True, "t": {"issueList": []}}
        )
        lottery_service.transformer.transform_results = Mock(return_value=[])

        await lottery_service.get_history("MB")

        # Verify API was called with limit=60 (default)
        lottery_service.api_client.fetch_results.assert_called_once_with("MB", 60)

    @pytest.mark.asyncio
    async def test_get_history_custom_limit(
        self, lottery_service, sample_api_response, mocker
    ):
        """Test get_history with custom limit"""
        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )
        lottery_service.transformer.transform_results = Mock(return_value=[])

        await lottery_service.get_history("MB", limit=30)

        # Verify API was called with custom limit
        lottery_service.api_client.fetch_results.assert_called_once_with("MB", 30)

    @pytest.mark.asyncio
    async def test_get_history_api_failure_returns_empty(
        self, lottery_service, mocker
    ):
        """Test that empty list is returned when API fails"""
        lottery_service.api_client.fetch_results = AsyncMock(return_value=None)

        history = await lottery_service.get_history("MB", limit=60)

        # Should return empty list, not None
        assert history == []

    @pytest.mark.asyncio
    async def test_get_history_exception_returns_empty(self, lottery_service, mocker):
        """Test that empty list is returned when exception occurs"""
        lottery_service.api_client.fetch_results = AsyncMock(
            side_effect=Exception("API Error")
        )

        history = await lottery_service.get_history("MB", limit=60)

        # Should return empty list, not raise exception
        assert history == []

    @pytest.mark.asyncio
    async def test_get_history_returns_all_results(
        self, lottery_service, sample_api_response, mocker
    ):
        """Test that all transformed results are returned"""
        results = [
            {"date": f"2025-10-{14-i:02d}", "province": "Test"} for i in range(10)
        ]

        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )
        lottery_service.transformer.transform_results = Mock(return_value=results)

        history = await lottery_service.get_history("MB", limit=60)

        assert len(history) == 10
        # Verify all dates are present
        for i, result in enumerate(history):
            assert result["date"] == f"2025-10-{14-i:02d}"

    @pytest.mark.asyncio
    async def test_get_history_different_provinces(
        self, lottery_service, sample_api_response, mocker
    ):
        """Test fetching history for different provinces"""
        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )
        lottery_service.transformer.transform_results = Mock(return_value=[])

        # Test different provinces
        await lottery_service.get_history("MB", limit=30)
        await lottery_service.get_history("TPHCM", limit=45)
        await lottery_service.get_history("GILA", limit=60)

        # Verify API was called 3 times with correct params
        assert lottery_service.api_client.fetch_results.call_count == 3
        calls = lottery_service.api_client.fetch_results.call_args_list
        assert calls[0][0] == ("MB", 30)
        assert calls[1][0] == ("TPHCM", 45)
        assert calls[2][0] == ("GILA", 60)


class TestClose:
    """Test close() method"""

    @pytest.mark.asyncio
    async def test_close_method_exists(self, lottery_service):
        """Test that close method exists and can be called"""
        # Should not raise exception
        await lottery_service.close()

    @pytest.mark.asyncio
    async def test_close_is_async(self, lottery_service):
        """Test that close is an async method"""
        import inspect

        assert inspect.iscoroutinefunction(lottery_service.close)


class TestServiceIntegration:
    """Test service integration and edge cases"""

    @pytest.mark.asyncio
    async def test_service_handles_all_regions(
        self, lottery_service, sample_api_response, sample_transformed_result, mocker
    ):
        """Test service handles MB, MN, MT regions"""
        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )
        lottery_service.transformer.transform_results = Mock(
            return_value=[sample_transformed_result]
        )

        # Test MB
        result_mb = await lottery_service.get_latest_result("MB")
        assert result_mb is not None

        # Test MN province
        result_mn = await lottery_service.get_latest_result("TPHCM")
        assert result_mn is not None

        # Test MT province
        result_mt = await lottery_service.get_latest_result("DANA")
        assert result_mt is not None

    @pytest.mark.asyncio
    async def test_service_logs_operations(self, lottery_service, mocker, caplog):
        """Test that service logs operations (info level)"""
        import logging

        caplog.set_level(logging.INFO)

        lottery_service.api_client.fetch_results = AsyncMock(return_value=None)

        await lottery_service.get_latest_result("MB")

        # Should have logged something about getting result
        assert len(caplog.records) > 0

    @pytest.mark.asyncio
    async def test_service_transformer_called_correctly(
        self, lottery_service, sample_api_response, mocker
    ):
        """Test that transformer is called with API response"""
        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )
        lottery_service.transformer.transform_results = Mock(
            return_value=[{"date": "2025-10-14"}]
        )

        await lottery_service.get_latest_result("MB")

        # Verify transformer was called with API response
        lottery_service.transformer.transform_results.assert_called_once_with(
            sample_api_response
        )

    @pytest.mark.asyncio
    async def test_service_reusable(
        self, lottery_service, sample_api_response, sample_transformed_result, mocker
    ):
        """Test that service can be reused multiple times"""
        lottery_service.api_client.fetch_results = AsyncMock(
            return_value=sample_api_response
        )
        lottery_service.transformer.transform_results = Mock(
            return_value=[sample_transformed_result]
        )

        # Call multiple times
        result1 = await lottery_service.get_latest_result("MB")
        result2 = await lottery_service.get_latest_result("TPHCM")
        history = await lottery_service.get_history("GILA", limit=30)

        # All should work
        assert result1 is not None
        assert result2 is not None
        assert isinstance(history, list)
