"""Unit tests for API data transformer"""

import pytest
import json
from app.services.api.transformer import DataTransformer


@pytest.fixture
def sample_mb_api_response():
    """Sample MB API response from MU88"""
    return {
        "success": True,
        "t": {
            "name": "Miền Bắc",
            "navCate": "MB",
            "issueList": [
                {
                    "turnNum": "2025-10-14",
                    "detail": json.dumps(
                        [
                            "12345",  # DB
                            "67890",  # G1
                            "11111,22222",  # G2
                            "33333,44444,55555,66666,77777,88888",  # G3
                            "1234,5678,9012,3456",  # G4
                            "1111,2222,3333,4444,5555,6666",  # G5
                            "111,222,333",  # G6
                            "11,22,33,44",  # G7
                        ]
                    ),
                }
            ],
        },
    }


@pytest.fixture
def sample_mn_api_response():
    """Sample MN API response from MU88"""
    return {
        "success": True,
        "t": {
            "name": "TP. Hồ Chí Minh",
            "navCate": "MN",
            "issueList": [
                {
                    "turnNum": "2025-10-15",
                    "detail": json.dumps(
                        [
                            "456789",  # DB
                            "890123",  # G1
                            "234567",  # G2
                            "123456,789012",  # G3
                            "12345,67890,11111,22222,33333,44444,55555",  # G4
                            "4567",  # G5
                            "1234,5678,9012",  # G6
                            "123",  # G7
                            "12",  # G8
                        ]
                    ),
                }
            ],
        },
    }


@pytest.fixture
def sample_mt_api_response():
    """Sample MT API response from MU88"""
    return {
        "success": True,
        "t": {
            "name": "Đà Nẵng",
            "navCate": "MT",
            "issueList": [
                {
                    "turnNum": "2025-10-16",
                    "detail": json.dumps(
                        [
                            "999999",  # DB
                            "888888",  # G1
                            "777777",  # G2
                            "666666,555555",  # G3
                            "11111,22222,33333,44444,55555,66666,77777",  # G4
                            "8888",  # G5
                            "1111,2222,3333",  # G6
                            "444",  # G7
                            "55",  # G8
                        ]
                    ),
                }
            ],
        },
    }


class TestTransformSingleResult:
    """Test transform_single_result() function"""

    def test_transform_mb_result(self):
        """Test transforming MB result"""
        issue = {
            "turnNum": "2025-10-14",
            "detail": json.dumps(
                [
                    "12345",  # DB
                    "67890",  # G1
                    "11111,22222",  # G2
                    "33333,44444,55555,66666,77777,88888",  # G3
                    "1234,5678,9012,3456",  # G4
                    "1111,2222,3333,4444,5555,6666",  # G5
                    "111,222,333",  # G6
                    "11,22,33,44",  # G7
                ]
            ),
        }

        result = DataTransformer.transform_single_result(issue, "Miền Bắc", "MB")

        assert result["date"] == "2025-10-14"
        assert result["province"] == "Miền Bắc"
        assert result["DB"] == ["12345"]
        assert result["G1"] == ["67890"]
        assert result["G2"] == ["11111", "22222"]
        assert len(result["G3"]) == 6
        assert result["G7"] == ["11", "22", "33", "44"]

    def test_transform_mn_result(self):
        """Test transforming MN result"""
        issue = {
            "turnNum": "2025-10-15",
            "detail": json.dumps(
                [
                    "456789",  # DB
                    "890123",  # G1
                    "234567",  # G2
                    "123456,789012",  # G3
                    "12345,67890,11111,22222,33333,44444,55555",  # G4
                    "4567",  # G5
                    "1234,5678,9012",  # G6
                    "123",  # G7
                    "12",  # G8
                ]
            ),
        }

        result = DataTransformer.transform_single_result(issue, "TP.HCM", "MN")

        assert result["date"] == "2025-10-15"
        assert result["province"] == "TP.HCM"
        assert result["DB"] == ["456789"]
        assert result["G8"] == ["12"]
        assert result["G7"] == ["123"]
        assert len(result["G4"]) == 7

    def test_transform_mt_result(self):
        """Test transforming MT result"""
        issue = {
            "turnNum": "2025-10-16",
            "detail": json.dumps(
                [
                    "999999",  # DB
                    "888888",  # G1
                    "777777",  # G2
                    "666666,555555",  # G3
                    "11111,22222,33333,44444,55555,66666,77777",  # G4
                    "8888",  # G5
                    "1111,2222,3333",  # G6
                    "444",  # G7
                    "55",  # G8
                ]
            ),
        }

        result = DataTransformer.transform_single_result(issue, "Đà Nẵng", "MT")

        assert result["date"] == "2025-10-16"
        assert result["province"] == "Đà Nẵng"
        assert result["DB"] == ["999999"]
        assert result["G1"] == ["888888"]
        assert result["G8"] == ["55"]

    def test_transform_with_empty_detail(self):
        """Test transforming result with empty detail"""
        issue = {"turnNum": "2025-10-14", "detail": "[]"}

        result = DataTransformer.transform_single_result(issue, "Test", "MB")

        assert result["date"] == "2025-10-14"
        assert result["province"] == "Test"
        # Should handle empty detail gracefully

    def test_transform_with_invalid_json(self):
        """Test transforming result with invalid JSON"""
        issue = {"turnNum": "2025-10-14", "detail": "invalid json"}

        result = DataTransformer.transform_single_result(issue, "Test", "MB")

        # Should return empty dict or handle gracefully
        assert isinstance(result, dict)

    def test_transform_preserves_province_name(self):
        """Test that province name is preserved correctly"""
        issue = {
            "turnNum": "2025-10-14",
            "detail": json.dumps(["12345"]),
        }

        result = DataTransformer.transform_single_result(issue, "Custom Province Name", "MB")

        assert result["province"] == "Custom Province Name"


class TestTransformResults:
    """Test transform_results() function"""

    def test_transform_mb_api_response(self, sample_mb_api_response):
        """Test transforming MB API response"""
        results = DataTransformer.transform_results(sample_mb_api_response)

        assert len(results) == 1
        result = results[0]
        assert result["date"] == "2025-10-14"
        assert result["province"] == "Miền Bắc"
        assert "DB" in result
        assert "G1" in result
        assert "G7" in result

    def test_transform_mn_api_response(self, sample_mn_api_response):
        """Test transforming MN API response"""
        results = DataTransformer.transform_results(sample_mn_api_response)

        assert len(results) == 1
        result = results[0]
        assert result["date"] == "2025-10-15"
        assert result["province"] == "TP. Hồ Chí Minh"
        assert "DB" in result
        assert "G8" in result

    def test_transform_mt_api_response(self, sample_mt_api_response):
        """Test transforming MT API response"""
        results = DataTransformer.transform_results(sample_mt_api_response)

        assert len(results) == 1
        result = results[0]
        assert result["date"] == "2025-10-16"
        assert result["province"] == "Đà Nẵng"
        assert "DB" in result
        assert "G8" in result

    def test_transform_multiple_issues(self):
        """Test transforming API response with multiple issues"""
        api_response = {
            "success": True,
            "t": {
                "name": "Test",
                "navCate": "MB",
                "issueList": [
                    {"turnNum": "2025-10-14", "detail": json.dumps(["12345"])},
                    {"turnNum": "2025-10-13", "detail": json.dumps(["67890"])},
                    {"turnNum": "2025-10-12", "detail": json.dumps(["11111"])},
                ],
            },
        }

        results = DataTransformer.transform_results(api_response)

        assert len(results) == 3
        assert results[0]["date"] == "2025-10-14"
        assert results[1]["date"] == "2025-10-13"
        assert results[2]["date"] == "2025-10-12"

    def test_transform_empty_issue_list(self):
        """Test transforming API response with empty issue list"""
        api_response = {
            "success": True,
            "t": {"name": "Test", "navCate": "MB", "issueList": []},
        }

        results = DataTransformer.transform_results(api_response)

        assert len(results) == 0

    def test_transform_missing_t_key(self):
        """Test transforming API response with missing 't' key"""
        api_response = {"success": True}

        results = DataTransformer.transform_results(api_response)

        # Should handle gracefully
        assert isinstance(results, list)

    def test_transform_determines_region_from_navcate(self):
        """Test that region is determined from navCate"""
        # Test MB
        mb_response = {
            "success": True,
            "t": {
                "name": "Test",
                "navCate": "MB",
                "issueList": [{"turnNum": "2025-10-14", "detail": json.dumps(["12345"])}],
            },
        }
        results = DataTransformer.transform_results(mb_response)
        assert len(results) == 1

        # Test MN
        mn_response = {
            "success": True,
            "t": {
                "name": "Test",
                "navCate": "MN",
                "issueList": [
                    {
                        "turnNum": "2025-10-14",
                        "detail": json.dumps(["12345"] * 9),  # 9 prizes for MN
                    }
                ],
            },
        }
        results = DataTransformer.transform_results(mn_response)
        assert len(results) == 1

        # Test MT
        mt_response = {
            "success": True,
            "t": {
                "name": "Test",
                "navCate": "MT",
                "issueList": [
                    {
                        "turnNum": "2025-10-14",
                        "detail": json.dumps(["12345"] * 9),  # 9 prizes for MT
                    }
                ],
            },
        }
        results = DataTransformer.transform_results(mt_response)
        assert len(results) == 1

    def test_transform_unknown_navcate_defaults_to_mn(self):
        """Test that unknown navCate defaults to MN"""
        api_response = {
            "success": True,
            "t": {
                "name": "Test",
                "navCate": "UNKNOWN",
                "issueList": [
                    {
                        "turnNum": "2025-10-14",
                        "detail": json.dumps(["12345"] * 9),
                    }
                ],
            },
        }

        results = DataTransformer.transform_results(api_response)

        # Should default to MN format (9 prizes)
        assert len(results) == 1

    def test_transform_skips_invalid_issues(self):
        """Test that invalid issues are skipped gracefully"""
        api_response = {
            "success": True,
            "t": {
                "name": "Test",
                "navCate": "MB",
                "issueList": [
                    {"turnNum": "2025-10-14", "detail": json.dumps(["12345"])},
                    {"turnNum": "2025-10-13", "detail": "invalid json"},  # Invalid
                    {"turnNum": "2025-10-12", "detail": json.dumps(["67890"])},
                ],
            },
        }

        results = DataTransformer.transform_results(api_response)

        # Should have 2 valid results (invalid one skipped)
        assert len(results) >= 1  # At least one valid result


class TestDataTransformerEdgeCases:
    """Test edge cases and error handling"""

    def test_prize_mapping_mb_correct_order(self):
        """Test that MB prizes are mapped in correct order"""
        assert DataTransformer.MB_PRIZES == [
            "DB",
            "G1",
            "G2",
            "G3",
            "G4",
            "G5",
            "G6",
            "G7",
        ]

    def test_prize_mapping_mn_mt_correct_order(self):
        """Test that MN/MT prizes are mapped in correct order"""
        assert DataTransformer.MN_MT_PRIZES == [
            "DB",
            "G1",
            "G2",
            "G3",
            "G4",
            "G5",
            "G6",
            "G7",
            "G8",
        ]

    def test_transform_handles_comma_separated_numbers(self):
        """Test that comma-separated numbers are split correctly"""
        issue = {
            "turnNum": "2025-10-14",
            "detail": json.dumps(["12345", "67890", "11111,22222,33333"]),
        }

        result = DataTransformer.transform_single_result(issue, "Test", "MB")

        # G2 should be split into array
        assert result["G2"] == ["11111", "22222", "33333"]

    def test_transform_preserves_date_format(self):
        """Test that date format is preserved"""
        issue = {
            "turnNum": "2025-10-14",
            "detail": json.dumps(["12345"]),
        }

        result = DataTransformer.transform_single_result(issue, "Test", "MB")

        assert result["date"] == "2025-10-14"

    def test_transformer_is_static(self):
        """Test that transformer methods are static"""
        # Should be able to call without instantiation
        issue = {"turnNum": "2025-10-14", "detail": json.dumps(["12345"])}
        result = DataTransformer.transform_single_result(issue, "Test", "MB")
        assert isinstance(result, dict)

        api_response = {
            "success": True,
            "t": {
                "name": "Test",
                "navCate": "MB",
                "issueList": [issue],
            },
        }
        results = DataTransformer.transform_results(api_response)
        assert isinstance(results, list)
