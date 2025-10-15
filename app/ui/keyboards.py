"""Keyboard layouts cho Telegram bot"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.config import PROVINCES, SCHEDULE
from app.utils.cache import get_cached_schedule_day


def get_schedule_today_keyboard() -> InlineKeyboardMarkup:
    """
    Lịch quay hôm nay với quick access - Tạo nút ĐỘNG dựa vào ngày hiện tại

    Returns:
        InlineKeyboardMarkup: Keyboard với các tỉnh quay hôm nay
    """
    # Lấy schedule_day từ cache (đã tính weekday conversion)
    schedule_day = get_cached_schedule_day()

    keyboard = []

    # Duyệt qua các miền theo thứ tự MB, MT, MN
    for region in ["MB", "MT", "MN"]:
        region_provinces = SCHEDULE[region].get(schedule_day, [])

        for province_code in region_provinces:
            province_info = PROVINCES.get(province_code)
            if province_info:
                display_name = province_info["name"]

                # Tạo button với tên đầy đủ (không giới hạn ký tự)
                button = InlineKeyboardButton(text=display_name, callback_data=f"result_{province_code}")

                # Thêm button vào hàng mới (2 buttons/hàng)
                if not keyboard or len(keyboard[-1]) == 2:
                    keyboard.append([button])
                else:
                    keyboard[-1].append(button)

    # Thêm nút Back
    keyboard.append([InlineKeyboardButton("🔙 Quay lại", callback_data="back_to_main")])

    return InlineKeyboardMarkup(keyboard)


def get_today_schedule_actions() -> InlineKeyboardMarkup:
    """
    Action buttons sau khi xem lịch hôm nay
    Hiển thị các tỉnh quay hôm nay để xem kết quả nhanh

    Returns:
        InlineKeyboardMarkup: Keyboard với province buttons + navigation
    """
    # Lấy schedule_day từ cache
    schedule_day = get_cached_schedule_day()

    keyboard = []

    # Thêm các tỉnh quay hôm nay (2 buttons/hàng)
    for region in ["MB", "MT", "MN"]:
        region_provinces = SCHEDULE[region].get(schedule_day, [])

        for province_code in region_provinces:
            province_info = PROVINCES.get(province_code)
            if province_info:
                display_name = province_info["name"]

                # Tạo button với tên đầy đủ
                button = InlineKeyboardButton(text=display_name, callback_data=f"result_{province_code}")

                # Thêm vào keyboard (2 buttons/hàng)
                if not keyboard or len(keyboard[-1]) == 2:
                    keyboard.append([button])
                else:
                    keyboard[-1].append(button)

    # Thêm navigation buttons (full width, 1 button/hàng)
    keyboard.append([InlineKeyboardButton("📅 Lịch cả tuần", callback_data="schedule_week")])
    keyboard.append([InlineKeyboardButton("🔙 Quay lại", callback_data="back_to_main")])

    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("🔥 Lịch quay hôm nay", callback_data="schedule_today")],
        [InlineKeyboardButton("📅 Lịch quay cả tuần", callback_data="schedule_week")],
        [InlineKeyboardButton("🔍 Xem kết quả", callback_data="results_menu")],
        [InlineKeyboardButton("ℹ️ Hướng dẫn", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_results_menu_keyboard() -> InlineKeyboardMarkup:
    """Results menu - chọn miền"""
    keyboard = [
        [InlineKeyboardButton("🔴 Miền Bắc", callback_data="results_MB")],
        [InlineKeyboardButton("🟠 Miền Trung", callback_data="results_MT")],
        [InlineKeyboardButton("🟢 Miền Nam", callback_data="results_MN")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_region_provinces_keyboard(region: str) -> InlineKeyboardMarkup:
    """
    Keyboard cho tỉnh trong 1 miền (2 buttons/hàng)

    Args:
        region: Mã miền (MB/MT/MN)
    """
    keyboard = []

    # Lấy tất cả tỉnh của miền
    all_provinces = set()
    for day_provinces in SCHEDULE[region].values():
        all_provinces.update(day_provinces)

    # Sort theo tên hiển thị
    sorted_provinces = sorted(all_provinces, key=lambda x: PROVINCES[x]["name"])

    # Tạo buttons (2 buttons/hàng)
    for province_code in sorted_provinces:
        province_info = PROVINCES.get(province_code)
        if province_info:
            button = InlineKeyboardButton(text=province_info["name"], callback_data=f"result_{province_code}")

            if not keyboard or len(keyboard[-1]) == 2:
                keyboard.append([button])
            else:
                keyboard[-1].append(button)

    # Thêm nút Back
    keyboard.append([InlineKeyboardButton("🔙 Quay lại", callback_data="results_menu")])

    return InlineKeyboardMarkup(keyboard)


def get_back_to_results_keyboard() -> InlineKeyboardMarkup:
    """Keyboard sau khi xem kết quả 1 tỉnh"""
    keyboard = [
        [InlineKeyboardButton("🔙 Chọn tỉnh khác", callback_data="results_menu")],
        [InlineKeyboardButton("🏠 Về trang chủ", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_week_schedule_keyboard() -> InlineKeyboardMarkup:
    """Keyboard cho lịch cả tuần"""
    keyboard = [
        [InlineKeyboardButton("🔥 Xem lịch hôm nay", callback_data="schedule_today")],
        [InlineKeyboardButton("🔍 Xem kết quả", callback_data="results_menu")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Simple back to main menu button"""
    keyboard = [
        [InlineKeyboardButton("🔙 Quay lại menu chính", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_stats_menu_keyboard() -> InlineKeyboardMarkup:
    """Statistics main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Lô 2 Số MB", callback_data="stats_MB_2digit"),
            InlineKeyboardButton("📊 Lô 2 Số MN", callback_data="stats_MN_2digit"),
        ],
        [InlineKeyboardButton("📊 Lô 2 Số MT", callback_data="stats_MT_2digit")],
        [InlineKeyboardButton("📈 Đầu-Đuôi ĐB", callback_data="stats_headtail")],
        [InlineKeyboardButton("❄️ Lô Gan", callback_data="stats_gan")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_province_detail_keyboard(province_key: str) -> InlineKeyboardMarkup:
    """
    Keyboard for province detail view with statistics options
    
    Args:
        province_key: Province code (e.g., TPHCM, DANA, MB)
    """
    keyboard = [
        [
            InlineKeyboardButton("📊 Thống kê Lô 2 số", callback_data=f"stats2_{province_key}"),
            InlineKeyboardButton("📊 Thống kê Lô 3 số", callback_data=f"stats3_{province_key}"),
        ],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="results_menu")],
        [InlineKeyboardButton("🏠 Về trang chủ", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_province_detail_menu(province_key: str) -> InlineKeyboardMarkup:
    """Alias for get_province_detail_keyboard for backward compatibility"""
    return get_province_detail_keyboard(province_key)


def get_region_menu_keyboard(region: str) -> InlineKeyboardMarkup:
    """
    Keyboard for region menu (same as province list)
    
    Args:
        region: Region code (MB, MT, MN)
    """
    return get_region_provinces_keyboard(region)


def get_schedule_menu() -> InlineKeyboardMarkup:
    """Schedule menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("🔥 Lịch hôm nay", callback_data="schedule_today")],
        [InlineKeyboardButton("📅 Lịch cả tuần", callback_data="schedule_week")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_schedule_back_button() -> InlineKeyboardMarkup:
    """Back button for schedule views"""
    keyboard = [
        [InlineKeyboardButton("🔙 Quay lại", callback_data="schedule_menu")],
        [InlineKeyboardButton("🏠 Về trang chủ", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)
