"""Command handlers - Xử lý các lệnh từ user"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.ui.keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /start - Khởi động bot và lưu user"""
    user = update.effective_user
    logger.info(f"User {user.id} started bot")
    
    # Gửi welcome message
    message = (
        f"👋 Chào mừng <b>{user.first_name}</b>!\n\n"
        "🎰 <b>Bot Xổ Số Ba Miền</b>\n\n"
        "🔹 Xem kết quả mới nhất\n"
        "🔹 Thống kê Lô 2 số, Lô 3 số\n"
        "🔹 Phân tích Đầu/Đuôi Lô\n"
        "🔹 Lô Gan (số lâu không về)\n"
        "🔔 Đăng ký nhận thông báo tự động\n\n"
        "📅 Chọn miền để bắt đầu:"
    )
    
    await update.message.reply_text(
        message,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /help - Hiển thị trợ giúp"""
    message = (
        "📖 <b>HƯỚNG DẪN SỬ DỤNG</b>\n\n"
        "<b>Commands:</b>\n"
        "• /start - Khởi động bot\n"
        "• /help - Xem hướng dẫn\n"
        "• /mb - Xổ số Miền Bắc\n"
        "• /mt - Xổ số Miền Trung\n"
        "• /mn - Xổ số Miền Nam\n"
        "• /subscriptions - Quản lý đăng ký\n"
        "• /testnotify - Test gửi thông báo (admin)\n\n"
        "<b>Tính năng:</b>\n"
        "🎰 Kết quả xổ số mới nhất\n"
        "📊 Thống kê Lô 2 số, Lô 3 số\n"
        "🔢 Phân tích Đầu/Đuôi Lô\n"
        "🔥 Lô Gan (số lâu không về)\n"
        "🔔 Nhận thông báo tự động\n\n"
        "💡 Chọn nút bên dưới để bắt đầu!"
    )
    
    await update.message.reply_text(
        message,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )


async def mb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /mb - Xổ số Miền Bắc"""
    from app.ui.keyboards import get_region_keyboard
    
    message = (
        "🎰 <b>XỔ SỐ MIỀN BẮC</b>\n\n"
        "Chọn tỉnh để xem kết quả:"
    )
    
    await update.message.reply_text(
        message,
        reply_markup=get_region_keyboard("MB"),
        parse_mode="HTML",
    )


async def mt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /mt - Xổ số Miền Trung"""
    from app.ui.keyboards import get_region_keyboard
    
    message = (
        "🎰 <b>XỔ SỐ MIỀN TRUNG</b>\n\n"
        "Chọn tỉnh để xem kết quả:"
    )
    
    await update.message.reply_text(
        message,
        reply_markup=get_region_keyboard("MT"),
        parse_mode="HTML",
    )


async def mn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /mn - Xổ số Miền Nam"""
    from app.ui.keyboards import get_region_keyboard
    
    message = (
        "�� <b>XỔ SỐ MIỀN NAM</b>\n\n"
        "Chọn tỉnh để xem kết quả:"
    )
    
    await update.message.reply_text(
        message,
        reply_markup=get_region_keyboard("MN"),
        parse_mode="HTML",
    )


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
    ADMIN_IDS = [6747306809]  # Thay bằng user ID của bạn
    
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
