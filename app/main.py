"""Entry point - Khởi động bot Telegram"""

import logging

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from app.config import LOG_LEVEL, TELEGRAM_TOKEN
from app.handlers.callbacks import button_callback
from app.handlers.commands import (
    help_command,
    mb_command,
    mn_command,
    mt_command,
    start_command,
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

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mb", mb_command))
    app.add_handler(CommandHandler("mt", mt_command))
    app.add_handler(CommandHandler("mn", mn_command))

    # Callback handlers (tất cả nút bấm)
    app.add_handler(CallbackQueryHandler(button_callback))

    # Error handler
    app.add_error_handler(error_handler)

    # Khởi động bot
    logger.info("✅ Bot đã khởi động thành công!")
    logger.info("🎯 Đang lắng nghe updates từ Telegram...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
