"""Callback handlers - Xử lý tất cả các callback từ inline buttons"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.config import PROVINCES
from app.services.lottery_service import LotteryService
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
    get_statistics_buttons_keyboard,
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
            from app.ui.messages import WELCOME_MESSAGE
            from app.ui.keyboards import get_main_menu_keyboard
            
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
            from app.ui.keyboards import get_results_menu_keyboard
            
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
                reply_markup=get_statistics_buttons_keyboard(province_key),
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
                logger.error(f"Error in stats by region: {e}")
                await query.edit_message_text(
                    f"❌ Lỗi khi lấy thống kê: {str(e)}",
                    reply_markup=get_back_to_menu_keyboard(),
                    parse_mode="HTML",
                )

        # Thống kê lô 2 số theo tỉnh
        elif callback_data.startswith("stats2_"):
            province_key = callback_data.split("_")[1]
            province = PROVINCES.get(province_key, {})

            try:
                # Query frequency từ database (50 ngày)
                frequency = await statistics_service.get_frequency_stats(province_key, days=200)
                
                # Format message
                if frequency:
                    sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:30]
                    
                    message = f"📊 <b>THỐNG KÊ LÔ 2 SỐ - {province.get('name', '')}</b>\n"
                    message += f"📅 Dữ liệu: 50 ngày gần nhất từ database\n\n"
                    
                    message += "🔥 <b>Top 30 số hay về:</b>\n"
                    for idx, (num, count) in enumerate(sorted_freq, 1):
                        message += f"  {idx:2d}. <code>{num}</code> - {count:2d} lần\n"
                    
                    message += f"\n💾 Tổng: {len(frequency)} số đã xuất hiện"
                else:
                    message = "⚠️ Chưa có dữ liệu trong database"
                
                await safe_edit_message(query, message, get_province_detail_keyboard(province_key))
            except Exception as e:
                logger.error(f"Error in stats2 for {province_key}: {e}")
                await query.edit_message_text(
                    f"❌ Lỗi khi lấy thống kê: {str(e)}",
                    reply_markup=get_province_detail_keyboard(province_key),
                    parse_mode="HTML",
                )

        # Thống kê lô 3 số theo tỉnh
        elif callback_data.startswith("stats3_"):
            province_key = callback_data.split("_")[1]
            province = PROVINCES.get(province_key, {})

            try:
                # Query frequency từ database (50 ngày)
                frequency = await statistics_service.get_lo3so_frequency_stats(province_key, days=200)
                
                # Format message
                if frequency:
                    sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:30]
                    
                    message = f"📊 <b>THỐNG KÊ LÔ 3 SỐ (BA CÀNG) - {province.get('name', '')}</b>\n"
                    message += f"📅 Dữ liệu: 50 ngày gần nhất từ database\n\n"
                    
                    message += "🔥 <b>Top 30 số hay về:</b>\n"
                    for i, (num, count) in enumerate(sorted_freq, 1):
                        message += f"  {i:2d}. <code>{num}</code> - {count:2d} lần\n"
                    
                    message += f"\n💾 Tổng: {len(frequency)} số đã xuất hiện"
                else:
                    # Fallback to 1-day stats if no database data
                    result = await lottery_service.get_latest_result(province_key)
                    stats = statistics_service.analyze_lo_3_so(result)
                    message = format_lo_3_so_stats(stats, province.get("name", ""))
                    message += "\n\n⚠️ <i>Chưa có dữ liệu dài hạn trong database</i>"
                
                await safe_edit_message(query, message, get_province_detail_keyboard(province_key))
            except Exception as e:
                logger.error(f"Error in stats3 for {province_key}: {e}")
                await query.edit_message_text(
                    f"❌ Lỗi khi lấy thống kê: {str(e)}",
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
                logger.error(f"Error in stats_headtail: {e}")
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
                logger.error(f"Error in stats_gan for {province_key}: {e}")
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
                logger.error(f"Error in stats_gan: {e}")
                await query.edit_message_text(
                    f"❌ Lỗi khi lấy thống kê lô gan: {str(e)}",
                    reply_markup=get_back_to_menu_keyboard(),
                    parse_mode="HTML",
                )

        # Đăng ký nhắc nhở
        elif callback_data.startswith("subscribe_"):
            province_key = callback_data.split("_")[1]
            province = PROVINCES.get(province_key, {})

            message = "🔔 <b>ĐĂNG KÝ NHẮC NHỞ</b>\n\n"
            message += f"Bạn muốn nhận thông báo khi có kết quả <b>{province.get('name', '')}</b>?\n\n"
            message += "⚠️ <i>Tính năng đang phát triển...</i>\n"
            message += "Sẽ sớm ra mắt trong phiên bản tiếp theo!"

            await query.edit_message_text(
                message,
                reply_markup=get_province_detail_keyboard(province_key),
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

        # Fallback

        # ========== NEW: 4 Statistics Buttons ==========
        
        elif callback_data.startswith("stats_lo2_"):
            """📊 Lô 2 số button"""
            province_code = callback_data.replace("stats_lo2_", "")
            await query.answer()
            
            try:
                result = await lottery_service.get_latest_result(province_code)
                if not result:
                    await query.edit_message_text(
                        text=f"❌ Không tìm thấy kết quả cho {province_code}",
                        reply_markup=get_back_to_results_keyboard(),
                        parse_mode=ParseMode.HTML
                    )
                    return
                
                region = result.get('region', 'MN')
                
                if region == 'MB':
                    from app.ui.formatters import format_lo_2_so_mb
                    text = format_lo_2_so_mb(result)
                else:
                    from app.ui.formatters import format_lo_2_so_mn_mt
                    text = format_lo_2_so_mn_mt(result)
                
                keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data=f"result_{province_code}")]]
                
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Error in stats_lo2: {e}")
                await query.edit_message_text(
                    text="❌ Có lỗi xảy ra",
                    reply_markup=get_back_to_results_keyboard(),
                    parse_mode=ParseMode.HTML
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
                        reply_markup=get_back_to_results_keyboard(),
                        parse_mode=ParseMode.HTML
                    )
                    return
                
                region = result.get('region', 'MN')
                
                if region == 'MB':
                    from app.ui.formatters import format_lo_3_so_mb
                    text = format_lo_3_so_mb(result)
                else:
                    from app.ui.formatters import format_lo_3_so_mn_mt
                    text = format_lo_3_so_mn_mt(result)
                
                keyboard = [[InlineKeyboardButton("�� Quay lại", callback_data=f"result_{province_code}")]]
                
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Error in stats_lo3: {e}")
                await query.edit_message_text(
                    text="❌ Có lỗi xảy ra",
                    reply_markup=get_back_to_results_keyboard(),
                    parse_mode=ParseMode.HTML
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
                        reply_markup=get_back_to_results_keyboard(),
                        parse_mode=ParseMode.HTML
                    )
                    return
                
                from app.ui.formatters import format_dau_lo
                text = format_dau_lo(result)
                
                keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data=f"result_{province_code}")]]
                
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Error in stats_dau: {e}")
                await query.edit_message_text(
                    text="❌ Có lỗi xảy ra",
                    reply_markup=get_back_to_results_keyboard(),
                    parse_mode=ParseMode.HTML
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
                        reply_markup=get_back_to_results_keyboard(),
                        parse_mode=ParseMode.HTML
                    )
                    return
                
                from app.ui.formatters import format_duoi_lo
                text = format_duoi_lo(result)
                
                keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data=f"result_{province_code}")]]
                
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Error in stats_duoi: {e}")
                await query.edit_message_text(
                    text="❌ Có lỗi xảy ra",
                    reply_markup=get_back_to_results_keyboard(),
                    parse_mode=ParseMode.HTML
                )

        else:
            await query.edit_message_text(
                f"⚠️ Chức năng <code>{callback_data}</code> đang phát triển...",
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML",
            )

    except Exception as e:
        logger.error(f"Error in button_callback: {e}")
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
                from datetime import datetime, timedelta
                
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