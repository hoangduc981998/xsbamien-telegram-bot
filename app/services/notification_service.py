"""Notification Service - Gửi thông báo kết quả xổ số"""

import logging
from typing import List, Optional
from datetime import date, datetime

from telegram import Bot
from telegram.error import TelegramError
from sqlalchemy import select, and_

from app.config import TELEGRAM_TOKEN as BOT_TOKEN, PROVINCES
from app.services.subscription_service import SubscriptionService
from app.services.lottery_service import LotteryService
from app.ui.formatters import format_lottery_result
from app.database import DatabaseSession
from app.models.lottery_result import NotificationLog

logger = logging.getLogger(__name__)


class NotificationService:
    """Service gửi thông báo tự động"""
    
    def __init__(self, bot=None):
        self.subscription_service = SubscriptionService()
        self.lottery_service = LotteryService(use_database=True)
        self.bot = bot
    
    async def check_and_send_if_new_result(
        self,
        province_code: str,
        check_date: date = None
    ) -> Optional[dict]:
        """
        ✅ LOGIC MỚI: Kiểm tra có kết quả mới không, nếu có thì gửi
        
        Args:
            province_code: Mã tỉnh
            check_date: Ngày kiểm tra (mặc định: hôm nay)
            
        Returns:
            Dict với thống kê nếu đã gửi, None nếu chưa gửi
        """
        if check_date is None:
            check_date = date.today()
        
        logger.info(f"🔍 Checking new result for {province_code} - {check_date}")
        
        # 1. Kiểm tra đã gửi chưa (tránh gửi trùng)
        if await self._already_sent(province_code, check_date):
            logger.info(f"⏭️  Already sent {province_code} - {check_date}, skipping")
            return None
        
        # 2. Kiểm tra có kết quả mới không
        result = await self.lottery_service.get_latest_result(province_code)
        
        if not result:
            logger.info(f"ℹ️  No result found for {province_code}")
            return None
        
        # 3. Parse result date và so sánh
        result_date_str = result.get('date')
        
        # Convert to date object for comparison
        try:
            # Try dd/mm/yyyy format first (API format)
            result_date = datetime.strptime(result_date_str, '%d/%m/%Y').date()
        except (ValueError, TypeError):
            try:
                # Try yyyy-mm-dd format (DB format)
                result_date = datetime.strptime(result_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                logger.error(f"❌ Cannot parse date: {result_date_str}")
                return None
        
        # Chỉ gửi nếu là kết quả của ngày check_date
        if result_date != check_date:
            logger.info(f"⏭️  Result date {result_date} != check date {check_date}, skipping")
            return None
        
        logger.info(f"✅ Result date {result_date} matches check date {check_date}")
        
        # 4. Kiểm tra đủ số giải chưa
        province = PROVINCES.get(province_code, {})
        region = province.get("region", "MN")
        
        if not self._is_result_complete(result, region):
            logger.info(f"⏳ Result incomplete for {province_code}, waiting...")
            return None
        
        logger.info(f"✅ Result complete for {province_code}, sending notifications...")
        
        # 5. ĐỦ GIẢI → GỬI NGAY!
        summary = await self.send_result_notification(
            province_code=province_code,
            result_date=check_date
        )
        
        # 6. Đánh dấu đã gửi
        if summary and summary.get('success', 0) > 0:
            await self._mark_as_sent(province_code, check_date, summary)
        
        return summary
    
    def _is_result_complete(self, result: dict, region: str) -> bool:
        """
        Kiểm tra kết quả đã đủ số giải chưa
        
        Args:
            result: Dict kết quả xổ số
            region: Vùng (MB/MN/MT)
            
        Returns:
            True nếu đủ giải, False nếu thiếu
        """
        prizes = result.get('prizes', {})
        
        if not prizes:
            return False
        
        # Miền Bắc: 27 giải
        if region == 'MB':
            required_count = 27
            total_prizes = sum(len(v) if isinstance(v, list) else 1 for v in prizes.values())
            return total_prizes >= required_count
        
        # Miền Nam/Miền Trung: 18 giải
        else:
            required_count = 18
            total_prizes = sum(len(v) if isinstance(v, list) else 1 for v in prizes.values())
            return total_prizes >= required_count
    
    async def send_result_notification(
        self,
        province_code: str,
        result_date: date = None
    ) -> dict:
        """
        Gửi kết quả xổ số cho tất cả subscribers của 1 tỉnh
        
        Args:
            province_code: Mã tỉnh
            result_date: Ngày mở thưởng (mặc định: hôm nay)
            
        Returns:
            Dict với thống kê gửi thành công/thất bại
        """
        if self.bot is None:
            logger.error("Bot instance not provided!")
            return {"total": 0, "success": 0, "failed": 0, "error": "no_bot"}
        
        if result_date is None:
            result_date = date.today()
        
        logger.info(f"📤 Sending notifications for {province_code} - {result_date}")
        
        # Lấy danh sách subscribers
        subscribers = await self.subscription_service.get_subscribers_by_province(
            province_code
        )
        
        if not subscribers:
            logger.info(f"ℹ️ No subscribers for {province_code}")
            return {"total": 0, "success": 0, "failed": 0}
        
        # Lấy kết quả xổ số
        try:
            # Lấy kết quả mới nhất
            result = await self.lottery_service.get_latest_result(province_code)
            
            if not result:
                logger.warning(f"⚠️ No result found for {province_code} - {result_date}")
                return {"total": len(subscribers), "success": 0, "failed": 0, "error": "no_result"}
            
            # Format message
            province = PROVINCES.get(province_code, {})
            region = province.get("region", "MN")
            message = format_lottery_result(result, region)
            
            # Thêm header cho notification
            notification_header = f"🔔 <b>THÔNG BÁO KẾT QUẢ XỔ SỐ</b>\n\n"
            full_message = notification_header + message
            
        except Exception as e:
            logger.error(f"❌ Error getting result: {e}")
            return {"total": len(subscribers), "success": 0, "failed": 0, "error": str(e)}
        
        # Gửi cho từng subscriber
        success_count = 0
        failed_count = 0
        
        for subscriber in subscribers:
            try:
                await self.bot.send_message(
                    chat_id=subscriber.user_id,
                    text=full_message,
                    parse_mode="HTML"
                )
                success_count += 1
                logger.info(f"✅ Sent to user {subscriber.user_id}")
                
            except TelegramError as e:
                failed_count += 1
                logger.error(f"❌ Failed to send to user {subscriber.user_id}: {e}")
        
        summary = {
            "total": len(subscribers),
            "success": success_count,
            "failed": failed_count,
            "province": province_code,
            "date": str(result_date)
        }
        
        logger.info(f"📊 Notification summary: {summary}")
        return summary
    
    async def _already_sent(self, province_code: str, result_date: date) -> bool:
        """Kiểm tra đã gửi thông báo chưa"""
        try:
            async with DatabaseSession() as session:
                query = select(NotificationLog).where(
                    and_(
                        NotificationLog.province_code == province_code,
                        NotificationLog.result_date == result_date
                    )
                )
                
                result = await session.execute(query)
                log = result.scalar_one_or_none()
                
                return log is not None
                
        except Exception as e:
            logger.error(f"Error checking notification log: {e}")
            return False
    
    async def _mark_as_sent(
        self,
        province_code: str,
        result_date: date,
        summary: dict
    ):
        """Đánh dấu đã gửi thông báo"""
        try:
            async with DatabaseSession() as session:
                log = NotificationLog(
                    province_code=province_code,
                    result_date=result_date,
                    sent_at=datetime.utcnow(),
                    total_sent=summary.get("total", 0),
                    success_count=summary.get("success", 0),
                    failed_count=summary.get("failed", 0)
                )
                
                session.add(log)
                await session.commit()
                
                logger.info(f"✅ Marked as sent: {province_code} - {result_date}")
                
        except Exception as e:
            logger.error(f"Error marking as sent: {e}")
    
    async def send_test_notification(self, user_id: int, province_code: str) -> bool:
        """Gửi thông báo test"""
        if self.bot is None:
            logger.error("Bot instance not provided!")
            return False
        
        try:
            result = await self.lottery_service.get_latest_result(province_code)
            
            if not result:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=f"⚠️ Chưa có kết quả mới nhất cho {province_code}",
                    parse_mode="HTML"
                )
                return False
            
            province = PROVINCES.get(province_code, {})
            region = province.get("region", "MN")
            message = format_lottery_result(result, region)
            
            test_header = f"🔔 <b>THÔNG BÁO TEST</b>\n\n"
            full_message = test_header + message
            
            await self.bot.send_message(
                chat_id=user_id,
                text=full_message,
                parse_mode="HTML"
            )
            
            logger.info(f"✅ Sent test notification to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending test notification: {e}")
            return False
