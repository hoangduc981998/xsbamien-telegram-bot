"""Admin Service - Quản lý admin functions"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter

from sqlalchemy import select, func, and_, or_
from telegram import Bot
from telegram.error import TelegramError

from app.database import DatabaseSession
from app.models.lottery_result import UserSubscription, NotificationLog, LotteryResult
from app.config import PROVINCES

logger = logging.getLogger(__name__)


class AdminService:
    """Service cho admin operations"""
    
    def __init__(self):
        pass
    
    async def get_dashboard_stats(self) -> Dict:
        """
        Lấy thống kê tổng quan cho admin dashboard
        
        Returns:
            Dict với các thống kê
        """
        try:
            async with DatabaseSession() as session:
                # 1. Tổng subscribers (unique users)
                query_users = select(func.count(func.distinct(UserSubscription.user_id))).where(
                    UserSubscription.is_active == True
                )
                result = await session.execute(query_users)
                total_users = result.scalar() or 0
                
                # 2. Tổng subscriptions
                query_subs = select(func.count(UserSubscription.id)).where(
                    UserSubscription.is_active == True
                )
                result = await session.execute(query_subs)
                total_subscriptions = result.scalar() or 0
                
                # 3. Top provinces
                query_top = select(
                    UserSubscription.province_code,
                    func.count(UserSubscription.id).label('count')
                ).where(
                    UserSubscription.is_active == True
                ).group_by(
                    UserSubscription.province_code
                ).order_by(
                    func.count(UserSubscription.id).desc()
                ).limit(10)
                
                result = await session.execute(query_top)
                top_provinces = result.all()
                
                # 4. Subscriptions gần đây (7 ngày)
                week_ago = datetime.utcnow() - timedelta(days=7)
                query_recent = select(
                    func.date(UserSubscription.created_at).label('date'),
                    func.count(UserSubscription.id).label('count')
                ).where(
                    and_(
                        UserSubscription.created_at >= week_ago,
                        UserSubscription.is_active == True
                    )
                ).group_by(
                    func.date(UserSubscription.created_at)
                ).order_by(
                    func.date(UserSubscription.created_at).desc()
                )
                
                result = await session.execute(query_recent)
                recent_subs = result.all()
                
                # 5. Thống kê notifications (30 ngày)
                month_ago = datetime.utcnow() - timedelta(days=30)
                query_notif = select(
                    func.sum(NotificationLog.total_sent).label('total'),
                    func.sum(NotificationLog.success_count).label('success'),
                    func.sum(NotificationLog.failed_count).label('failed')
                ).where(
                    NotificationLog.sent_at >= month_ago
                )
                
                result = await session.execute(query_notif)
                notif_stats = result.first()
                
                return {
                    'total_users': total_users,
                    'total_subscriptions': total_subscriptions,
                    'avg_subs_per_user': round(total_subscriptions / total_users, 1) if total_users > 0 else 0,
                    'top_provinces': [
                        {'code': row.province_code, 'count': row.count}
                        for row in top_provinces
                    ],
                    'recent_subscriptions': [
                        {'date': str(row.date), 'count': row.count}
                        for row in recent_subs
                    ],
                    'notifications': {
                        'total': notif_stats.total or 0 if notif_stats else 0,
                        'success': notif_stats.success or 0 if notif_stats else 0,
                        'failed': notif_stats.failed or 0 if notif_stats else 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {}
    
    async def get_all_subscribers(self) -> List[Dict]:
        """
        Lấy danh sách tất cả subscribers với chi tiết
        
        Returns:
            List of dicts với thông tin subscriber
        """
        try:
            async with DatabaseSession() as session:
                query = select(
                    UserSubscription.user_id,
                    UserSubscription.username,
                    func.group_concat(UserSubscription.province_code).label('provinces'),
                    func.count(UserSubscription.id).label('sub_count')
                ).where(
                    UserSubscription.is_active == True
                ).group_by(
                    UserSubscription.user_id
                )
                
                result = await session.execute(query)
                subscribers = result.all()
                
                return [
                    {
                        'user_id': row.user_id,
                        'username': row.username,
                        'provinces': row.provinces.split(',') if row.provinces else [],
                        'count': row.sub_count
                    }
                    for row in subscribers
                ]
                
        except Exception as e:
            logger.error(f"Error getting subscribers: {e}")
            return []
    
    async def broadcast_message(
        self,
        bot: Bot,
        message: str,
        province_filter: Optional[str] = None
    ) -> Dict:
        """
        Gửi broadcast message đến tất cả hoặc subscribers của 1 tỉnh
        
        Args:
            bot: Telegram Bot instance
            message: Nội dung tin nhắn
            province_filter: Nếu có, chỉ gửi cho subscribers của tỉnh này
            
        Returns:
            Dict với thống kê gửi
        """
        try:
            async with DatabaseSession() as session:
                # Lấy danh sách user_id
                query = select(func.distinct(UserSubscription.user_id)).where(
                    UserSubscription.is_active == True
                )
                
                if province_filter:
                    query = query.where(UserSubscription.province_code == province_filter)
                
                result = await session.execute(query)
                user_ids = [row[0] for row in result.all()]
            
            if not user_ids:
                return {'total': 0, 'success': 0, 'failed': 0, 'error': 'no_subscribers'}
            
            # Gửi message
            success_count = 0
            failed_count = 0
            
            for user_id in user_ids:
                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='HTML'
                    )
                    success_count += 1
                    logger.info(f"✅ Broadcast sent to user {user_id}")
                    
                except TelegramError as e:
                    failed_count += 1
                    logger.error(f"❌ Failed to broadcast to user {user_id}: {e}")
            
            summary = {
                'total': len(user_ids),
                'success': success_count,
                'failed': failed_count,
                'province_filter': province_filter
            }
            
            logger.info(f"📊 Broadcast summary: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error in broadcast: {e}")
            return {'total': 0, 'success': 0, 'failed': 0, 'error': str(e)}
