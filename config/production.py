"""
Production-specific configuration
This module contains settings optimized for production deployment
"""

import logging
import os
from typing import Dict, Any


class ProductionConfig:
    """Production environment configuration"""

    # Environment
    ENVIRONMENT = "production"
    DEBUG = False

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Performance Settings
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    API_RETRY_TIMES = int(os.getenv("API_RETRY_TIMES", "3"))
    API_RETRY_DELAY = 2  # seconds

    # Cache Settings
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    CACHE_MAX_SIZE = 1000

    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_CALLS = 30  # calls per window
    RATE_LIMIT_WINDOW = 60  # seconds

    # Security Settings
    ALLOWED_UPDATES = ["message", "callback_query"]
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

    # Error Handling
    RETRY_ON_ERRORS = True
    MAX_ERROR_RETRIES = 3
    ERROR_NOTIFICATION_ENABLED = True

    # Monitoring
    HEALTH_CHECK_ENABLED = True
    METRICS_ENABLED = True

    @staticmethod
    def get_logging_config() -> Dict[str, Any]:
        """Get logging configuration for production"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": ProductionConfig.LOG_FORMAT,
                    "datefmt": ProductionConfig.LOG_DATE_FORMAT,
                },
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": ProductionConfig.LOG_LEVEL,
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "default",
                    "filename": "logs/app.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "default",
                    "filename": "logs/error.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                },
            },
            "root": {
                "level": ProductionConfig.LOG_LEVEL,
                "handlers": ["console", "file", "error_file"],
            },
            "loggers": {
                "telegram": {
                    "level": "WARNING",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "httpx": {
                    "level": "WARNING",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }

    @staticmethod
    def setup_production_logging():
        """Setup logging for production environment"""
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Configure logging
        config = ProductionConfig.get_logging_config()
        logging.config.dictConfig(config)

        # Set log level
        log_level = getattr(logging, ProductionConfig.LOG_LEVEL.upper(), logging.INFO)
        logging.getLogger().setLevel(log_level)


# Export config instance
config = ProductionConfig()
