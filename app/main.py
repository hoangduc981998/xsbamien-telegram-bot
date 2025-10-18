"""Main bot application - XS Ba Miền Bot"""

import logging
import signal
import sys
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from app.config import TELEGRAM_TOKEN, LOG_LEVEL
from app.services.scheduler_jobs import SchedulerJobs

# Import command handlers
from app.handlers.commands import (
    start_command,
    help_command,
    mb_command,
    mt_command,
    mn_command,
    subscriptions_command,
    test_notify_command,
    admin_command,
)

# Import callback handlers
from app.handlers.callbacks import button_callback

# Import admin handlers
from app.handlers.admin_handlers import (
    admin_menu,
    admin_backfill_menu,
    admin_backfill,
    admin_stats,
    admin_clear_cache,
)

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL),
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates"""
    logger.error("Exception while handling an update:", exc_info=context.error)


def main():
    """Khởi động bot"""
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN không được thiết lập!")
        return

    logger.info("🚀 Đang khởi động XS Ba Miền Bot...")

    # ====================================
    # TẠO APPLICATION
    # ====================================
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # ====================================
    # SETUP SCHEDULER
    # ====================================
    scheduler = SchedulerJobs(bot=app.bot)
    scheduler.setup_jobs()
    scheduler.start()
    logger.info("✅ Scheduler started with notification jobs")

    # ====================================
    # COMMAND HANDLERS
    # ====================================
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mb", mb_command))
    app.add_handler(CommandHandler("mt", mt_command))
    app.add_handler(CommandHandler("mn", mn_command))
    app.add_handler(CommandHandler("subscriptions", subscriptions_command))
    app.add_handler(CommandHandler("testnotify", test_notify_command))
    
    # ====================================
    # ADMIN COMMANDS
    # ====================================
    app.add_handler(CommandHandler("admin", admin_command))
    # Legacy admin commands (if still needed)
    try:
        from app.handlers.admin import (
            admin_dashboard_command,
            admin_subscribers_command,
            admin_broadcast_command,
        )
        app.add_handler(CommandHandler("admin_dashboard", admin_dashboard_command))
        app.add_handler(CommandHandler("admin_subs", admin_subscribers_command))
        app.add_handler(CommandHandler("broadcast", admin_broadcast_command))
        logger.info("✅ Legacy admin commands registered")
    except ImportError:
        logger.warning("⚠️ Legacy admin commands not found, skipping...")

    # ====================================
    # ADMIN CALLBACK HANDLERS (PHẢI ĐỨNG TRƯỚC!)
    # ====================================
    app.add_handler(CallbackQueryHandler(admin_menu, pattern="^admin_menu$"))
    app.add_handler(CallbackQueryHandler(admin_backfill_menu, pattern="^admin_backfill_menu$"))
    app.add_handler(CallbackQueryHandler(admin_backfill, pattern="^admin_backfill_[A-Z]+$"))
    app.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(admin_clear_cache, pattern="^admin_clear_cache$"))
    
    logger.info("✅ Admin handlers registered")
    
    # ====================================
    # CALLBACK HANDLERS (Catch-all - PHẢI ĐỨNG SAU!)
    # ====================================
    app.add_handler(CallbackQueryHandler(button_callback))
    # ERROR HANDLER
    # ====================================
    app.add_error_handler(error_handler)

    # ====================================
    # GRACEFUL SHUTDOWN HANDLER
    # ====================================
    def signal_handler(sig, frame):
        """Handle shutdown signals (SIGINT, SIGTERM)"""
        logger.info(f"🛑 Received signal {sig}, initiating graceful shutdown...")
        try:
            # 1. Stop Telegram Application
            app.stop()
            logger.info("✅ Telegram application stopped")
            
            # 2. Stop Scheduler
            scheduler.shutdown()
            logger.info("✅ Scheduler stopped")
            
            logger.info("✅ Bot shutdown complete")
        except Exception as e:
            logger.exception(f"❌ Error during shutdown: {e}")
        finally:
            sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Kill signal
    
    # ====================================
    # START BOT
    # ====================================
    logger.info("✅ Bot đã khởi động thành công!")
    logger.info("🎯 Đang lắng nghe updates từ Telegram...")
    logger.info("💡 Press Ctrl+C to stop")
    
    # Start polling
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.exception(f"❌ Fatal error in main loop: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()