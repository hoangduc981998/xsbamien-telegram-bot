"""Command handlers - Xử lý các lệnh /start, /help, /mb, /mt, /mn"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.services.mock_data import get_mock_lottery_result
from app.ui.formatters import format_lottery_result
from app.ui.keyboards import get_main_menu_keyboard
from app.ui.messages import HELP_MESSAGE, WELCOME_MESSAGE

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /start - Hiển thị menu chính"""
    try:
        await update.message.reply_text(
            WELCOME_MESSAGE, reply_markup=get_main_menu_keyboard(), parse_mode="HTML"
        )
        logger.info(f"User {update.effective_user.id} started bot")
    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        await update.message.reply_text("❌ Có lỗi xảy ra. Vui lòng thử lại.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /help - Hiển thị hướng dẫn"""
    try:
        await update.message.reply_text(
            HELP_MESSAGE, reply_markup=get_main_menu_keyboard(), parse_mode="HTML"
        )
        logger.info(f"User {update.effective_user.id} requested help")
    except Exception as e:
        logger.error(f"Error in help_command: {e}")
        await update.message.reply_text("❌ Có lỗi xảy ra. Vui lòng thử lại.")


async def mb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /mb - Kết quả Miền Bắc hôm nay"""
    try:
        # Hiển thị loading
        loading_msg = await update.message.reply_text("⏳ Đang tải kết quả Miền Bắc...")

        # Lấy mock data
        result_data = get_mock_lottery_result("MB")
        formatted_result = format_lottery_result("MB", result_data)

        # Cập nhật message
        await loading_msg.edit_text(formatted_result, parse_mode="HTML")

        logger.info(f"User {update.effective_user.id} requested MB results")
    except Exception as e:
        logger.error(f"Error in mb_command: {e}")
        await update.message.reply_text("❌ Có lỗi xảy ra. Vui lòng thử lại.")


async def mt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /mt - Kết quả Miền Trung hôm nay"""
    try:
        # Hiển thị loading
        loading_msg = await update.message.reply_text(
            "⏳ Đang tải kết quả Miền Trung..."
        )

        # Lấy mock data (DANA - Đà Nẵng làm ví dụ)
        result_data = get_mock_lottery_result("DANA")
        formatted_result = format_lottery_result("DANA", result_data)

        # Cập nhật message
        await loading_msg.edit_text(formatted_result, parse_mode="HTML")

        logger.info(f"User {update.effective_user.id} requested MT results")
    except Exception as e:
        logger.error(f"Error in mt_command: {e}")
        await update.message.reply_text("❌ Có lỗi xảy ra. Vui lòng thử lại.")


async def mn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /mn - Kết quả Miền Nam hôm nay"""
    try:
        # Hiển thị loading
        loading_msg = await update.message.reply_text("⏳ Đang tải kết quả Miền Nam...")

        # Lấy mock data (TPHCM làm ví dụ)
        result_data = get_mock_lottery_result("TPHCM")
        formatted_result = format_lottery_result("TPHCM", result_data)

        # Cập nhật message
        await loading_msg.edit_text(formatted_result, parse_mode="HTML")

        logger.info(f"User {update.effective_user.id} requested MN results")
    except Exception as e:
        logger.error(f"Error in mn_command: {e}")
        await update.message.reply_text("❌ Có lỗi xảy ra. Vui lòng thử lại.")
