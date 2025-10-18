"""Scheduler Jobs - CHECK KẾT QUẢ MỚI TRONG KHUNG GIỜ CỤ THỂ"""

import logging
from datetime import date, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from app.config import PROVINCES, SCHEDULE
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class SchedulerJobs:
    """Quản lý các scheduled jobs"""
    
    def __init__(self, bot):
        self.scheduler = AsyncIOScheduler()
        self.notification_service = NotificationService(bot=bot)
    
    def setup_jobs(self):
        """Thiết lập các jobs"""
        # ✅ Định nghĩa timezone Việt Nam
        vietnam_tz = ZoneInfo("Asia/Ho_Chi_Minh")
        
        # Miền Bắc: 18:30-18:48 (mỗi 3 phút, 6 lần)
        self.scheduler.add_job(
            self.check_mb_new_results,
            CronTrigger(
                hour=18,
                minute='30,33,36,39,42,45',
                timezone=vietnam_tz
            ),
            id='check_mb_results',
            name='Check Miền Bắc (18:30-18:48, mỗi 3 phút)',
            replace_existing=True
        )
        
        # Miền Trung: 17:30-17:48 (mỗi 3 phút, 6 lần)
        self.scheduler.add_job(
            self.check_mt_new_results,
            CronTrigger(
                hour=17,
                minute='30,33,36,39,42,45',
                timezone=vietnam_tz
            ),
            id='check_mt_results',
            name='Check Miền Trung (17:30-17:48, mỗi 3 phút)',
            replace_existing=True
        )
        
        # Miền Nam: 16:30-16:48 (mỗi 3 phút, 6 lần)
        self.scheduler.add_job(
            self.check_mn_new_results,
            CronTrigger(
                hour=16,
                minute='30,33,36,39,42,45',
                timezone=vietnam_tz
            ),
            id='check_mn_results',
            name='Check Miền Nam (16:30-16:48, mỗi 3 phút)',
            replace_existing=True
        )
        
        logger.info("✅ Scheduler jobs đã được thiết lập (HIGH FREQUENCY MODE - GIỜ VIỆT NAM)")
        logger.info("   🕐 MB: 18:30-18:48 VN (mỗi 3 phút, 6 lần)")
        logger.info("   🕐 MT: 17:30-17:48 VN (mỗi 3 phút, 6 lần)")
        logger.info("   🕐 MN: 16:30-16:48 VN (mỗi 3 phút, 6 lần)")
    
    async def check_mb_new_results(self):
        """Check kết quả Miền Bắc mới (18:10-18:45)"""
        current_time = datetime.now().strftime("%H:%M")
        logger.info(f"🔍 [{current_time}] Checking MB new results...")
        
        today = date.today()
        
        try:
            summary = await self.notification_service.check_and_send_if_new_result(
                province_code="MB",
                check_date=today
            )
            
            if summary:
                logger.info(f"✅ [{current_time}] MB notification sent: {summary}")
            else:
                logger.info(f"ℹ️ [{current_time}] MB: No new complete result or already sent")
                
        except Exception as e:
            logger.error(f"❌ Error checking MB: {e}")
    
    async def check_mt_new_results(self):
        """Check kết quả Miền Trung mới (17:20-17:45)"""
        current_time = datetime.now().strftime("%H:%M")
        logger.info(f"🔍 [{current_time}] Checking MT new results...")
        
        today = date.today()
        weekday = today.weekday()
        schedule_day = (weekday + 2) % 7
        
        # Lấy tỉnh Miền Trung quay hôm nay
        provinces_today = SCHEDULE["MT"].get(schedule_day, [])
        
        logger.info(f"📋 MT provinces today: {provinces_today}")
        
        for province_code in provinces_today:
            try:
                summary = await self.notification_service.check_and_send_if_new_result(
                    province_code=province_code,
                    check_date=today
                )
                
                if summary:
                    logger.info(f"✅ [{current_time}] {province_code} sent: {summary}")
                    
            except Exception as e:
                logger.error(f"❌ Error checking {province_code}: {e}")
    
    async def check_mn_new_results(self):
        """Check kết quả Miền Nam mới (16:20-16:45)"""
        current_time = datetime.now().strftime("%H:%M")
        logger.info(f"🔍 [{current_time}] Checking MN new results...")
        
        today = date.today()
        weekday = today.weekday()
        schedule_day = (weekday + 2) % 7
        
        # Lấy tỉnh Miền Nam quay hôm nay
        provinces_today = SCHEDULE["MN"].get(schedule_day, [])
        
        logger.info(f"📋 MN provinces today: {provinces_today}")
        
        for province_code in provinces_today:
            try:
                summary = await self.notification_service.check_and_send_if_new_result(
                    province_code=province_code,
                    check_date=today
                )
                
                if summary:
                    logger.info(f"✅ [{current_time}] {province_code} sent: {summary}")
                    
            except Exception as e:
                logger.error(f"❌ Error checking {province_code}: {e}")
    
    def start(self):
        """Khởi động scheduler"""
        self.scheduler.start()
        logger.info("🚀 Scheduler started (OPTIMIZED MODE)")
        logger.info("   ⏰ Chỉ check trong khung giờ cụ thể")
        logger.info("   ✅ Kiểm tra đủ giải mới gửi")
    
    def shutdown(self):
        """Tắt scheduler"""
        self.scheduler.shutdown()
        logger.info("🛑 Scheduler stopped")