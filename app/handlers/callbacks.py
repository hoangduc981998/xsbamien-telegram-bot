"""Callback handlers - Xử lý tất cả các callback từ inline buttons"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.config import PROVINCES
from app.services.lottery_service import LotteryService  # ← THÊM IMPORT MỚI
from app.ui.formatters import (
    format_dau_lo,
    format_duoi_lo,
    format_lo_2_so_mb,
    format_lo_2_so_mn_mt,
    format_lo_3_so_mb,
    format_lo_3_so_mn_mt,
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

# ← KHỞI TẠO SERVICE
lottery_service = LotteryService()


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tất cả callback queries từ inline buttons"""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    logger.info(f"User {update.effective_user.id} clicked: {callback_data}")

    try:
        # Main menu
        if callback_data == "main_menu":
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

            await query.edit_message_text(
                f"📊 <b>Thống Kê Lô 2 Số - {region_names.get(region, region)}</b>\n\n"
                "🚧 Tính năng đang được phát triển.\n"
                "💡 Sẽ sớm cập nhật trong phiên bản tiếp theo!",
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML",
            )

        # Thống kê lô 2 số theo tỉnh
        elif callback_data.startswith("stats2_"):
            province_key = callback_data.split("_")[1]
            province = PROVINCES.get(province_key, {})

            await query.edit_message_text(
                f"📊 <b>Thống Kê Lô 2 Số - {province.get('name', '')}</b>\n\n"
                "🚧 Tính năng đang được phát triển.\n"
                "💡 Sẽ sớm cập nhật trong phiên bản tiếp theo!",
                reply_markup=get_province_detail_keyboard(province_key),
                parse_mode="HTML",
            )

        # Thống kê lô 3 số theo tỉnh
        elif callback_data.startswith("stats3_"):
            province_key = callback_data.split("_")[1]
            province = PROVINCES.get(province_key, {})

            await query.edit_message_text(
                f"📊 <b>Thống Kê Lô 3 Số - {province.get('name', '')}</b>\n\n"
                "🚧 Tính năng đang được phát triển.\n"
                "�� Sẽ sớm cập nhật trong phiên bản tiếp theo!",
                reply_markup=get_province_detail_keyboard(province_key),
                parse_mode="HTML",
            )

        # Thống kê đầu-đuôi
        elif callback_data == "stats_headtail":
            await query.edit_message_text(
                "📊 <b>Thống Kê Đầu-Đuôi Giải Đặc Biệt</b>\n\n"
                "🚧 Tính năng đang được phát triển.\n"
                "💡 Sẽ sớm cập nhật trong phiên bản tiếp theo!",
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="HTML",
            )

        # Lô gan
        elif callback_data == "stats_gan":
            await query.edit_message_text(
                "📊 <b>Thống Kê Lô Gan (Lâu Về)</b>\n\n"
                "🚧 Tính năng đang được phát triển.\n"
                "💡 Sẽ sớm cập nhật trong phiên bản tiếp theo!",
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

        # Fallback
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
