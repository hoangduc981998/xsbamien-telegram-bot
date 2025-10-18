"""Lottery result models"""

from datetime import datetime
from typing import Dict

from sqlalchemy import Column, Integer, BigInteger, String, Date, JSON, DateTime, Boolean
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    JSON,
    ForeignKey,
    Index,
    BigInteger,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base



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



class Lo3SoHistory(Base):
    """Lịch sử xuất hiện của lô 3 số (ba càng)"""
    
    __tablename__ = "lo_3_so_history"
    
    id = Column(Integer, primary_key=True, index=True)
    lottery_result_id = Column(Integer, ForeignKey("lottery_results.id"), nullable=False, index=True)
    province_code = Column(String(20), nullable=False, index=True)
    region = Column(String(10), nullable=False, index=True)
    draw_date = Column(Date, nullable=False, index=True)
    number = Column(String(3), nullable=False, index=True)  # 3 chữ số
    prize_type = Column(String(10), nullable=False)  # Loại giải (DB, G1, G2, etc.)
    position = Column(String(20), nullable=False)  # Vị trí trong giải
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_lo3so_number_date", "number", "draw_date"),
        Index("idx_lo3so_province_number_date", "province_code", "number", "draw_date"),
        Index("idx_lo3so_region_number_date", "region", "number", "draw_date"),
        Index("idx_lo3so_draw_date_number", "draw_date", "number"),
    )
    
    def __repr__(self):
        return f"<Lo3SoHistory(number={self.number}, province={self.province_code}, date={self.draw_date})>"



class UserSubscription(Base):
    """User subscription for lottery result notifications"""
    
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    province_code = Column(String(10), nullable=False, index=True)
    notification_time = Column(String(5), nullable=True, comment="HH:MM format, e.g., 18:30")
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserSubscription(user_id={self.user_id}, province={self.province_code}, active={self.is_active})>"


class NotificationLog(Base):
    """Log các lần gửi thông báo để tránh gửi trùng"""
    
    __tablename__ = "notification_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    province_code = Column(String(10), nullable=False, index=True)
    result_date = Column(Date, nullable=False)
    sent_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_sent = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<NotificationLog(province={self.province_code}, date={self.result_date}, sent={self.total_sent})>"
