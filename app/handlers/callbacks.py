"""Callback handlers - Xử lý tất cả các callback từ inline buttons"""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from app.ui.keyboards import get_subscription_management_keyboard
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from app.ui.messages import WELCOME_MESSAGE
from app.ui.keyboards import (
    get_main_menu_keyboard,
    get_results_menu_keyboard,
)
from app.database import DatabaseSession

from app.config import PROVINCES
from app.services.lottery_service import LotteryService
from app.services.subscription_service import SubscriptionService
from app.services.beautiful_numbers_service import BeautifulNumbersService
from app.services.statistics_service import StatisticsService
from app.services.mock_data import get_mock_lo_gan
from app.ui.formatters import (
    format_dau_lo,
    format_duoi_lo,
    format_lo_2_so_mb,
    format_lo_2_so_mn_mt,
    format_lo_2_so_stats,
    format_lo_3_so_mb,
    format_lo_3_so_mn_mt,
    format_lo_3_so_stats,
    format_lo_gan,
    format_lottery_result,
    format_result_mb_full,
    format_result_mn_mt_full,
)
from app.ui.keyboards import (
    get_back_to_menu_keyboard,
    get_main_menu_keyboard,
    get_province_detail_keyboard,
    get_province_detail_menu,
    get_region_menu_keyboard,
    get_schedule_back_button,
    get_schedule_menu,
    get_schedule_today_keyboard,
    get_stats_menu_keyboard,
    get_today_schedule_actions,
)
from app.ui.messages import (
    HELP_MESSAGE,
    WELCOME_MESSAGE,
    get_full_week_schedule_message,
    get_region_message,
    get_today_schedule_message,
    get_tomorrow_schedule_message,
)

logger = logging.getLogger(__name__)

# Initialize services
lottery_service = LotteryService(use_database=True)
statistics_service = StatisticsService(use_database=True)

subscription_service = SubscriptionService()

async def safe_edit_message(query, message, reply_markup, parse_mode="HTML"):
    """
    Safely edit message, catching duplicate content errors
    
    Args:
        query: CallbackQuery object
        message: New message text
        reply_markup: New keyboard
        parse_mode: Parse mode (default: HTML)
    """
    try:
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "message is not modified" in error_msg:
            # Message content is same, just answer callback silently
            logger.info(f"Message content unchanged, skipping edit")
        else:
            # Other errors, re-raise
            raise

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tất cả callback queries từ inline buttons"""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    logger.info(f"User {update.effective_user.id} clicked: {callback_data}")

    try:
        # Main menu
        # Back to main menu
        if callback_data == "back_to_main":
            await query.answer()
            
            message = WELCOME_MESSAGE
            keyboard = get_main_menu_keyboard()
            await query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        
        # Results menu
        elif callback_data == "results_menu":
            await query.answer()
            
            message = "🎯 <b>XEM KẾT QUẢ XỔ SỐ</b>\n\n"
            message += "Chọn khu vực để xem kết quả:"
            keyboard = get_results_menu_keyboard()
            await query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        
        # Main menu
        elif callback_data == "main_menu":
            await query.edit_message_text(
                WELCOME_MESSAGE,
                reply_markup=get_main_menu_keyboard(),
                parse_mode="HTML",
            )

        # Help
        elif callback_data == "help":
            await query.edit_message_text(
                HELP_MESSAGE,
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML",
            )

        # Lịch quay hôm nay
        elif callback_data == "today":
            message = get_today_schedule_message()
            await query.edit_message_text(message, reply_markup=get_schedule_today_keyboard(), parse_mode="HTML")

        # Lịch quay trong tuần
        elif callback_data == "schedule":
            await query.edit_message_text(
                "📅 <b>Chọn Xem Lịch Quay</b>\n\nBạn muốn xem lịch của ngày nào?",
                reply_markup=get_schedule_menu(),
                parse_mode="HTML",
            )

        # Quay lại menu lịch
        elif callback_data == "schedule_menu":
            await query.edit_message_text(
                "📅 <b>Chọn Xem Lịch Quay</b>\n\nBạn muốn xem lịch của ngày nào?",
                reply_markup=get_schedule_menu(),
                parse_mode="HTML",
            )

        # Lịch hôm nay (động)
        elif callback_data == "schedule_today":
            await query.edit_message_text(
                get_today_schedule_message(),
                reply_markup=get_today_schedule_actions(),
                parse_mode="HTML",
            )

        # Lịch ngày mai
        elif callback_data == "schedule_tomorrow":
            await query.edit_message_text(
                get_tomorrow_schedule_message(),
                reply_markup=get_schedule_back_button(),
                parse_mode="HTML",
            )

        # Lịch cả tuần
        elif callback_data == "schedule_week":
            await query.edit_message_text(
                get_full_week_schedule_message(),
                reply_markup=get_schedule_back_button(),
                parse_mode="HTML",
            )

        # Chọn miền
        elif callback_data.startswith("region_"):
            region = callback_data.split("_")[1]
            message = get_region_message(region)
            await query.edit_message_text(
                message,
                reply_markup=get_region_menu_keyboard(region),
                parse_mode="HTML",
            )

        # Chọn tỉnh
        elif callback_data.startswith("province_"):
            province_key = callback_data.split("_")[1]

            if province_key in PROVINCES:
                province = PROVINCES[province_key]
                message = f"{province['emoji']} <b>{province['name'].upper()}</b>\n\n"
                message += "📊 Chọn chức năng bạn muốn xem:"

                await query.edit_message_text(
                    message,
                    reply_markup=get_province_detail_menu(province_key),
                    parse_mode="HTML",
                )

        # ✅ THAY ĐỔI: SỬ DỤNG API THẬT
        elif callback_data.startswith("result_") and not callback_data.startswith("result_full_"):
            province_key = callback_data.split("_")[1]

            # Hiển thị loading
            await query.edit_message_text("⏳ Đang tải kết quả từ API...")

            # ✅ GỌI API THẬT
            result_data = await lottery_service.get_latest_result(province_key)

            # Xác định region
            if province_key in ["MB", "MT", "MN"]:
                region = province_key
            else:
                province = PROVINCES.get(province_key, {})
                region = province.get("region", "MN")

            logger.info(f"🔍 province_key={province_key}, region={region}")

            # Format result
            formatted_result = format_lottery_result(result_data, region)

            await query.edit_message_text(
                formatted_result,
                reply_markup=get_province_detail_keyboard(province_key),
                parse_mode="HTML",
            )

        # Menu thống kê
        elif callback_data == "stats_menu":
            message = "📊 <b>THỐNG KÊ & PHÂN TÍCH</b>\n\n"
            message += "Chọn loại thống kê bạn muốn xem:"

            await query.edit_message_text(message, reply_markup=get_stats_menu_keyboard(), parse_mode="HTML")

        # Thống kê lô 2 số theo miền
        elif callback_data.startswith("stats_") and "_2digit" in callback_data:
            region = callback_data.split("_")[1]
            region_names = {"MB": "Miền Bắc", "MT": "Miền Trung", "MN": "Miền Nam"}

            try:
                # Query frequency từ database (50 ngày)
                frequency = await statistics_service.get_frequency_stats(region, days=200)
                
                # Format message
                if frequency:
                    sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:30]
                    
                    message = f"📊 <b>THỐNG KÊ LÔ 2 SỐ - {region_names.get(region, region)}</b>\n"
                    message += f"📅 Dữ liệu: 50 ngày gần nhất từ database\n\n"
                    
                    message += "🔥 <b>Top 30 số hay về:</b>\n"
                    for idx, (num, count) in enumerate(sorted_freq, 1):
                        message += f"  {idx:2d}. <code>{num}</code> - {count:2d} lần\n"
                    
                    message += f"\n💾 Tổng: {len(frequency)} số đã xuất hiện"
                else:
                    message = "⚠️ Chưa có dữ liệu trong database"
                await query.edit_message_text(
                    message,
                    reply_markup=get_back_to_menu_keyboard(),
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.exception(f"Error in stats by region: {e}")
                await query.edit_message_text(
                    f"❌ Lỗi khi lấy thống kê: {str(e)}",
                    reply_markup=get_back_to_menu_keyboard(),
                    parse_mode="HTML",
                )

        # Thống kê lô 2 số - STREAK ANALYSIS
        elif callback_data.startswith("stats2_"):
            province_key = callback_data.split("_")[1]
            province = PROVINCES.get(province_key, {})

            try:
                logger.info(f"Getting lo2so streak analysis for {province_key}")
                
                # Gọi streak analysis
                streaks_data = await statistics_service.get_lo2so_streaks(
                    province_key, 
                    draws=200, 
                    min_streak=2
                )
                
                # Import formatter
                from app.ui.formatters_stats import format_lo_2_so_streaks
                message = format_lo_2_so_streaks(streaks_data, province.get("name", ""))
                
                await safe_edit_message(query, message, get_province_detail_keyboard(province_key))
            except Exception as e:
                logger.exception(f"Error in stats2 for {province_key}: {e}")
                await query.edit_message_text(
                    f"❌ Lỗi: {str(e)}",
                    reply_markup=get_province_detail_keyboard(province_key),
                    parse_mode="HTML",
                )

        # Thống kê lô 3 số - STREAK ANALYSIS
        elif callback_data.startswith("stats3_"):
            province_key = callback_data.split("_")[1]
            province = PROVINCES.get(province_key, {})

            try:
                logger.info(f"Getting lo3so streak analysis for {province_key}")
                
                # Gọi streak analysis
                streaks_data = await statistics_service.get_lo3so_streaks(
                    province_key, 
                    draws=200, 
                    min_streak=2
                )
                
                # Import formatter
                from app.ui.formatters_stats import format_lo_3_so_streaks
                message = format_lo_3_so_streaks(streaks_data, province.get("name", ""))
                
                await safe_edit_message(query, message, get_province_detail_keyboard(province_key))
            except Exception as e:
                logger.exception(f"Error in stats3 for {province_key}: {e}")
                await query.edit_message_text(
                    f"❌ Lỗi: {str(e)}",
                    reply_markup=get_province_detail_keyboard(province_key),
                    parse_mode="HTML",
                )


        # Thống kê đầu-đuôi
        elif callback_data == "stats_headtail":
            try:
                # Get MB result (headtail usually for MB)
                result = await lottery_service.get_latest_result("MB")
                
                # Use existing formatters
                dau_message = format_dau_lo(result)
                duoi_message = format_duoi_lo(result)
                
                # Combine messages
                message = dau_message + "\n\n" + duoi_message
                
                await query.edit_message_text(
                    message,
                    reply_markup=get_back_to_menu_keyboard(),
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.exception(f"Error in stats_headtail: {e}")
                await query.edit_message_text(
                    f"❌ Lỗi khi lấy thống kê: {str(e)}",
                    reply_markup=get_back_to_menu_keyboard(),
                    parse_mode="HTML",
                )
        # Lô gan theo tỉnh
        elif callback_data.startswith("stats_gan_"):
            province_key = callback_data.split("_")[2]
            province = PROVINCES.get(province_key, {})
            
            try:
                # Query lô gan từ database (200 draws)
                logger.info(f"Getting lô gan from DB for {province_key} (200 draws)")
                gan_data = await statistics_service.get_lo_gan(province_key, draws=200, limit=15)
                
                # Format message
                message = format_lo_gan(gan_data, province.get("name", province_key))
                
                await safe_edit_message(query, message, get_province_detail_keyboard(province_key))
            except Exception as e:
                logger.exception(f"Error in stats_gan for {province_key}: {e}")
                await query.edit_message_text(
                    f"❌ Lỗi khi lấy thống kê lô gan: {str(e)}",
                    reply_markup=get_province_detail_keyboard(province_key),
                    parse_mode="HTML",
                )
        
        # Lô gan
        elif callback_data == "stats_gan":
            try:
                # Use REAL DATABASE query (200 draws)
                logger.info(f"Getting lô gan from DB for MB (200 draws)")
                gan_data = await statistics_service.get_lo_gan("MB", draws=200, limit=15)
                
                # Format message
                message = format_lo_gan(gan_data, "Miền Bắc")
                
                await query.edit_message_text(
                    message,
                    reply_markup=get_back_to_menu_keyboard(),
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.exception(f"Error in stats_gan: {e}")
                await query.edit_message_text(
                    f"❌ Lỗi khi lấy thống kê lô gan: {str(e)}",
                    reply_markup=get_back_to_menu_keyboard(),
                    parse_mode="HTML",
                )

        # ✅ KẾT QUẢ ĐẦY ĐỦ - DÙNG API
        elif callback_data.startswith("result_full_"):
            province_code = callback_data.replace("result_full_", "")

            # ✅ GỌI API THẬT
            result_data = await lottery_service.get_latest_result(province_code)

            logger.info(f"🔍 result_full_{province_code}")
            logger.info(f"🔍 result_data keys: {result_data.keys()}")

            # Format theo miền
            if province_code == "MB":
                message = format_result_mb_full(result_data)
            else:
                message = format_result_mn_mt_full(result_data)

            await query.edit_message_text(
                message,
                reply_markup=get_province_detail_menu(province_code),
                parse_mode="HTML",
            )

        # ✅ LÔ 2 SỐ - DÙNG API
        elif callback_data.startswith("lo2_"):
            province_code = callback_data.replace("lo2_", "")

            # ✅ GỌI API THẬT
            result_data = await lottery_service.get_latest_result(province_code)

            # Format theo miền
            if province_code == "MB":
                message = format_lo_2_so_mb(result_data)
            else:
                message = format_lo_2_so_mn_mt(result_data)

            await query.edit_message_text(
                message,
                reply_markup=get_province_detail_menu(province_code),
                parse_mode="HTML",
            )

        # ✅ LÔ 3 SỐ - DÙNG API
        elif callback_data.startswith("lo3_"):
            province_code = callback_data.replace("lo3_", "")

            # ✅ GỌI API THẬT
            result_data = await lottery_service.get_latest_result(province_code)

            # Format theo miền
            if province_code == "MB":
                message = format_lo_3_so_mb(result_data)
            else:
                message = format_lo_3_so_mn_mt(result_data)

            await query.edit_message_text(
                message,
                reply_markup=get_province_detail_menu(province_code),
                parse_mode="HTML",
            )

        # ✅ ĐẦU LÔ - DÙNG API
        elif callback_data.startswith("daulo_"):
            province_code = callback_data.replace("daulo_", "")

            # ✅ GỌI API THẬT
            result_data = await lottery_service.get_latest_result(province_code)
            message = format_dau_lo(result_data)

            await query.edit_message_text(
                message,
                reply_markup=get_province_detail_menu(province_code),
                parse_mode="HTML",
            )

        # ✅ ĐUÔI LÔ - DÙNG API
        elif callback_data.startswith("duoilo_"):
            province_code = callback_data.replace("duoilo_", "")

            # ✅ GỌI API THẬT
            result_data = await lottery_service.get_latest_result(province_code)
            message = format_duoi_lo(result_data)

            await query.edit_message_text(
                message,
                reply_markup=get_province_detail_menu(province_code),
                parse_mode="HTML",
            )

        # Region results (show provinces list)
        elif callback_data == "results_MB":
            from app.ui.keyboards import get_region_provinces_keyboard
            
            message = "🏔️ <b>MIỀN BẮC</b>\n\n"
            message += "Chọn tỉnh để xem kết quả:"
            
            await query.edit_message_text(
                message,
                reply_markup=get_region_provinces_keyboard("MB"),
                parse_mode="HTML",
            )
        
        elif callback_data == "results_MT":
            from app.ui.keyboards import get_region_provinces_keyboard
            
            message = "🏖️ <b>MIỀN TRUNG</b>\n\n"
            message += "Chọn tỉnh để xem kết quả:"
            
            await query.edit_message_text(
                message,
                reply_markup=get_region_provinces_keyboard("MT"),
                parse_mode="HTML",
            )
        
        elif callback_data == "results_MN":
            from app.ui.keyboards import get_region_provinces_keyboard
            
            message = "🌴 <b>MIỀN NAM</b>\n\n"
            message += "Chọn tỉnh để xem kết quả:"
            
            await query.edit_message_text(
                message,
                reply_markup=get_region_provinces_keyboard("MN"),
                parse_mode="HTML",
            )
        # ========== 4 NEW BUTTONS: Quick Stats ==========
        
        elif callback_data.startswith("stats_lo2_"):
            """📊 Lô 2 số button - Quick display"""
            province_code = callback_data.replace("stats_lo2_", "")
            await query.answer()
            
            try:
                result = await lottery_service.get_latest_result(province_code)
                if not result:
                    await query.edit_message_text(
                        text=f"❌ Không tìm thấy kết quả cho {province_code}",
                        reply_markup=get_province_detail_keyboard(province_code),
                        parse_mode=ParseMode.HTML
                    )
                    return
                
                region = result.get('region', 'MN')
                
                if region == 'MB':
                    text = format_lo_2_so_mb(result)
                else:
                    text = format_lo_2_so_mn_mt(result)
                
                await safe_edit_message(query, text, get_province_detail_keyboard(province_code))
            except Exception as e:
                logger.exception(f"Error in stats_lo2: {e}")
                await safe_edit_message(
                    query,
                    "❌ Có lỗi xảy ra",
                    get_province_detail_keyboard(province_code)
                )
        
        elif callback_data.startswith("stats_lo3_"):
            """🎰 Lô 3 số button"""
            province_code = callback_data.replace("stats_lo3_", "")
            await query.answer()
            
            try:
                result = await lottery_service.get_latest_result(province_code)
                if not result:
                    await query.edit_message_text(
                        text=f"❌ Không tìm thấy kết quả cho {province_code}",
                        reply_markup=get_province_detail_keyboard(province_code),
                        parse_mode=ParseMode.HTML
                    )
                    return
                
                region = result.get('region', 'MN')
                
                if region == 'MB':
                    text = format_lo_3_so_mb(result)
                else:
                    text = format_lo_3_so_mn_mt(result)
                
                await safe_edit_message(query, text, get_province_detail_keyboard(province_code))
            except Exception as e:
                logger.exception(f"Error in stats_lo3: {e}")
                await safe_edit_message(
                    query,
                    "❌ Có lỗi xảy ra",
                    get_province_detail_keyboard(province_code)
                )
        
        elif callback_data.startswith("stats_dau_"):
            """🔢 Đầu Lô button"""
            province_code = callback_data.replace("stats_dau_", "")
            await query.answer()
            
            try:
                result = await lottery_service.get_latest_result(province_code)
                if not result:
                    await query.edit_message_text(
                        text=f"❌ Không tìm thấy kết quả cho {province_code}",
                        reply_markup=get_province_detail_keyboard(province_code),
                        parse_mode=ParseMode.HTML
                    )
                    return
                
                text = format_dau_lo(result)
                await safe_edit_message(query, text, get_province_detail_keyboard(province_code))
            except Exception as e:
                logger.exception(f"Error in stats_dau: {e}")
                await safe_edit_message(
                    query,
                    "❌ Có lỗi xảy ra",
                    get_province_detail_keyboard(province_code)
                )
        
        elif callback_data.startswith("stats_duoi_"):
            """🔢 Đuôi Lô button"""
            province_code = callback_data.replace("stats_duoi_", "")
            await query.answer()
            
            try:
                result = await lottery_service.get_latest_result(province_code)
                if not result:
                    await query.edit_message_text(
                        text=f"❌ Không tìm thấy kết quả cho {province_code}",
                        reply_markup=get_province_detail_keyboard(province_code),
                        parse_mode=ParseMode.HTML
                    )
                    return
                
                text = format_duoi_lo(result)
                await safe_edit_message(query, text, get_province_detail_keyboard(province_code))
            except Exception as e:
                logger.exception(f"Error in stats_duoi: {e}")
                await safe_edit_message(
                    query,
                    "❌ Có lỗi xảy ra",
                    get_province_detail_keyboard(province_code)
                )
        # ========== SUBSCRIPTION HANDLERS ==========
        
        elif callback_data.startswith("subscribe_"):
            """🔔 Đăng ký nhận thông báo"""
            province_code = callback_data.replace("subscribe_", "")
            province = PROVINCES.get(province_code, {})
            
            from app.ui.keyboards import get_subscribe_confirm_keyboard
            
            message = f"🔔 <b>ĐĂNG KÝ NHẬN THÔNG BÁO</b>\n\n"
            message += f"📍 Tỉnh: <b>{province.get('name', province_code)}</b>\n\n"
            message += "Bạn sẽ nhận thông báo tự động khi có kết quả mới!\n\n"
            message += "⏰ Thời gian gửi: Sau khi có kết quả chính thức\n"
            message += "🔕 Bạn có thể hủy đăng ký bất kỳ lúc nào\n\n"
            message += "Xác nhận đăng ký?"
            
            await safe_edit_message(
                query,
                message,
                get_subscribe_confirm_keyboard(province_code)
            )
        
        elif callback_data.startswith("confirm_sub_"):
            """✅ Xác nhận đăng ký"""
            province_code = callback_data.replace("confirm_sub_", "")
            province = PROVINCES.get(province_code, {})
            user = update.effective_user
            
            try:
                success = await subscription_service.subscribe(
                    user_id=user.id,
                    province_code=province_code,
                    username=user.username
                )
                
                if success:
                    message = f"✅ <b>ĐĂNG KÝ THÀNH CÔNG!</b>\n\n"
                    message += f"📍 Tỉnh: <b>{province.get('name', province_code)}</b>\n\n"
                    message += "Bạn sẽ nhận thông báo khi có kết quả mới 🎉\n\n"
                    message += "💡 <i>Quản lý đăng ký: /subscriptions</i>"
                else:
                    message = "❌ Có lỗi xảy ra. Vui lòng thử lại sau!"
                
                await safe_edit_message(
                    query,
                    message,
                    get_province_detail_keyboard(province_code)
                )
                
            except Exception as e:
                logger.exception(f"Error confirming subscription: {e}")
                await safe_edit_message(
                    query,
                    "❌ Có lỗi xảy ra. Vui lòng thử lại!",
                    get_province_detail_keyboard(province_code)
                )
        
        elif callback_data.startswith("beautiful_"):
            province_code = callback_data.replace("beautiful_", "")
            await handle_beautiful_numbers_callback(update, context, province_code)
        
        elif callback_data.startswith("unsub_"):
            """❌ Hủy đăng ký"""
            province_code = callback_data.replace("unsub_", "")
            await handle_unsubscribe_callback(update, context, province_code)
            user = update.effective_user

        # Fallback
        else:
            await query.edit_message_text(
                f"⚠️ Chức năng <code>{callback_data}</code> đang phát triển...",
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML",
            )

    except Exception as e:
        logger.exception(f"Error in button_callback: {e}")
        try:
            await query.edit_message_text(
                "❌ Có lỗi xảy ra. Vui lòng thử lại.",
                reply_markup=get_back_to_menu_keyboard(),
            )
        except Exception:
            pass

    async def get_lo_gan(
        self,
        province_code: str,
        days: int = 100,  # Cần 100 ngày để tính gan cực đại
        limit: int = 15
        ) -> list[dict]:
        """
        Get "Lô Gan" (numbers that haven't appeared recently)
        
        Args:
            province_code: Province code (MB, TPHCM, etc.)
            days: Number of days to look back (default: 100 for max cycle)
            limit: Maximum number of results (default: 15)
            
        Returns:
            List of dicts with {
                number, 
                days_since_last,      # Số ngày chưa về
                last_seen_date,       # Lần cuối xuất hiện
                max_cycle,            # Gan cực đại trong lịch sử
                category              # gan_thuong, gan_lon, cuc_gan
            }
        """
        try:
            async with DatabaseSession() as session:
                
                end_date = date.today()
                start_date = end_date - timedelta(days=days)
                
                # Get all numbers 00-99
                all_numbers = [f"{i:02d}" for i in range(100)]
                
                # Query: Get last appearance date for each number
                query = select(
                    Lo2SoHistory.number,
                    func.max(Lo2SoHistory.draw_date).label("last_date")
                ).where(
                    and_(
                        Lo2SoHistory.province_code == province_code,
                        Lo2SoHistory.draw_date >= start_date,
                        Lo2SoHistory.draw_date <= end_date
                    )
                ).group_by(Lo2SoHistory.number)
                
                result = await session.execute(query)
                last_appearances = {row.number: row.last_date for row in result}
                
                # Calculate gan data
                lo_gan = []
                for num in all_numbers:
                    if num in last_appearances:
                        last_date = last_appearances[num]
                        days_since = (end_date - last_date).days
                        
                        # Only include if gan (>= 10 days)
                        if days_since >= 10:
                            # Calculate max cycle (gan cực đại) in history
                            max_cycle_query = select(
                                func.max(
                                    func.julianday(Lo2SoHistory.draw_date) - 
                                    func.lag(func.julianday(Lo2SoHistory.draw_date)).over(
                                        partition_by=Lo2SoHistory.number,
                                        order_by=Lo2SoHistory.draw_date
                                    )
                                ).label("max_gap")
                            ).where(
                                Lo2SoHistory.province_code == province_code,
                                Lo2SoHistory.number == num
                            )
                            
                            max_result = await session.execute(max_cycle_query)
                            max_cycle = max_result.scalar() or days_since
                            max_cycle = int(max_cycle) if max_cycle else days_since
                            
                            # Categorize
                            if days_since >= 21:
                                category = "cuc_gan"
                            elif days_since >= 16:
                                category = "gan_lon"
                            else:
                                category = "gan_thuong"
                            
                            lo_gan.append({
                                "number": num,
                                "days_since_last": days_since,
                                "last_seen_date": last_date.strftime("%d/%m/%Y"),
                                "max_cycle": max_cycle,
                                "category": category
                            })
                    else:
                        # Never appeared in this period
                        lo_gan.append({
                            "number": num,
                            "days_since_last": days,
                            "last_seen_date": "Chưa về",
                            "max_cycle": days,
                            "category": "cuc_gan"
                        })
                
                # Sort by days_since_last (descending)
                lo_gan.sort(key=lambda x: x["days_since_last"], reverse=True)
                
                logger.info(f"✅ Got {len(lo_gan)} lo gan numbers for {province_code}")
                return lo_gan[:limit]
                
        except Exception as e:
            logger.error(f"❌ Error getting lo gan: {e}")
            return []


async def handle_beautiful_numbers_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, province_code: str):
    """Xử lý callback lọc số đẹp"""
    query = update.callback_query
    await query.answer()
    
    try:

        lottery_service = LotteryService(use_database=True)
        beautiful_service = BeautifulNumbersService()
        
        # Gửi loading message
        loading_msg = await query.message.reply_text("⏳ Đang tìm số đẹp...")
        
        # Lấy kết quả
        result = await lottery_service.get_latest_result(province_code)
        
        if not result:
            await loading_msg.edit_text(
                f"❌ Chưa có kết quả mới nhất cho {province_code}",
                parse_mode="HTML"
            )
            return
        
        # Tìm số đẹp
        beautiful_numbers = beautiful_service.find_beautiful_numbers(result)
        
        # Format message
        province = PROVINCES.get(province_code, {})
        province_name = province.get('name', province_code)
        date_str = result.get('date', 'N/A')
        
        message = beautiful_service.format_beautiful_numbers(beautiful_numbers, province_name)
        message += f"\n📅 <b>Ngày:</b> {date_str}"
        
        # Gửi kết quả
        await loading_msg.edit_text(message, parse_mode="HTML")
        
        logger.info(f"✨ Beautiful numbers sent for {province_code}")
        
    except Exception as e:
        logger.exception(f"Error in beautiful numbers callback: {e}")
        try:
            await query.message.reply_text(
                "❌ Có lỗi xảy ra khi tìm số đẹp. Vui lòng thử lại!",
                parse_mode="HTML"
            )
        except:
            pass


async def handle_unsubscribe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, province_code: str):
    """Xử lý hủy đăng ký nhận thông báo"""
    query = update.callback_query
    await query.answer()
    
    try:
        
        user = update.effective_user
        subscription_service = SubscriptionService()
        
        logger.info(f"User {user.id} requesting unsubscribe from {province_code}")
        
        # Hủy đăng ký
        success = await subscription_service.unsubscribe(
            user_id=user.id,
            province_code=province_code
        )
        
        province = PROVINCES.get(province_code, {})
        province_name = province.get('name', province_code)
        
        if success:
            logger.info(f"✅ User {user.id} unsubscribed from {province_code}")
        else:
            logger.warning(f"⚠️ User {user.id} unsubscribe failed for {province_code}")
        
        # Refresh subscription list
        subscriptions = await subscription_service.get_user_subscriptions(user.id)
        
        
        full_message = "🔔 <b>QUẢN LÝ ĐĂNG KÝ</b>\n\n"
        
        if success:
            full_message += f"✅ <b>Đã hủy đăng ký {province_name}</b>\n\n"
        
        if subscriptions:
            full_message += f"Bạn đang đăng ký <b>{len(subscriptions)}</b> tỉnh:\n\n"
            for sub in subscriptions:
                prov = PROVINCES.get(sub.province_code, {})
                full_message += f"  📍 {prov.get('name', sub.province_code)}\n"
            full_message += "\n❌ Nhấn tỉnh để hủy đăng ký"
        else:
            full_message += "Bạn chưa đăng ký tỉnh nào\n\n"
            full_message += "💡 <i>Đăng ký tại menu của từng tỉnh</i>"
        
        await query.edit_message_text(
            full_message,
            reply_markup=get_subscription_management_keyboard(subscriptions),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.exception(f"Error in unsubscribe callback: {e}", exc_info=True)
        try:
            await query.message.reply_text(
                "❌ Có lỗi xảy ra. Vui lòng thử lại!",
                parse_mode="HTML"
            )
        except:
            pass