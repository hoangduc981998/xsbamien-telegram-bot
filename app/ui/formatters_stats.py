# -*- coding: utf-8 -*-
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
            
            # Chọn emoji dựa vào streak
            if streak >= 10:
                emoji = "🔥"
            elif streak >= 7:
                emoji = "🟠"
            elif streak >= 5:
                emoji = "🟡"
            elif streak >= 3:
                emoji = "⭐"
            else:
                emoji = "💫"
            
            result += f"{emoji} {i}. <b>{number}</b> - {streak} kỳ liên tiếp\n"
            result += f"   └ Lần cuối: {end_date}\n"
    else:
        result += "<i>Không có lô nào đạt ngưỡng ≥2 kỳ</i>\n"
    
    result += "\n"
    
    result += "🏆 <b>CHUỖI DÀI NHẤT (Lịch sử 200 kỳ):</b>\n"
    result += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if max_streaks:
        for i, item in enumerate(max_streaks[:10], 1):
            number = item["number"]
            max_streak = item["max_streak"]
            last_date = item["last_streak_date"]
            
            # Chọn emoji dựa vào max_streak
            if max_streak >= 15:
                emoji = "🏆"
            elif max_streak >= 10:
                emoji = "��"
            elif max_streak >= 7:
                emoji = "🥇"
            elif max_streak >= 5:
                emoji = "🥈"
            else:
                emoji = "🥉"
            
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
            
            if streak >= 10:
                emoji = "🔥"
            elif streak >= 7:
                emoji = "🟠"
            elif streak >= 5:
                emoji = "🟡"
            elif streak >= 3:
                emoji = "⭐"
            else:
                emoji = "💫"
            
            result += f"{emoji} {i}. <b>{number}</b> - {streak} kỳ liên tiếp\n"
            result += f"   └ Lần cuối: {end_date}\n"
    else:
        result += "<i>Không có lô nào đạt ngưỡng ≥2 kỳ</i>\n"
    
    result += "\n"
    
    result += "🏆 <b>CHUỖI DÀI NHẤT (Lịch sử 200 kỳ):</b>\n"
    result += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if max_streaks:
        for i, item in enumerate(max_streaks[:10], 1):
            number = item["number"]
            max_streak = item["max_streak"]
            last_date = item["last_streak_date"]
            
            if max_streak >= 15:
                emoji = "🏆"
            elif max_streak >= 10:
                emoji = "💎"
            elif max_streak >= 7:
                emoji = "🥇"
            elif max_streak >= 5:
                emoji = "🥈"
            else:
                emoji = "🥉"
            
            result += f"{emoji} {i}. <b>{number}</b> - {max_streak} kỳ liên tiếp\n"
            result += f"   └ Lần cuối: {last_date}\n"
    else:
        result += "<i>Không có dữ liệu</i>\n"
    
    result += "\n━━━━━━━━━━━━━━━━━━━━\n"
    result += "🔥 Nóng = Đang về liên tiếp\n"
    result += "🏆 Max = Kỷ lục dài nhất\n"
    result += "\n📊 <i>Dữ liệu từ database</i>"
    
    return result
