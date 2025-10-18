"""Individual callback handlers - Extracted from callbacks.py"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from app.ui.messages import WELCOME_MESSAGE
from app.ui.keyboards import (
    get_main_menu_keyboard,
    get_results_menu_keyboard,
    get_subscription_management_keyboard,
)
from app.services.lottery_service import LotteryService
from app.services.subscription_service import SubscriptionService
from app.config import PROVINCES

logger = logging.getLogger(__name__)


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, arg: str = None):
    """Handle back to main menu"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        WELCOME_MESSAGE,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


async def handle_results_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, arg: str = None):
    """Handle results menu"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📊 <b>XEM KẾT QUẢ XỔ SỐ</b>\n\nChọn vùng miền:",
        reply_markup=get_results_menu_keyboard(),
        parse_mode="HTML"
    )


async def handle_result(update: Update, context: ContextTypes.DEFAULT_TYPE, province_code: str):
    """
    Handle result callback
    
    Args:
        province_code: Province code (MB, TPHCM, etc.)
    """
    query = update.callback_query
    await query.answer()
    
    try:
        service = LotteryService(use_database=True)
        result = await service.get_latest_result(province_code)
        
        if result:
            from app.ui.formatters import format_lottery_result
            province_info = PROVINCES.get(province_code, {})
            region = province_info.get("region", "MN")
            
            message = format_lottery_result(result, region)
            
            # Create keyboard with detail buttons
            from app.ui.keyboards import get_province_detail_keyboard
            keyboard = get_province_detail_keyboard(province_code)
            
            await query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await query.edit_message_text(
                f"❌ Chưa có kết quả cho {province_code}",
                reply_markup=get_main_menu_keyboard(),
                parse_mode="HTML"
            )
    except Exception as e:
        logger.exception(f"Error in handle_result for {province_code}")
        await query.edit_message_text(
            "❌ Có lỗi xảy ra. Vui lòng thử lại.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )


async def handle_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
    """
    Handle subscription callbacks
    
    Args:
        action: Action string (e.g., 'confirm_MB', 'cancel_MB', 'manage')
    """
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    if action == "manage":
        # Show subscription management
        service = SubscriptionService()
        subscriptions = await service.get_user_subscriptions(user.id)
        
        # Build message
        if subscriptions:
            msg = "📋 <b>ĐĂNG KÝ CỦA BẠN</b>\n\n"
            for sub in subscriptions:
                province = PROVINCES.get(sub.province_code, {})
                msg += f"✅ {province.get('name', sub.province_code)}\n"
        else:
            msg = "ℹ️ Bạn chưa đăng ký nhận thông báo nào."
        
        await query.edit_message_text(
            msg,
            reply_markup=get_subscription_management_keyboard(user.id),
            parse_mode="HTML"
        )
    
    elif action.startswith("confirm_"):
        province_code = action.replace("confirm_", "")
        service = SubscriptionService()
        
        success = await service.subscribe(user.id, province_code)
        
        if success:
            province = PROVINCES.get(province_code, {})
            msg = f"✅ Đã đăng ký nhận thông báo {province.get('name', province_code)}"
        else:
            msg = "❌ Có lỗi xảy ra. Vui lòng thử lại."
        
        await query.edit_message_text(
            msg,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
    
    elif action.startswith("cancel_"):
        province_code = action.replace("cancel_", "")
        service = SubscriptionService()
        
        success = await service.unsubscribe(user.id, province_code)
        
        if success:
            province = PROVINCES.get(province_code, {})
            msg = f"✅ Đã hủy đăng ký {province.get('name', province_code)}"
        else:
            msg = "❌ Có lỗi xảy ra."
        
        await query.edit_message_text(
            msg,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )


async def handle_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, stat_type: str):
    """
    Handle statistics callbacks
    
    Args:
        stat_type: Type of stats (e.g., '2_MB', '3_TPHCM', 'headtail_MB')
    """
    query = update.callback_query
    await query.answer()
    
    # Parse stat type
    parts = stat_type.split("_", 1)
    if len(parts) != 2:
        await query.edit_message_text(
            "❌ Dữ liệu không hợp lệ",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        return
    
    stat_kind = parts[0]  # '2', '3', 'headtail', etc.
    province_code = parts[1]
    
    try:
        from app.services.db.statistics_db_service import StatisticsDBService
        stats_service = StatisticsDBService()
        
        if stat_kind == "2":
            # Lo 2 so stats
            results = await stats_service.get_lo2so_stats(province_code, limit=200)
            from app.ui.formatters import format_lo2so_stats
            message = format_lo2so_stats(results, province_code)
        
        elif stat_kind == "3":
            # Lo 3 so stats
            results = await stats_service.get_lo3so_stats(province_code, limit=200)
            from app.ui.formatters import format_lo3so_stats
            message = format_lo3so_stats(results, province_code)
        
        elif stat_kind == "headtail":
            # Head/tail stats
            results = await stats_service.get_headtail_stats(province_code)
            from app.ui.formatters import format_headtail_stats
            message = format_headtail_stats(results, province_code)
        
        else:
            message = "❌ Loại thống kê không hợp lệ"
        
        from app.ui.keyboards import get_province_detail_keyboard
        await query.edit_message_text(
            message,
            reply_markup=get_province_detail_keyboard(province_code),
            parse_mode="HTML"
        )
    
    except Exception as e:
        logger.exception(f"Error in handle_stats for {stat_type}")
        await query.edit_message_text(
            "❌ Có lỗi xảy ra khi lấy thống kê",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle unknown callback"""
    query = update.callback_query
    await query.answer("⚠️ Chức năng không tồn tại")
    
    await query.edit_message_text(
        "❌ Chức năng không khả dụng",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
