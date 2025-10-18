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
        await update.message.reply_text(WELCOME_MESSAGE, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
        logger.info(f"User {update.effective_user.id} started bot")
    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        await update.message.reply_text("❌ Có lỗi xảy ra. Vui lòng thử lại.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /help - Hiển thị hướng dẫn"""
    try:
        await update.message.reply_text(HELP_MESSAGE, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
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
        loading_msg = await update.message.reply_text("⏳ Đang tải kết quả Miền Trung...")

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
async def subscriptions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /subscriptions - Quản lý đăng ký"""
    from app.services.subscription_service import SubscriptionService
    from app.ui.keyboards import get_subscription_management_keyboard
    from app.config import PROVINCES
    
    user = update.effective_user
    subscription_service = SubscriptionService()
    
    try:
        subscriptions = await subscription_service.get_user_subscriptions(user.id)
        
        message = "🔔 <b>QUẢN LÝ ĐĂNG KÝ NHẬN THÔNG BÁO</b>\n\n"
        
        if subscriptions:
            message += f"Bạn đang đăng ký <b>{len(subscriptions)}</b> tỉnh:\n\n"
            for sub in subscriptions:
                province = PROVINCES.get(sub.province_code, {})
                message += f"  📍 {province.get('name', sub.province_code)}\n"
            message += "\n❌ Nhấn tỉnh để hủy đăng ký"
        else:
            message += "Bạn chưa đăng ký tỉnh nào\n\n"
            message += "💡 <i>Đăng ký tại menu của từng tỉnh</i>"
        
        await update.message.reply_text(
            message,
            reply_markup=get_subscription_management_keyboard(subscriptions),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error in subscriptions command: {e}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra. Vui lòng thử lại sau!",
            parse_mode="HTML"
        )


async def test_notify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /testnotify - Test gửi thông báo (admin only)"""
    user = update.effective_user
    
    # Admin check
    ADMIN_IDS = [6747306809]  # ID của bạn từ log
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này")
        return
    
    try:
        from app.services.notification_service import NotificationService
        
        notification_service = NotificationService(bot=context.bot)
        
        await update.message.reply_text("📤 Đang gửi thông báo test...")
        
        # Gửi thông báo MB
        summary = await notification_service.send_result_notification("MB")
        
        message = f"📤 <b>TEST GỬI THÔNG BÁO</b>\n\n"
        message += f"📍 Tỉnh: MB (Miền Bắc)\n"
        message += f"📊 Kết quả:\n"
        message += f"  • Tổng subscribers: {summary.get('total', 0)}\n"
        message += f"  • Gửi thành công: ✅ {summary.get('success', 0)}\n"
        message += f"  • Gửi thất bại: ❌ {summary.get('failed', 0)}\n"
        
        if summary.get('error'):
            message += f"\n⚠️ Lỗi: {summary.get('error')}"
        
        await update.message.reply_text(message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in test_notify: {e}")
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")