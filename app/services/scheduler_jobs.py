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
        
        # ✅ MIỀN BẮC: Check mỗi 5 phút từ 18:25-18:45
        self.scheduler.add_job(
            self.check_mb_new_results,
            trigger=CronTrigger(
                hour=18, 
                minute='25,30,35,40,45',
                timezone=vietnam_tz
            ),
            id='check_mb_results',
            name='Check Miền Bắc (18:25-18:45, mỗi 5 phút)',
            replace_existing=True
        )
        
        # ✅ MIỀN TRUNG: Check mỗi 5 phút từ 17:20-17:45
        self.scheduler.add_job(
            self.check_mt_new_results,
            trigger=CronTrigger(
                hour=17, 
                minute='20,25,30,35,40,45', 
                timezone=vietnam_tz
            ),
            id='check_mt_results',
            name='Check Miền Trung (17:20-17:45, mỗi 5 phút)',
            replace_existing=True
        )
        
        # ✅ MIỀN NAM: Check mỗi 5 phút từ 16:20-16:45
        self.scheduler.add_job(
            self.check_mn_new_results,
            trigger=CronTrigger(
                hour=16, 
                minute='20,25,30,35,40,45', 
                timezone=vietnam_tz
                ),
            id='check_mn_results',
            name='Check Miền Nam (16:20-16:45, mỗi 5 phút)',
            replace_existing=True
        )
        
        logger.info("✅ Scheduler jobs đã được thiết lập (OPTIMIZED MODE - GIỜ VIỆT NAM)")
        logger.info("   🕐 MB: 18:20-18:45 VN (mỗi 5 phút)")
        logger.info("   🕐 MT: 17:20-17:45 VN (mỗi 5 phút)")
        logger.info("   🕐 MN: 16:20-16:45 VN (mỗi 5 phút)")
    
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