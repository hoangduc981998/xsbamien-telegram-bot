"""Pytest fixtures for XS Ba Miền Bot tests"""

import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_datetime():
    """Mock datetime.now() to test different weekdays

    Returns:
        Function that creates a mock datetime with specified weekday
    """
    def _mock_datetime(weekday):
        mock = Mock()
        mock.weekday.return_value = weekday
        return mock
    return _mock_datetime


@pytest.fixture
def expected_provinces_by_day():
    """Expected provinces for each day of the week

    Returns:
        Dict mapping Python weekday (0=Monday) to list of expected province codes
    """
    return {
        0: ["MB", "THTH", "PHYE", "TPHCM", "DOTH", "CAMA"],  # Monday (schedule_day=1)
        1: ["MB", "QUNA", "DALAK", "BETR", "VUTA", "BALI"],  # Tuesday (schedule_day=2)
        2: ["MB", "DANA", "KHHO", "DONA", "CATH", "SOTR"],   # Wednesday (schedule_day=3)
        3: ["MB", "BIDI", "QUBI", "QUTR", "TANI", "ANGI", "BITH"],  # Thursday (schedule_day=4)
        4: ["MB", "GILA", "NITH", "VILO", "BIDU", "TRVI"],   # Friday (schedule_day=5)
        5: ["MB", "DANA", "QUNG", "DANO", "TPHCM", "LOAN", "BIPH", "HAGI"],  # Saturday (schedule_day=6)
        6: ["MB", "THTH", "KHHO", "KOTU", "TIGI", "KIGI", "DALAT"],  # Sunday (schedule_day=0)
    }
