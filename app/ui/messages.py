"""Message templates - Các thông báo đẹp mắt với emoji"""
from datetime import datetime, timedelta
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
    """
    Lịch quay HÔM NAY - Động theo ngày hiện tại
    
    Returns:
        Message hiển thị các đài quay hôm nay với format đẹp
    """
    now = datetime.utcnow()  # UTC time
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    date_str = now.strftime("%d/%m/%Y")
    
    # Day names tiếng Việt
    day_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    day_name = day_names[weekday]
    
    # Chuyển Python weekday (0=Mon) sang SCHEDULE format (0=Sun, 1=Mon...)
    schedule_day = (weekday + 1) % 7
    
    message = f"🔥 <b>HÔM NAY - {day_name}, {date_str}</b>\n\n"
    
    # Miền Nam (16:15 - 16:45)
    mn_codes = SCHEDULE["MN"][schedule_day]
    mn_names = [PROVINCES[code]["name"] for code in mn_codes if code in PROVINCES]
    message += "🟢 <b>Miền Nam</b> (16:15 - 16:45)\n"
    if mn_names:
        message += "  ✅ " + "\n  ✅ ".join(mn_names) + "\n\n"
    else:
        message += "  • Không có\n\n"
    
    # Miền Trung (17:15 - 17:45)
    mt_codes = SCHEDULE["MT"][schedule_day]
    mt_names = [PROVINCES[code]["name"] for code in mt_codes if code in PROVINCES]
    message += "🟠 <b>Miền Trung</b> (17:15 - 17:45)\n"
    if mt_names:
        message += "  ✅ " + "\n  ✅ ".join(mt_names) + "\n\n"
    else:
        message += "  • Không có\n\n"
    
    # Miền Bắc (18:15 - 18:30)
    message += "🔴 <b>Miền Bắc</b> (18:15 - 18:30)\n"
    message += "  ✅ Miền Bắc (hàng ngày)\n\n"
    
    message += "━━━━━━━━━━━━━━━━━━━━\n"
    message += "💡 <i>Nhấn nút bên dưới để xem kết quả</i>"
    
    return message


def get_tomorrow_schedule_message() -> str:
    """
    Lịch quay NGÀY MAI - Động theo ngày mai
    
    Returns:
        Message hiển thị các đài quay ngày mai
    """
    tomorrow = datetime.utcnow() + timedelta(days=1)
    weekday = tomorrow.weekday()
    date_str = tomorrow.strftime("%d/%m/%Y")
    
    day_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    day_name = day_names[weekday]
    
    schedule_day = (weekday + 1) % 7
    
    message = f"📆 <b>NGÀY MAI - {day_name}, {date_str}</b>\n\n"
    
    # Miền Nam
    mn_codes = SCHEDULE["MN"][schedule_day]
    mn_names = [PROVINCES[code]["name"] for code in mn_codes if code in PROVINCES]
    message += "🟢 <b>Miền Nam</b> (16:15 - 16:45)\n"
    if mn_names:
        message += "  • " + "\n  • ".join(mn_names) + "\n\n"
    else:
        message += "  • Không có\n\n"
    
    # Miền Trung
    mt_codes = SCHEDULE["MT"][schedule_day]
    mt_names = [PROVINCES[code]["name"] for code in mt_codes if code in PROVINCES]
    message += "🟠 <b>Miền Trung</b> (17:15 - 17:45)\n"
    if mt_names:
        message += "  • " + "\n  • ".join(mt_names) + "\n\n"
    else:
        message += "  • Không có\n\n"
    
    # Miền Bắc
    message += "🔴 <b>Miền Bắc</b> (18:15 - 18:30)\n"
    message += "  • Miền Bắc (hàng ngày)\n\n"
    
    message += "━━━━━━━━━━━━━━━━━━━━\n"
    message += "💡 <i>Chuẩn bị sẵn số may mắn!</i>"
    
    return message


def get_full_week_schedule_message() -> str:
    """
    Lịch quay CẢ TUẦN - Static, hiển thị đầy đủ
    
    Returns:
        Message lịch quay cả tuần với format đẹp
    """
    message = "📅 <b>LỊCH QUAY THƯỞNG CẢ TUẦN</b>\n\n"
    
    message += "<b>🟢 Miền Nam (16:15 - 16:45)</b>\n"
    message += "• <b>Chủ Nhật:</b> Tiền Giang, Kiên Giang, Đà Lạt\n"
    message += "• <b>Thứ Hai:</b> TP.HCM, Đồng Tháp, Cà Mau\n"
    message += "• <b>Thứ Ba:</b> Bến Tre, Vũng Tàu, Bạc Liêu\n"
    message += "• <b>Thứ Tư:</b> Đồng Nai, Cần Thơ, Sóc Trăng\n"
    message += "• <b>Thứ Năm:</b> Tây Ninh, An Giang, Bình Thuận\n"
    message += "• <b>Thứ Sáu:</b> Vĩnh Long, Bình Dương, Trà Vinh\n"
    message += "• <b>Thứ Bảy:</b> TP.HCM, Long An, Bình Phước, Hậu Giang\n\n"
    
    message += "<b>🟠 Miền Trung (17:15 - 17:45)</b>\n"
    message += "• <b>Chủ Nhật:</b> Huế, Khánh Hòa, Kon Tum\n"
    message += "• <b>Thứ Hai:</b> Huế, Phú Yên\n"
    message += "• <b>Thứ Ba:</b> Quảng Nam, Đắk Lắk\n"
    message += "• <b>Thứ Tư:</b> Đà Nẵng, Khánh Hòa\n"
    message += "• <b>Thứ Năm:</b> Bình Định, Quảng Bình, Quảng Trị\n"
    message += "• <b>Thứ Sáu:</b> Gia Lai, Ninh Thuận\n"
    message += "• <b>Thứ Bảy:</b> Đà Nẵng, Quảng Ngãi, Đắk Nông\n\n"
    
    message += "<b>🔴 Miền Bắc (18:15 - 18:30)</b>\n"
    message += "• <b>Hàng ngày</b> (trừ Tết)\n\n"
    
    message += "━━━━━━━━━━━━━━━━━━━━\n"
    message += "💡 <i>Chúc bạn may mắn!</i>"
    
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
