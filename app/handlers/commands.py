"""Command handlers - Xử lý các lệnh từ user"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.utils.sanitize import sanitize_text, is_valid_province_code
from app.ui.keyboards import get_main_menu_keyboard
from app.config import PROVINCES

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Sanitize username (if exists)
    user_name = sanitize_text(user.first_name) if user else "User"
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
        "💫💫 <b>XỔ SỐ MIỀN NAM</b>\n\n"
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
        logger.exception(f"Error in subscriptions command: {e}")
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
        logger.exception(f"Error in test_notify: {e}")
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")


# ========================================
# ADMIN COMMANDS
# ========================================

ADMIN_IDS = [6747306809]  # Thay bằng user ID của bạn


def is_admin(user_id: int) -> bool:
    """Check xem user có phải admin không"""
    return user_id in ADMIN_IDS


async def admin_dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /admin - Xem admin dashboard"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ Bạn không có quyền truy cập")
        return
    
    try:
        from app.services.admin_service import AdminService
        
        admin_service = AdminService()
        stats = await admin_service.get_dashboard_stats()
        
        if not stats:
            await update.message.reply_text("❌ Không thể lấy thống kê")
            return
        
        # Format message
        message = "📊 <b>ADMIN DASHBOARD</b>\n"
        message += "━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Users & Subscriptions
        message += f"👥 <b>Tổng users đăng ký:</b> {stats['total_users']}\n"
        message += f"📍 <b>Tổng subscriptions:</b> {stats['total_subscriptions']}\n"
        message += f"💫💫 <b>Trung bình:</b> {stats['avg_subs_per_user']} tỉnh/user\n\n"
        
        # Top provinces
        if stats['top_provinces']:
            message += "📈 <b>Top tỉnh được đăng ký:</b>\n"
            for i, prov in enumerate(stats['top_provinces'][:5], 1):
                province_name = PROVINCES.get(prov['code'], {}).get('name', prov['code'])
                message += f"  {i}. {province_name}: <b>{prov['count']}</b> users\n"
            message += "\n"
        
        # Recent subscriptions
        if stats['recent_subscriptions']:
            message += "📅 <b>Đăng ký mới (7 ngày):</b>\n"
            for sub in stats['recent_subscriptions'][:5]:
                message += f"  • {sub['date']}: {sub['count']} đăng ký\n"
            message += "\n"
        
        # Notifications
        notif = stats['notifications']
        if notif['total'] > 0:
            success_rate = (notif['success'] / notif['total'] * 100) if notif['total'] > 0 else 0
            message += "📤 <b>Thông báo đã gửi (30 ngày):</b>\n"
            message += f"  • Tổng: {notif['total']}\n"
            message += f"  • Thành công: ✅ {notif['success']} ({success_rate:.1f}%)\n"
            message += f"  • Thất bại: ❌ {notif['failed']}\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
        
    except Exception as e:
        logger.exception(f"Error in admin_dashboard: {e}")
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")


async def admin_subscribers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /admin_subs - Xem danh sách subscribers"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ Bạn không có quyền truy cập")
        return
    
    try:
        from app.services.admin_service import AdminService
        
        admin_service = AdminService()
        subscribers = await admin_service.get_all_subscribers()
        
        if not subscribers:
            await update.message.reply_text("ℹ️ Chưa có subscriber nào")
            return
        
        message = "👥 <b>DANH SÁCH SUBSCRIBERS</b>\n"
        message += "━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for sub in subscribers:
            username = f"@{sub['username']}" if sub['username'] else f"ID:{sub['user_id']}"
            provinces_str = ', '.join(sub['provinces'])
            message += f"• {username}\n"
            message += f"  📍 {provinces_str} ({sub['count']} tỉnh)\n\n"
        
        message += f"<b>Tổng:</b> {len(subscribers)} users"
        
        await update.message.reply_text(message, parse_mode='HTML')
        
    except Exception as e:
        logger.exception(f"Error in admin_subscribers: {e}")
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")


async def admin_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /broadcast <message> - Gửi thông báo cho tất cả"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ Bạn không có quyền truy cập")
        return
    
    # Lấy message từ command
    if not context.args:
        await update.message.reply_text(
            "📢 <b>SỬ DỤNG:</b>\n\n"
            "<code>/broadcast Nội dung tin nhắn</code>\n\n"
            "Tin nhắn sẽ được gửi đến tất cả users đã đăng ký.",
            parse_mode='HTML'
        )
        return
    
    message_text = ' '.join(context.args)
    
    try:
        from app.services.admin_service import AdminService
        
        admin_service = AdminService()
        
        await update.message.reply_text("📤 Đang gửi broadcast...")
        
        summary = await admin_service.broadcast_message(
            bot=context.bot,
            message=f"📢 <b>THÔNG BÁO</b>\n\n{message_text}"
        )
        
        result_msg = f"📊 <b>KẾT QUẢ BROADCAST</b>\n\n"
        result_msg += f"• Tổng: {summary['total']} users\n"
        result_msg += f"• Thành công: ✅ {summary['success']}\n"
        result_msg += f"• Thất bại: ❌ {summary['failed']}\n"
        
        if summary.get('error'):
            result_msg += f"\n⚠️ Lỗi: {summary['error']}"
        
        await update.message.reply_text(result_msg, parse_mode='HTML')
        
    except Exception as e:
        logger.exception(f"Error in broadcast: {e}")
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")
