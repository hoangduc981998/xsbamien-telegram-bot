"""Error handler - Xử lý lỗi chung cho toàn bộ bot"""

import logging
import traceback

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lỗi toàn cục"""
    # Log lỗi chi tiết
    logger.error(f"Exception while handling an update: {context.error}")

    # Log traceback để debug
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)
    logger.error(f"Traceback:\n{tb_string}")

    # Thông báo thân thiện cho user
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ <b>Đã xảy ra lỗi!</b>\n\n"
                "Vui lòng thử lại sau hoặc sử dụng lệnh /start để quay lại menu chính.\n\n"
                "💡 Nếu lỗi vẫn tiếp tục, vui lòng liên hệ admin.",
                parse_mode="HTML",
            )
    except Exception as e:
        logger.error(f"Error sending error message: {e}")
