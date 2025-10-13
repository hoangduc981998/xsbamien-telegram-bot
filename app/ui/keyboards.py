"""Inline keyboards - Menu và nút bấm đẹp mắt"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.config import PROVINCES, SCHEDULE
from datetime import datetime


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Menu chính - Màn hình đầu tiên khi /start"""
    keyboard = [
        [
            InlineKeyboardButton("🔴 Miền Bắc", callback_data="region_MB"),
            InlineKeyboardButton("🟠 Miền Trung", callback_data="region_MT"),
        ],
        [
            InlineKeyboardButton("🟢 Miền Nam", callback_data="region_MN"),
        ],
        [
            InlineKeyboardButton("📅 Lịch Quay Hôm Nay", callback_data="today"),
            InlineKeyboardButton("📆 Lịch Tuần", callback_data="schedule"),
        ],
        [
            InlineKeyboardButton("📊 Thống Kê", callback_data="stats_menu"),
            InlineKeyboardButton("❓ Trợ Giúp", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_region_menu_keyboard(region: str) -> InlineKeyboardMarkup:
    """Menu chọn tỉnh/thành theo miền"""
    keyboard = []
    
    # Lấy danh sách tỉnh theo miền
    provinces = [(k, v) for k, v in PROVINCES.items() if v["region"] == region]
    
    # Sắp xếp theo tên
    provinces.sort(key=lambda x: x[1]["name"])
    
    # Tạo nút 2 cột
    for i in range(0, len(provinces), 2):
        row = []
        for j in range(2):
            if i + j < len(provinces):
                key, province = provinces[i + j]
                emoji = province["emoji"]
                name = province["name"]
                # Rút gọn tên nếu quá dài
                display_name = name if len(name) <= 15 else name[:12] + "..."
                row.append(
                    InlineKeyboardButton(
                        f"{emoji} {display_name}",
                        callback_data=f"province_{key}"
                    )
                )
        keyboard.append(row)
    
    # Nút quay lại
    keyboard.append([InlineKeyboardButton("◀️ Quay Lại", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


def get_province_detail_keyboard(province_key: str) -> InlineKeyboardMarkup:
    """Menu chi tiết cho từng tỉnh"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Kết Quả Hôm Nay", callback_data=f"result_{province_key}"),
        ],
        [
            InlineKeyboardButton("📈 Thống Kê Lô 2 Số", callback_data=f"stats2_{province_key}"),
            InlineKeyboardButton("📊 Thống Kê Lô 3 Số", callback_data=f"stats3_{province_key}"),
        ],
        [
            InlineKeyboardButton("🔔 Đăng Ký Nhắc Nhở", callback_data=f"subscribe_{province_key}"),
        ],
        [
            InlineKeyboardButton("◀️ Quay Lại", callback_data=f"region_{PROVINCES[province_key]['region']}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_stats_menu_keyboard() -> InlineKeyboardMarkup:
    """Menu thống kê"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Lô 2 Số - Miền Bắc", callback_data="stats_MB_2digit"),
        ],
        [
            InlineKeyboardButton("📊 Lô 2 Số - Miền Trung", callback_data="stats_MT_2digit"),
        ],
        [
            InlineKeyboardButton("📊 Lô 2 Số - Miền Nam", callback_data="stats_MN_2digit"),
        ],
        [
            InlineKeyboardButton("📈 Đầu-Đuôi Giải Đặc Biệt", callback_data="stats_headtail"),
        ],
        [
            InlineKeyboardButton("🎯 Lô Gan (Lâu Về)", callback_data="stats_gan"),
        ],
        [
            InlineKeyboardButton("◀️ Quay Lại", callback_data="main_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Nút quay về menu chính"""
    keyboard = [
        [InlineKeyboardButton("◀️ Quay Lại Menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_schedule_today_keyboard() -> InlineKeyboardMarkup:
    """Lịch quay hôm nay với quick access"""
    weekday = datetime.now().weekday()
    
    keyboard = []
    
    # Thêm các tỉnh quay hôm nay cho từng miền
    for region in ["MB", "MT", "MN"]:
        provinces_today = SCHEDULE[region].get(weekday, [])
        if provinces_today:
            row = []
            for prov_key in provinces_today[:2]:  # Giới hạn 2 tỉnh/hàng
                if prov_key in PROVINCES:
                    emoji = PROVINCES[prov_key]["emoji"]
                    name = PROVINCES[prov_key]["name"]
                    display_name = name if len(name) <= 12 else name[:9] + "..."
                    row.append(
                        InlineKeyboardButton(
                            f"{emoji} {display_name}",
                            callback_data=f"province_{prov_key}"
                        )
                    )
            if row:
                keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("◀️ Quay Lại", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)
