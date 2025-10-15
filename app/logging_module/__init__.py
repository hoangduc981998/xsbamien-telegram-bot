"""Configuration modules"""

# Import từ config_data.py (file cũ chứa PROVINCES, SCHEDULE)
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import config data
from config_data import PROVINCES, SCHEDULE

# Import logging config
from .logging_config import setup_logging

__all__ = ["PROVINCES", "SCHEDULE", "setup_logging"]
