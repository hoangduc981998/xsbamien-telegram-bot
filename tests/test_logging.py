"""Tests cho logging system"""

import pytest
import logging
from pathlib import Path
from unittest.mock import patch
from datetime import date

from app.utils.logging_helper import setup_logging
from app.utils.cache import ScheduleCache


class TestLoggingConfiguration:
    """Tests cho logging configuration"""

    def test_logging_directory_created(self):
        """Test logs directory được tạo"""
        setup_logging()

        log_dir = Path("logs")
        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_logging_setup_no_errors(self):
        """Test logging setup không có lỗi"""
        setup_logging()

        logger = logging.getLogger("test")
        logger.info("Test message")

        # No assertions needed, just verify no exceptions
        assert True


class TestCacheLogging:
    """Tests cho cache logging"""

    def setup_method(self):
        """Setup before each test"""
        setup_logging()
        ScheduleCache.clear_cache()

    def test_cache_refresh_logging(self, caplog):
        """Test cache refresh được log"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 1
            mock_dt.now.return_value.date.return_value = date(2025, 10, 15)

            with caplog.at_level(logging.INFO):
                ScheduleCache.get_schedule_day()

            # Verify log message
            assert "Cache refreshed" in caplog.text
            assert "weekday=1" in caplog.text
            assert "schedule_day=2" in caplog.text

    def test_cache_hit_logging(self, caplog):
        """Test cache hit được log"""
        with patch("app.utils.cache.datetime") as mock_dt:
            today = date(2025, 10, 15)
            mock_dt.now.return_value.weekday.return_value = 1
            mock_dt.now.return_value.date.return_value = today

            # First call - cache miss
            ScheduleCache.get_schedule_day()

            # Second call - cache hit
            caplog.clear()
            with caplog.at_level(logging.DEBUG):
                ScheduleCache.get_schedule_day()

            assert "Cache HIT" in caplog.text

    def test_cache_miss_logging(self, caplog):
        """Test cache miss được log"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 1
            mock_dt.now.return_value.date.return_value = date(2025, 10, 15)

            with caplog.at_level(logging.INFO):
                ScheduleCache.get_schedule_day()

            assert "Cache MISS" in caplog.text or "Cache refreshed" in caplog.text

    def test_cache_clear_logging(self, caplog):
        """Test cache clear được log"""
        with caplog.at_level(logging.WARNING):
            ScheduleCache.clear_cache()

        assert "Cache cleared" in caplog.text

    def test_cache_stats_tracking(self):
        """Test cache stats được track đúng"""
        with patch("app.utils.cache.datetime") as mock_dt:
            today = date(2025, 10, 15)
            mock_dt.now.return_value.weekday.return_value = 1
            mock_dt.now.return_value.date.return_value = today

            # Multiple calls (1 miss + 9 hits)
            for _ in range(10):
                ScheduleCache.get_schedule_day()

            info = ScheduleCache.get_cache_info()
            stats = info["stats"]

            assert stats["cache_hits"] == 9
            assert stats["cache_misses"] == 1
            assert stats["total_requests"] == 10
            assert stats["hit_rate"] == 90.0

    def test_conversion_formula_logging(self, caplog):
        """Test conversion formula được log"""
        with patch("app.utils.cache.datetime") as mock_dt:
            mock_dt.now.return_value.weekday.return_value = 1
            mock_dt.now.return_value.date.return_value = date(2025, 10, 15)

            with caplog.at_level(logging.DEBUG):
                ScheduleCache.get_schedule_day()

            assert "Conversion" in caplog.text
            assert "weekday + 1" in caplog.text


class TestLoggingIntegration:
    """Integration tests cho logging system"""

    def setup_method(self):
        """Setup before each test"""
        setup_logging()

    def test_multiple_loggers_coexist(self):
        """Test nhiều loggers có thể cùng tồn tại"""
        logger1 = logging.getLogger("app.utils.cache")
        logger2 = logging.getLogger("app.ui.keyboards")
        logger3 = logging.getLogger("app.main")

        logger1.info("Cache logger")
        logger2.info("Keyboard logger")
        logger3.info("Main logger")

        # No errors
        assert True

    def test_log_levels_work(self, caplog):
        """Test các log levels hoạt động đúng"""
        logger = logging.getLogger("test")

        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug")
            logger.info("Info")
            logger.warning("Warning")
            logger.error("Error")
            logger.critical("Critical")

        assert "Debug" in caplog.text
        assert "Info" in caplog.text
        assert "Warning" in caplog.text
        assert "Error" in caplog.text
        assert "Critical" in caplog.text
