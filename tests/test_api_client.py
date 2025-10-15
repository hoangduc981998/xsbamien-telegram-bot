"""Unit tests for API client"""

import pytest
import httpx
from unittest.mock import Mock, AsyncMock
from app.services.api.client import MU88APIClient


@pytest.fixture
def api_client():
    """Create API client instance"""
    return MU88APIClient(timeout=10.0)


@pytest.fixture
def sample_api_response():
    """Sample successful API response"""
    return {
        "success": True,
        "msg": "Success",
        "t": {
            "name": "Miền Bắc",
            "navCate": "MB",
            "issueList": [
                {
                    "turnNum": "2025-10-14",
                    "detail": '["12345","67890"]',
                }
            ],
        },
    }


class TestMU88APIClient:
    """Test MU88APIClient class"""

    def test_client_initialization(self):
        """Test client can be initialized"""
        client = MU88APIClient()
        assert client.timeout == 30.0  # Default timeout

    def test_client_custom_timeout(self):
        """Test client with custom timeout"""
        client = MU88APIClient(timeout=60.0)
        assert client.timeout == 60.0

    def test_base_url_is_set(self):
        """Test that BASE_URL is set correctly"""
        assert MU88APIClient.BASE_URL == "https://mu88.live/api/front/open/lottery/history/list/game"

    def test_province_map_contains_mb(self):
        """Test province map contains MB"""
        assert "MB" in MU88APIClient.PROVINCE_MAP
        assert MU88APIClient.PROVINCE_MAP["MB"] == "miba"

    def test_province_map_contains_mn_provinces(self):
        """Test province map contains MN provinces"""
        assert "TPHCM" in MU88APIClient.PROVINCE_MAP
        assert MU88APIClient.PROVINCE_MAP["TPHCM"] == "tphc"
        assert "BALI" in MU88APIClient.PROVINCE_MAP
        assert "VILO" in MU88APIClient.PROVINCE_MAP

    def test_province_map_contains_mt_provinces(self):
        """Test province map contains MT provinces"""
        assert "DANA" in MU88APIClient.PROVINCE_MAP
        assert "GILA" in MU88APIClient.PROVINCE_MAP
        assert "KHHO" in MU88APIClient.PROVINCE_MAP


class TestFetchResults:
    """Test fetch_results() method"""

    @pytest.mark.asyncio
    async def test_fetch_results_success(self, api_client, sample_api_response, mocker):
        """Test successful API fetch"""
        # Mock httpx.AsyncClient
        mock_response = Mock()
        mock_response.json.return_value = sample_api_response
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        result = await api_client.fetch_results("MB", limit=1)

        assert result is not None
        assert result["success"] is True
        assert "t" in result

    @pytest.mark.asyncio
    async def test_fetch_results_converts_province_code(self, api_client, mocker):
        """Test that province code is converted to game code"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        await api_client.fetch_results("TPHCM", limit=1)

        # Verify get was called with correct params
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params["gameCode"] == "tphc"  # TPHCM -> tphc

    @pytest.mark.asyncio
    async def test_fetch_results_with_limit(self, api_client, mocker):
        """Test that limit parameter is passed correctly"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        await api_client.fetch_results("MB", limit=60)

        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params["limitNum"] == 60

    @pytest.mark.asyncio
    async def test_fetch_results_api_error(self, api_client, mocker):
        """Test handling of API error response"""
        error_response = {"success": False, "msg": "Error occurred"}

        mock_response = Mock()
        mock_response.json.return_value = error_response
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        result = await api_client.fetch_results("MB", limit=1)

        # Should return None when API returns error
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_results_http_error(self, api_client, mocker):
        """Test handling of HTTP errors"""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        result = await api_client.fetch_results("MB", limit=1)

        # Should return None on HTTP error
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_results_timeout(self, api_client, mocker):
        """Test handling of timeout errors"""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        result = await api_client.fetch_results("MB", limit=1)

        # Should return None on timeout
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_results_generic_exception(self, api_client, mocker):
        """Test handling of generic exceptions"""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(side_effect=Exception("Unexpected error"))

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        result = await api_client.fetch_results("MB", limit=1)

        # Should return None on any exception
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_results_uses_correct_url(self, api_client, mocker):
        """Test that correct base URL is used"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        await api_client.fetch_results("MB", limit=1)

        # Verify correct URL is used
        call_args = mock_client.get.call_args
        assert call_args[0][0] == MU88APIClient.BASE_URL

    @pytest.mark.asyncio
    async def test_fetch_results_unknown_province(self, api_client, mocker):
        """Test fetching with unknown province code"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # Unknown province should be lowercased
        await api_client.fetch_results("UNKNOWN", limit=1)

        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params["gameCode"] == "unknown"  # Lowercase fallback

    @pytest.mark.asyncio
    async def test_fetch_results_case_insensitive(self, api_client, mocker):
        """Test that province code is case insensitive"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # Lowercase province code
        await api_client.fetch_results("mb", limit=1)

        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params["gameCode"] == "miba"  # Should still map correctly

    @pytest.mark.asyncio
    async def test_fetch_results_default_limit(self, api_client, mocker):
        """Test default limit value"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)

        mocker.patch("httpx.AsyncClient", return_value=mock_client)

        # Use default limit (60)
        await api_client.fetch_results("MB")

        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params["limitNum"] == 60  # Default limit


class TestProvinceMapping:
    """Test province code mapping"""

    def test_all_regions_mapped(self):
        """Test that all major regions are mapped"""
        province_map = MU88APIClient.PROVINCE_MAP

        # Check MB
        assert "MB" in province_map

        # Check some MN provinces
        mn_provinces = ["TPHCM", "BALI", "BETR", "ANGI", "BIDU"]
        for province in mn_provinces:
            assert province in province_map

        # Check some MT provinces
        mt_provinces = ["DANA", "BIDI", "DALAK", "DANO", "GILA"]
        for province in mt_provinces:
            assert province in province_map

    def test_province_codes_are_lowercase(self):
        """Test that all game codes are lowercase"""
        province_map = MU88APIClient.PROVINCE_MAP

        for game_code in province_map.values():
            assert game_code == game_code.lower()

    def test_province_map_no_duplicates(self):
        """Test that there are no duplicate game codes"""
        province_map = MU88APIClient.PROVINCE_MAP
        game_codes = list(province_map.values())

        # Check for duplicates
        assert len(game_codes) == len(set(game_codes))
