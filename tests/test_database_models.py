"""Test database models"""

import pytest
from datetime import date, datetime
from app.models import LotteryResult, Lo2SoHistory


class TestLotteryResult:
    """Test LotteryResult model"""

    def test_lottery_result_creation(self):
        """Test creating a LotteryResult instance"""
        result = LotteryResult(
            province_code="MB",
            province_name="Miền Bắc",
            region="MB",
            draw_date=date(2025, 10, 15),
            prizes={"DB": ["12345"], "G1": ["67890"]},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        assert result.province_code == "MB"
        assert result.province_name == "Miền Bắc"
        assert result.region == "MB"
        assert result.draw_date == date(2025, 10, 15)
        assert result.prizes["DB"] == ["12345"]

    def test_lottery_result_to_dict(self):
        """Test to_dict method"""
        result = LotteryResult(
            id=1,
            province_code="TPHCM",
            province_name="TP. Hồ Chí Minh",
            region="MN",
            draw_date=date(2025, 10, 15),
            prizes={"DB": ["12345"]},
            created_at=datetime(2025, 10, 15, 10, 0, 0),
            updated_at=datetime(2025, 10, 15, 10, 0, 0)
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["id"] == 1
        assert result_dict["province_code"] == "TPHCM"
        assert result_dict["date"] == "2025-10-15"
        assert result_dict["prizes"]["DB"] == ["12345"]

    def test_lottery_result_repr(self):
        """Test string representation"""
        result = LotteryResult(
            province_code="MB",
            province_name="Miền Bắc",
            region="MB",
            draw_date=date(2025, 10, 15),
            prizes={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        assert "LotteryResult" in repr(result)
        assert "MB" in repr(result)


class TestLo2SoHistory:
    """Test Lo2SoHistory model"""

    def test_lo2so_history_creation(self):
        """Test creating a Lo2SoHistory instance"""
        lo2so = Lo2SoHistory(
            lottery_result_id=1,
            province_code="MB",
            region="MB",
            draw_date=date(2025, 10, 15),
            number="45",
            prize_type="DB",
            position="last_2",
            created_at=datetime.utcnow()
        )
        
        assert lo2so.lottery_result_id == 1
        assert lo2so.province_code == "MB"
        assert lo2so.number == "45"
        assert lo2so.prize_type == "DB"

    def test_lo2so_history_to_dict(self):
        """Test to_dict method"""
        lo2so = Lo2SoHistory(
            id=1,
            lottery_result_id=10,
            province_code="TPHCM",
            region="MN",
            draw_date=date(2025, 10, 15),
            number="78",
            prize_type="G7",
            position="last_2"
        )
        
        lo2so_dict = lo2so.to_dict()
        
        assert lo2so_dict["id"] == 1
        assert lo2so_dict["lottery_result_id"] == 10
        assert lo2so_dict["number"] == "78"
        assert lo2so_dict["date"] == "2025-10-15"

    def test_lo2so_history_repr(self):
        """Test string representation"""
        lo2so = Lo2SoHistory(
            lottery_result_id=1,
            province_code="MB",
            region="MB",
            draw_date=date(2025, 10, 15),
            number="45",
            prize_type="DB",
            position="last_2"
        )
        
        assert "Lo2So" in repr(lo2so)
        assert "45" in repr(lo2so)
        assert "MB" in repr(lo2so)
