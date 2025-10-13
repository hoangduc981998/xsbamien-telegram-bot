"""Callback handlers - Xử lý tất cả các callback từ inline buttons"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from app.ui.keyboards import (
    get_main_menu_keyboard,
    get_region_menu_keyboard,
    get_province_detail_keyboard,
    get_stats_menu_keyboard,
    get_back_to_menu_keyboard,
    get_schedule_today_keyboard,
)
from app.ui.messages import (
    WELCOME_MESSAGE,
    HELP_MESSAGE,
    get_schedule_message,
    get_today_schedule_message,
    get_region_message,
)
from app.ui.formatters import (
    format_lottery_result,
    format_stats_2digit,
    format_stats_3digit,
    format_head_tail,
    format_gan,
)
from app.services.mock_data import (
    get_mock_lottery_result,
    get_mock_stats_2digit,
    get_mock_stats_3digit,
)
from app.config import PROVINCES

logger = logging.getLogger(__name__)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tất cả callback queries từ inline buttons"""
    query = update.callback_query
    
    # QUAN TRỌNG: Phản hồi ngay để button phản ứng nhanh
    await query.answer()
    
    callback_data = query.data
    logger.info(f"User {update.effective_user.id} clicked: {callback_data}")
    
    try:
        # Main menu
        if callback_data == "main_menu":
            await query.edit_message_text(
                WELCOME_MESSAGE,
                reply_markup=get_main_menu_keyboard(),
                parse_mode="HTML"
            )
        
        # Help
        elif callback_data == "help":
            await query.edit_message_text(
                HELP_MESSAGE,
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML"
            )
        
        # Lịch quay hôm nay
        elif callback_data == "today":
            message = get_today_schedule_message()
            await query.edit_message_text(
                message,
                reply_markup=get_schedule_today_keyboard(),
                parse_mode="HTML"
            )
        
        # Lịch quay trong tuần
        elif callback_data == "schedule":
            message = get_schedule_message()
            await query.edit_message_text(
                message,
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML"
            )
        
        # Chọn miền (region_MB, region_MT, region_MN)
        elif callback_data.startswith("region_"):
            region = callback_data.split("_")[1]
            message = get_region_message(region)
            await query.edit_message_text(
                message,
                reply_markup=get_region_menu_keyboard(region),
                parse_mode="HTML"
            )
        
        # Chọn tỉnh (province_TPHCM, province_DANA, etc.)
        elif callback_data.startswith("province_"):
            province_key = callback_data.split("_")[1]
            
            if province_key in PROVINCES:
                province = PROVINCES[province_key]
                message = f"{province['emoji']} <b>{province['name'].upper()}</b>\n\n"
                message += "📊 Chọn chức năng bạn muốn xem:"
                
                await query.edit_message_text(
                    message,
                    reply_markup=get_province_detail_keyboard(province_key),
                    parse_mode="HTML"
                )
        
        # Kết quả tỉnh (result_TPHCM, result_DANA, etc.)
        elif callback_data.startswith("result_"):
            province_key = callback_data.split("_")[1]
            
            # Hiển thị loading trước
            await query.edit_message_text("⏳ Đang tải kết quả...")
            
            # Lấy mock data
            result_data = get_mock_lottery_result(province_key)
            formatted_result = format_lottery_result(province_key, result_data)
            
            await query.edit_message_text(
                formatted_result,
                reply_markup=get_province_detail_keyboard(province_key),
                parse_mode="HTML"
            )
        
        # Menu thống kê
        elif callback_data == "stats_menu":
            message = "📊 <b>THỐNG KÊ & PHÂN TÍCH</b>\n\n"
            message += "Chọn loại thống kê bạn muốn xem:"
            
            await query.edit_message_text(
                message,
                reply_markup=get_stats_menu_keyboard(),
                parse_mode="HTML"
            )
        
        # Thống kê lô 2 số theo miền (stats_MB_2digit, stats_MT_2digit, stats_MN_2digit)
        elif callback_data.startswith("stats_") and "_2digit" in callback_data:
            region = callback_data.split("_")[1]
            
            await query.edit_message_text("⏳ Đang tải thống kê...")
            
            stats_data = get_mock_stats_2digit(region)
            formatted_stats = format_stats_2digit(region, stats_data)
            
            await query.edit_message_text(
                formatted_stats,
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML"
            )
        
        # Thống kê lô 2 số theo tỉnh (stats2_TPHCM, etc.)
        elif callback_data.startswith("stats2_"):
            province_key = callback_data.split("_")[1]
            province = PROVINCES.get(province_key, {})
            region = province.get("region", "MN")
            
            await query.edit_message_text("⏳ Đang tải thống kê...")
            
            stats_data = get_mock_stats_2digit(region)
            formatted_stats = format_stats_2digit(region, stats_data)
            
            await query.edit_message_text(
                formatted_stats,
                reply_markup=get_province_detail_keyboard(province_key),
                parse_mode="HTML"
            )
        
        # Thống kê lô 3 số theo tỉnh (stats3_TPHCM, etc.)
        elif callback_data.startswith("stats3_"):
            province_key = callback_data.split("_")[1]
            
            await query.edit_message_text("⏳ Đang tải thống kê...")
            
            stats_data = get_mock_stats_3digit(province_key)
            formatted_stats = format_stats_3digit(province_key, stats_data)
            
            await query.edit_message_text(
                formatted_stats,
                reply_markup=get_province_detail_keyboard(province_key),
                parse_mode="HTML"
            )
        
        # Thống kê đầu-đuôi
        elif callback_data == "stats_headtail":
            await query.edit_message_text("⏳ Đang tải thống kê...")
            
            formatted_stats = format_head_tail()
            
            await query.edit_message_text(
                formatted_stats,
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML"
            )
        
        # Lô gan
        elif callback_data == "stats_gan":
            await query.edit_message_text("⏳ Đang tải thống kê...")
            
            # Mặc định hiển thị Miền Nam
            formatted_stats = format_gan("MN")
            
            await query.edit_message_text(
                formatted_stats,
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML"
            )
        
        # Đăng ký nhắc nhở (subscribe_TPHCM, etc.)
        elif callback_data.startswith("subscribe_"):
            province_key = callback_data.split("_")[1]
            province = PROVINCES.get(province_key, {})
            
            message = f"🔔 <b>ĐĂNG KÝ NHẮC NHỞ</b>\n\n"
            message += f"Bạn muốn nhận thông báo khi có kết quả <b>{province.get('name', '')}</b>?\n\n"
            message += "⚠️ <i>Tính năng đang phát triển...</i>\n"
            message += "Sẽ sớm ra mắt trong phiên bản tiếp theo!"
            
            await query.edit_message_text(
                message,
                reply_markup=get_province_detail_keyboard(province_key),
                parse_mode="HTML"
            )
        
        # Fallback cho các callback chưa xử lý
        else:
            await query.edit_message_text(
                f"⚠️ Chức năng <code>{callback_data}</code> đang phát triển...",
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML"
            )
    
    except Exception as e:
        logger.error(f"Error in button_callback: {e}")
        try:
            await query.edit_message_text(
                "❌ Có lỗi xảy ra. Vui lòng thử lại.",
                reply_markup=get_back_to_menu_keyboard()
            )
        except:
            pass
