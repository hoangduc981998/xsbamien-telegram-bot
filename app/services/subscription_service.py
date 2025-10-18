"""Subscription Service - Quản lý đăng ký nhận thông báo"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import DatabaseSession
from app.models.lottery_result import UserSubscription

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service quản lý subscriptions"""
    
    async def subscribe(
        self,
        user_id: int,
        province_code: str,
        username: Optional[str] = None,
        notification_time: Optional[str] = None
    ) -> bool:
        """
        Đăng ký nhận thông báo kết quả
        
        Args:
            user_id: Telegram user ID
            province_code: Mã tỉnh (MB, TPHCM, etc.)
            username: Telegram username
            notification_time: Giờ nhận thông báo (HH:MM)
            
        Returns:
            True nếu thành công
        """
        try:
            async with DatabaseSession() as session:
                # Kiểm tra đã subscribe chưa
                existing = await self._get_subscription(
                    session, user_id, province_code
                )
                
                if existing:
                    # Đã có, chỉ cần activate lại
                    existing.is_active = True
                    existing.updated_at = datetime.utcnow()
                    if notification_time:
                        existing.notification_time = notification_time
                    logger.info(f"✅ Reactivated subscription: user {user_id} -> {province_code}")
                else:
                    # Tạo mới
                    subscription = UserSubscription(
                        user_id=user_id,
                        username=username,
                        province_code=province_code,
                        notification_time=notification_time,
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    session.add(subscription)
                    logger.info(f"✅ New subscription: user {user_id} -> {province_code}")
                
                await session.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Error subscribing: {e}")
            return False
    
    async def unsubscribe(self, user_id: int, province_code: str) -> bool:
        """Hủy đăng ký"""
        try:
            async with DatabaseSession() as session:
                subscription = await self._get_subscription(
                    session, user_id, province_code
                )
                
                if subscription:
                    subscription.is_active = False
                    subscription.updated_at = datetime.utcnow()
                    await session.commit()
                    logger.info(f"✅ Unsubscribed: user {user_id} -> {province_code}")
                    return True
                
                logger.warning(f"⚠️ Subscription not found: user {user_id} -> {province_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error unsubscribing: {e}")
            return False
    
    async def get_user_subscriptions(self, user_id: int) -> List[UserSubscription]:
        """Lấy tất cả subscriptions của user"""
        try:
            async with DatabaseSession() as session:
                query = select(UserSubscription).where(
                    and_(
                        UserSubscription.user_id == user_id,
                        UserSubscription.is_active == True
                    )
                ).order_by(UserSubscription.province_code)
                
                result = await session.execute(query)
                subscriptions = result.scalars().all()
                
                logger.info(f"📋 User {user_id} has {len(subscriptions)} subscriptions")
                return list(subscriptions)
                
        except Exception as e:
            logger.error(f"❌ Error getting subscriptions: {e}")
            return []
    
    async def get_subscribers_by_province(
        self, province_code: str
    ) -> List[UserSubscription]:
        """Lấy tất cả users đăng ký nhận thông báo của 1 tỉnh"""
        try:
            async with DatabaseSession() as session:
                query = select(UserSubscription).where(
                    and_(
                        UserSubscription.province_code == province_code,
                        UserSubscription.is_active == True
                    )
                )
                
                result = await session.execute(query)
                subscribers = result.scalars().all()
                
                logger.info(f"📋 Province {province_code} has {len(subscribers)} subscribers")
                return list(subscribers)
                
        except Exception as e:
            logger.error(f"❌ Error getting subscribers: {e}")
            return []
    
    async def delete_subscription(self, user_id: int, province_code: str) -> bool:
        """Xóa hoàn toàn subscription (không chỉ deactivate)"""
        try:
            async with DatabaseSession() as session:
                stmt = delete(UserSubscription).where(
                    and_(
                        UserSubscription.user_id == user_id,
                        UserSubscription.province_code == province_code
                    )
                )
                
                await session.execute(stmt)
                await session.commit()
                
                logger.info(f"🗑️ Deleted subscription: user {user_id} -> {province_code}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error deleting subscription: {e}")
            return False
    
    async def _get_subscription(
        self,
        session: AsyncSession,
        user_id: int,
        province_code: str
    ) -> Optional[UserSubscription]:
        """Helper: Lấy subscription"""
        query = select(UserSubscription).where(
            and_(
                UserSubscription.user_id == user_id,
                UserSubscription.province_code == province_code
            )
        )
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
