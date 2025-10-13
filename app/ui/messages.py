"""Message templates - Các thông báo đẹp mắt với emoji"""
from datetime import datetime
from app.config import PROVINCES, SCHEDULE, DRAW_TIMES


WELCOME_MESSAGE = """
🎰 <b>Chào mừng đến với XS Ba Miền Bot!</b> 🎰

Bot tra cứu <b>kết quả xổ số nhanh chóng</b> cho cả 3 miền:
🔴 <b>Miền Bắc</b> (1 tỉnh)
🟠 <b>Miền Trung</b> (14 tỉnh)
🟢 <b>Miền Nam</b> (21 tỉnh)

⚡ <b>Tính năng nổi bật:</b>
✅ Kết quả trực tiếp hàng ngày
✅ Thống kê lô 2-3 số chi tiết
✅ Lịch quay thưởng đầy đủ
✅ Đăng ký nhắc nhở thông minh

📱 Chọn miền bạn muốn tra cứu bên dưới!
"""


HELP_MESSAGE = """
❓ <b>Hướng Dẫn Sử Dụng Bot</b>

<b>📋 Lệnh Cơ Bản:</b>
/start - Khởi động bot, hiển thị menu
/help - Xem hướng dẫn này
/mb - Kết quả Miền Bắc hôm nay
/mt - Kết quả Miền Trung hôm nay  
/mn - Kết quả Miền Nam hôm nay

<b>🎯 Cách Sử Dụng:</b>
1️⃣ Chọn miền (Bắc/Trung/Nam)
2️⃣ Chọn tỉnh/thành bạn muốn xem
3️⃣ Xem kết quả hoặc thống kê

<b>📊 Thống Kê:</b>
• <b>Lô 2 số</b>: Thống kê tần suất xuất hiện
• <b>Lô 3 số</b>: Phân tích số 3 chữ số
• <b>Đầu-Đuôi</b>: Thống kê giải đặc biệt
• <b>Lô Gan</b>: Số lâu không về

<b>⏰ Giờ Quay Thưởng:</b>
🟢 Miền Nam: 16:15 - 16:45
🟠 Miền Trung: 17:15 - 17:45
🔴 Miền Bắc: 18:15 - 18:30

💡 <b>Mẹo:</b> Dùng nút bấm để thao tác nhanh hơn!
"""


LOADING_MESSAGE = "⏳ Đang tải dữ liệu, vui lòng chờ..."


ERROR_MESSAGE = """
❌ <b>Có lỗi xảy ra!</b>

Vui lòng thử lại sau hoặc liên hệ admin nếu lỗi vẫn tiếp tục.
"""


NO_DATA_MESSAGE = """
😔 <b>Chưa có dữ liệu</b>

Kết quả sẽ được cập nhật sau khi kỳ quay kết thúc.
"""


def get_schedule_message() -> str:
    """Lịch quay theo tuần đầy đủ"""
    days = ["Chủ Nhật", "Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"]
    today = datetime.now().weekday()
    
    message = "📅 <b>LỊCH QUAY THƯỞNG TRONG TUẦN</b>\n\n"
    
    for day_idx in range(7):
        day_name = days[day_idx]
        is_today = " 👉 <b>HÔM NAY</b>" if day_idx == today else ""
        
        message += f"<b>{day_name}{is_today}</b>\n"
        
        # Miền Bắc
        mb_provinces = SCHEDULE["MB"].get(day_idx, [])
        if mb_provinces:
            message += f"  🔴 <b>Miền Bắc</b>: {', '.join([PROVINCES[p]['name'] for p in mb_provinces if p in PROVINCES])}\n"
        
        # Miền Trung
        mt_provinces = SCHEDULE["MT"].get(day_idx, [])
        if mt_provinces:
            names = [PROVINCES[p]['name'] for p in mt_provinces if p in PROVINCES]
            message += f"  🟠 <b>Miền Trung</b>: {', '.join(names)}\n"
        
        # Miền Nam
        mn_provinces = SCHEDULE["MN"].get(day_idx, [])
        if mn_provinces:
            names = [PROVINCES[p]['name'] for p in mn_provinces if p in PROVINCES]
            message += f"  🟢 <b>Miền Nam</b>: {', '.join(names)}\n"
        
        message += "\n"
    
    message += "\n⏰ <b>Giờ Quay:</b>\n"
    message += f"🟢 Miền Nam: {DRAW_TIMES['MN']['start']} - {DRAW_TIMES['MN']['end']}\n"
    message += f"🟠 Miền Trung: {DRAW_TIMES['MT']['start']} - {DRAW_TIMES['MT']['end']}\n"
    message += f"🔴 Miền Bắc: {DRAW_TIMES['MB']['start']} - {DRAW_TIMES['MB']['end']}\n"
    
    return message


def get_today_schedule_message() -> str:
    """Lịch quay hôm nay"""
    today = datetime.now()
    weekday = today.weekday()
    days = ["Chủ Nhật", "Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"]
    
    message = f"📅 <b>LỊCH QUAY HÔM NAY - {days[weekday].upper()}</b>\n"
    message += f"📆 <i>{today.strftime('%d/%m/%Y')}</i>\n\n"
    
    # Miền Bắc
    mb_provinces = SCHEDULE["MB"].get(weekday, [])
    if mb_provinces:
        names = [PROVINCES[p]['name'] for p in mb_provinces if p in PROVINCES]
        message += f"🔴 <b>Miền Bắc</b> ({DRAW_TIMES['MB']['start']} - {DRAW_TIMES['MB']['end']})\n"
        message += f"   • {', '.join(names)}\n\n"
    
    # Miền Trung
    mt_provinces = SCHEDULE["MT"].get(weekday, [])
    if mt_provinces:
        names = [PROVINCES[p]['name'] for p in mt_provinces if p in PROVINCES]
        message += f"🟠 <b>Miền Trung</b> ({DRAW_TIMES['MT']['start']} - {DRAW_TIMES['MT']['end']})\n"
        message += f"   • {', '.join(names)}\n\n"
    
    # Miền Nam
    mn_provinces = SCHEDULE["MN"].get(weekday, [])
    if mn_provinces:
        names = [PROVINCES[p]['name'] for p in mn_provinces if p in PROVINCES]
        message += f"🟢 <b>Miền Nam</b> ({DRAW_TIMES['MN']['start']} - {DRAW_TIMES['MN']['end']})\n"
        message += f"   • {', '.join(names)}\n\n"
    
    message += "💡 <i>Chọn tỉnh bên dưới để xem kết quả ngay!</i>"
    
    return message


def get_region_message(region: str) -> str:
    """Message khi chọn miền"""
    region_names = {
        "MB": "🔴 Miền Bắc",
        "MT": "🟠 Miền Trung",
        "MN": "🟢 Miền Nam"
    }
    
    region_name = region_names.get(region, region)
    provinces_count = len([p for p in PROVINCES.values() if p["region"] == region])
    
    message = f"<b>{region_name}</b>\n\n"
    message += f"📊 Tổng số: <b>{provinces_count} tỉnh/thành</b>\n"
    message += f"⏰ Giờ quay: <b>{DRAW_TIMES[region]['start']} - {DRAW_TIMES[region]['end']}</b>\n\n"
    message += "👇 Chọn tỉnh/thành bạn muốn xem:"
    
    return message
