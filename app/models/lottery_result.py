"""Lottery Result Database Model"""

from datetime import datetime
from typing import Dict, List

from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class LotteryResult(Base):
    """
    Store complete lottery results for all provinces
    
    This table stores the full lottery result for each draw,
    including all prizes (DB, G1-G8) in JSON format.
    """
    __tablename__ = "lottery_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    province_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    province_name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # MB, MN, MT
    draw_date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    
    # Store all prizes in JSON format
    # Example: {"DB": ["12345"], "G1": ["67890"], "G2": ["11111", "22222"], ...}
    prizes: Mapped[Dict] = mapped_column(JSON, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Composite unique constraint - one result per province per day
    __table_args__ = (
        Index('idx_province_date', 'province_code', 'draw_date', unique=True),
        Index('idx_region_date', 'region', 'draw_date'),
        Index('idx_draw_date_desc', 'draw_date', postgresql_ops={'draw_date': 'DESC'}),
    )

    def __repr__(self) -> str:
        return f"<LotteryResult(province={self.province_code}, date={self.draw_date})>"

    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        return {
            "id": self.id,
            "province": self.province_name,
            "province_code": self.province_code,
            "region": self.region,
            "date": self.draw_date.strftime("%Y-%m-%d"),
            "prizes": self.prizes,
            "created_at": self.created_at.isoformat(),
        }


class Lo2SoHistory(Base):
    """
    Store extracted 2-digit lottery numbers (Lô 2 số) for fast queries
    
    This table denormalizes the 2-digit numbers from lottery results
    for efficient statistics queries (frequency, Lô Gan, etc.)
    """
    __tablename__ = "lo_2_so_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lottery_result_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    province_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    draw_date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    
    # The 2-digit number (00-99)
    number: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    
    # Which prize this number came from (DB, G1, G2, etc.)
    prize_type: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Position in the original number (last 2 digits)
    # This helps track if it's from special prizes
    position: Mapped[str] = mapped_column(String(20), default="last_2", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        # Fast lookup for specific number history
        Index('idx_number_date', 'number', 'draw_date', postgresql_ops={'draw_date': 'DESC'}),
        # Fast lookup for province statistics
        Index('idx_province_number_date', 'province_code', 'number', 'draw_date'),
        # Fast lookup for region statistics
        Index('idx_region_number_date', 'region', 'number', 'draw_date'),
        # Fast date range queries
        Index('idx_draw_date_number', 'draw_date', 'number', postgresql_ops={'draw_date': 'DESC'}),
    )

    def __repr__(self) -> str:
        return f"<Lo2So(number={self.number}, province={self.province_code}, date={self.draw_date})>"

    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        return {
            "id": self.id,
            "lottery_result_id": self.lottery_result_id,
            "province_code": self.province_code,
            "region": self.region,
            "date": self.draw_date.strftime("%Y-%m-%d"),
            "number": self.number,
            "prize_type": self.prize_type,
            "position": self.position,
        }
