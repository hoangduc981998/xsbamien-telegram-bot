"""Statistics formatters - Format streak analysis results"""


def format_lo_2_so_streaks(streaks_data: dict, province_name: str = "") -> str:
    """Format lô 2 số streak analysis"""
    current = streaks_data.get("current_streaks", [])
    max_streaks = streaks_data.get("max_streaks", [])
    
    province_display = province_name.upper() if province_name else "TỈNH"
    
    result = f"🔥 <b>PHÂN TÍCH CHUỖI LÔ 2 SỐ - {province_display}</b>\n"
    result += f"📊 Dữ liệu: 200 kỳ quay gần nhất\n"
    result += f"📊 Ngưỡng tối thiểu: ≥2 kỳ liên tiếp\n\n"
    
    result += "🔥 <b>LÔ ĐANG 'NÓNG' (Xuất hiện liên tiếp):</b>\n"
    result += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if current:
        for i, item in enumerate(current[:10], 1):
            number = item["number"]
            streak = item["streak"]
            end_date = item["end_date"]
            emoji = "🔥" if streak >= 10 else "🟠" if streak >= 7 else "��"
            result += f"{emoji} {i}. <b>{number}</b> - {streak} kỳ liên tiếp\n"
            result += f"   └ Lần cuối: {end_date}\n"
    else:
        result += "<i>Không có lô nào đạt ngưỡng ≥2 kỳ</i>\n"
    
    result += "\n🏆 <b>CHUỖI DÀI NHẤT (Lịch sử 200 kỳ):</b>\n"
    result += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if max_streaks:
        for i, item in enumerate(max_streaks[:10], 1):
            number = item["number"]
            max_streak = item["max_streak"]
            last_date = item["last_streak_date"]
            emoji = "💎" if max_streak >= 9 else "🥇" if max_streak >= 7 else "🥈"
            result += f"{emoji} {i}. <b>{number}</b> - {max_streak} kỳ liên tiếp\n"
            result += f"   └ Lần cuối: {last_date}\n"
    else:
        result += "<i>Không có dữ liệu</i>\n"
    
    result += "\n━━━━━━━━━━━━━━━━━━━━\n"
    result += "🔥 Nóng = Đang về liên tiếp\n"
    result += "🏆 Max = Kỷ lục dài nhất\n"
    result += "\n📊 <i>Dữ liệu từ database</i>"
    
    return result


def format_lo_3_so_streaks(streaks_data: dict, province_name: str = "") -> str:
    """Format lô 3 số streak analysis"""
    current = streaks_data.get("current_streaks", [])
    max_streaks = streaks_data.get("max_streaks", [])
    
    province_display = province_name.upper() if province_name else "TỈNH"
    
    result = f"🎰 <b>PHÂN TÍCH CHUỖI LÔ 3 SỐ - {province_display}</b>\n"
    result += f"📊 Dữ liệu: 200 kỳ quay gần nhất\n"
    result += f"📊 Ngưỡng tối thiểu: ≥2 kỳ liên tiếp\n\n"
    
    result += "🔥 <b>LÔ ĐANG 'NÓNG' (Xuất hiện liên tiếp):</b>\n"
    result += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if current:
        for i, item in enumerate(current[:10], 1):
            number = item["number"]
            streak = item["streak"]
            end_date = item["end_date"]
            emoji = "🔥" if streak >= 10 else "🟠" if streak >= 7 else "🌟"
            result += f"{emoji} {i}. <b>{number}</b> - {streak} kỳ liên tiếp\n"
            result += f"   └ Lần cuối: {end_date}\n"
    else:
        result += "<i>Không có lô nào đạt ngưỡng ≥2 kỳ</i>\n"
    
    result += "\n🏆 <b>CHUỖI DÀI NHẤT (Lịch sử 200 kỳ):</b>\n"
    result += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if max_streaks:
        for i, item in enumerate(max_streaks[:10], 1):
            number = item["number"]
            max_streak = item["max_streak"]
            last_date = item["last_streak_date"]
            emoji = "💎" if max_streak >= 9 else "🥇" if max_streak >= 7 else "🥈"
            result += f"{emoji} {i}. <b>{number}</b> - {max_streak} kỳ liên tiếp\n"
            result += f"   └ Lần cuối: {last_date}\n"
    else:
        result += "<i>Không có dữ liệu</i>\n"
    
    result += "\n━━━━━━━━━━━━━━━━━━━━\n"
    result += "🔥 Nóng = Đang về liên tiếp\n"
    result += "🏆 Max = Kỷ lục dài nhất\n"
    result += "\n📊 <i>Dữ liệu từ database</i>"
    
    return result
