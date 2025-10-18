"""Entry point - Khởi động bot Telegram"""

import logging

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler
from app.services.scheduler_jobs import SchedulerJobs
from app.config import LOG_LEVEL, TELEGRAM_TOKEN
from app.handlers.callbacks import button_callback
from app.handlers.commands import (
    help_command,
    mb_command,
    mn_command,
    mt_command,
    start_command,
    subscriptions_command,
    test_notify_command,
    admin_dashboard_command,
    admin_subscribers_command,
    admin_broadcast_command
)
from app.handlers.errors import error_handler

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL),
)
logger = logging.getLogger(__name__)


def main():
    """Khởi động bot"""
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN không được thiết lập!")
        return

    logger.info("🚀 Đang khởi động XS Ba Miền Bot...")

    # Tạo application
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Setup scheduler
    scheduler = SchedulerJobs(bot=app.bot)
    scheduler.setup_jobs()
    scheduler.start()
    logger.info("✅ Scheduler started with notification jobs")

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mb", mb_command))
    app.add_handler(CommandHandler("mt", mt_command))
    app.add_handler(CommandHandler("mn", mn_command))
    app.add_handler(CommandHandler("subscriptions", subscriptions_command))
    app.add_handler(CommandHandler("testnotify", test_notify_command))
    # Admin commands
    app.add_handler(CommandHandler("admin", admin_dashboard_command))
    app.add_handler(CommandHandler("admin_subs", admin_subscribers_command))
    app.add_handler(CommandHandler("broadcast", admin_broadcast_command))
    
    # Callback handlers (tất cả nút bấm)
    app.add_handler(CallbackQueryHandler(button_callback))

    # Error handler
    app.add_error_handler(error_handler)

    # Khối code mới cho GRACEFUL SHUTDOWN
    import signal
    import sys
    
    # Cần phải định nghĩa signal_handler trước khi sử dụng
    def signal_handler(sig, frame):
        # Tín hiệu SIGINT (Ctrl+C) hoặc SIGTERM (Lệnh tắt máy chủ)
        logger.info(f"🛑 Received signal {sig}, initiating graceful shutdown...")
        try:
            # 1. Dừng Telegram Application (Ngừng lắng nghe update)
            # Dùng stop() để dừng polling của telegram.ext
            app.stop() 
            
            # 2. Dừng Scheduler
            scheduler.shutdown()
            
            logger.info("✅ Bot shutdown complete.")
        except Exception as e:
            logger.exception(f"Error during shutdown: {e}")
        finally:
            # Thoát chương trình
            sys.exit(0)
    
    # Đăng ký handler cho các tín hiệu dừng
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Khởi động bot
    logger.info("✅ Bot đã khởi động thành công!")
    logger.info("🎯 Đang lắng nghe updates từ Telegram...")

    # Chạy Polling
    try:
        # app.run_polling sẽ chạy cho đến khi app.stop() được gọi
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        # Bắt các lỗi nghiêm trọng không liên quan đến tín hiệu dừng (ví dụ: lỗi mạng)
        logger.exception("❌ Fatal error in main loop. Exiting...")
    
    # Khối logic đã lặp lại và xử lý KeyboardInterrupt cũ đã được loại bỏ.

if __name__ == "__main__":
    main()
