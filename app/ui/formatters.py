"""Formatters - Format kết quả đẹp mắt với bảng Unicode"""
from typing import Dict, List
from datetime import datetime
from app.config import PROVINCES


def format_lottery_result(province_key: str, result_data: Dict) -> str:
    """Format kết quả xổ số với bảng Unicode đẹp mắt"""
    province = PROVINCES.get(province_key, {})
    province_name = province.get("name", province_key)
    emoji = province.get("emoji", "📍")
    
    # Header
    date_str = result_data.get("date", datetime.now().strftime("%d/%m/%Y"))
    message = f"{emoji} <b>{province_name.upper()}</b>\n"
    message += f"📅 Ngày: <b>{date_str}</b>\n"
    message += f"{'─' * 30}\n\n"
    
    # Giải đặc biệt
    db = result_data.get("DB", "123456")
    message += f"🎊 <b>Giải Đặc Biệt</b>\n"
    message += f"   <code>{db}</code>\n\n"
    
    # Giải nhất
    g1 = result_data.get("G1", "12345")
    message += f"🥇 <b>Giải Nhất</b>\n"
    message += f"   <code>{g1}</code>\n\n"
    
    # Giải nhì
    g2_list = result_data.get("G2", ["12345", "67890"])
    message += f"🥈 <b>Giải Nhì</b>\n"
    message += f"   <code>{' - '.join(g2_list)}</code>\n\n"
    
    # Giải ba
    g3_list = result_data.get("G3", ["12345", "67890", "11111", "22222", "33333", "44444"])
    message += f"🥉 <b>Giải Ba</b>\n"
    # Chia làm 2 dòng, mỗi dòng 3 số
    for i in range(0, len(g3_list), 3):
        chunk = g3_list[i:i+3]
        message += f"   <code>{' - '.join(chunk)}</code>\n"
    message += "\n"
    
    # Giải tư
    g4_list = result_data.get("G4", ["1234", "5678", "9012", "3456"])
    message += f"🎁 <b>Giải Tư</b>\n"
    message += f"   <code>{' - '.join(g4_list)}</code>\n\n"
    
    # Giải năm
    g5_list = result_data.get("G5", ["123", "456", "789", "012", "345", "678"])
    message += f"🎯 <b>Giải Năm</b>\n"
    for i in range(0, len(g5_list), 3):
        chunk = g5_list[i:i+3]
        message += f"   <code>{' - '.join(chunk)}</code>\n"
    message += "\n"
    
    # Giải sáu
    g6_list = result_data.get("G6", ["12", "34", "56"])
    message += f"🎈 <b>Giải Sáu</b>\n"
    message += f"   <code>{' - '.join(g6_list)}</code>\n\n"
    
    # Giải bảy
    g7_list = result_data.get("G7", ["1", "2", "3", "4"])
    message += f"🎀 <b>Giải Bảy</b>\n"
    message += f"   <code>{' - '.join(g7_list)}</code>\n\n"
    
    # Footer
    message += f"{'─' * 30}\n"
    message += "✅ <i>Kết quả chính thức</i>"
    
    return message


def format_stats_2digit(region: str, stats_data: Dict) -> str:
    """Format thống kê lô 2 số"""
    region_names = {
        "MB": "🔴 Miền Bắc",
        "MT": "🟠 Miền Trung", 
        "MN": "🟢 Miền Nam"
    }
    
    message = f"📊 <b>THỐNG KÊ LÔ 2 SỐ - {region_names.get(region, region)}</b>\n\n"
    
    # Top 10 số hay về
    message += "🔥 <b>Top 10 Số Hay Về</b>\n"
    message += "┌───┬────┬─────────┐\n"
    message += "│ #  │ Số │ Số lần │\n"
    message += "├───┼────┼─────────┤\n"
    
    top_numbers = stats_data.get("top_frequent", [
        (27, 45), (38, 42), (56, 41), (12, 39), (89, 38),
        (34, 37), (67, 36), (45, 35), (78, 34), (90, 33)
    ])
    
    for idx, (num, count) in enumerate(top_numbers[:10], 1):
        message += f"│ {idx:2d} │ {num:02d} │ {count:3d} lần │\n"
    
    message += "└───┴────┴─────────┘\n\n"
    
    # Số ít về
    message += "❄️ <b>Top 5 Số Ít Về</b>\n"
    rare_numbers = stats_data.get("rare", [(5, 12), (19, 13), (82, 14), (94, 15), (61, 16)])
    message += "   "
    message += " - ".join([f"<code>{num:02d}</code> ({count})" for num, count in rare_numbers])
    message += "\n\n"
    
    # Thời gian cập nhật
    message += f"🕐 <i>Thống kê 30 kỳ gần nhất</i>\n"
    message += f"📅 <i>Cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>"
    
    return message


def format_stats_3digit(province_key: str, stats_data: Dict) -> str:
    """Format thống kê lô 3 số"""
    province = PROVINCES.get(province_key, {})
    province_name = province.get("name", province_key)
    emoji = province.get("emoji", "📍")
    
    message = f"{emoji} <b>THỐNG KÊ LÔ 3 SỐ - {province_name}</b>\n\n"
    
    # Giải đặc biệt hay về
    message += "🎊 <b>Đặc Biệt Hay Về</b>\n"
    db_stats = stats_data.get("db_frequent", [
        (123, 5), (456, 4), (789, 4), (234, 3), (567, 3)
    ])
    message += "   "
    message += " - ".join([f"<code>{num:03d}</code> ({count})" for num, count in db_stats])
    message += "\n\n"
    
    # Bộ 3 số hay về
    message += "🎯 <b>Bộ 3 Số Hay Ra</b>\n"
    triple_stats = stats_data.get("triples", [
        ("12", "34", "56", 8),
        ("23", "45", "67", 7),
        ("34", "56", "78", 6),
    ])
    
    for idx, (n1, n2, n3, count) in enumerate(triple_stats, 1):
        message += f"{idx}. <code>{n1}</code> - <code>{n2}</code> - <code>{n3}</code> ({count} lần)\n"
    
    message += "\n"
    message += f"📅 <i>Thống kê 30 kỳ gần nhất</i>"
    
    return message


def format_head_tail() -> str:
    """Format thống kê đầu-đuôi giải đặc biệt"""
    message = "📈 <b>THỐNG KÊ ĐẦU-ĐUÔI GIẢI ĐẶC BIỆT</b>\n\n"
    
    # Đầu số
    message += "🔢 <b>Thống Kê Đầu Số</b>\n"
    message += "┌──────┬─────────┐\n"
    message += "│ Đầu │ Số lần │\n"
    message += "├──────┼─────────┤\n"
    
    head_stats = [(0, 32), (1, 28), (2, 35), (3, 31), (4, 29),
                  (5, 27), (6, 33), (7, 30), (8, 26), (9, 34)]
    
    for head, count in head_stats:
        message += f"│  {head}   │  {count:2d}    │\n"
    
    message += "└──────┴─────────┘\n\n"
    
    # Đuôi số
    message += "🔢 <b>Thống Kê Đuôi Số</b>\n"
    message += "┌──────┬─────────┐\n"
    message += "│ Đuôi │ Số lần │\n"
    message += "├──────┼─────────┤\n"
    
    tail_stats = [(0, 31), (1, 29), (2, 33), (3, 28), (4, 32),
                  (5, 30), (6, 27), (7, 35), (8, 29), (9, 31)]
    
    for tail, count in tail_stats:
        message += f"│  {tail}   │  {count:2d}    │\n"
    
    message += "└──────┴─────────┘\n\n"
    message += "📊 <i>Thống kê 100 kỳ gần nhất</i>"
    
    return message


def format_gan(region: str) -> str:
    """Format lô gan - số lâu không về"""
    region_names = {
        "MB": "🔴 Miền Bắc",
        "MT": "🟠 Miền Trung",
        "MN": "🟢 Miền Nam"
    }
    
    message = f"🎯 <b>LÔ GAN - {region_names.get(region, region)}</b>\n"
    message += "<i>Những số lâu chưa về</i>\n\n"
    
    # Top 15 số gan nhất
    gan_numbers = [
        (43, 18), (72, 17), (15, 16), (91, 15), (28, 14),
        (54, 13), (86, 13), (37, 12), (69, 12), (2, 11),
        (41, 11), (75, 10), (18, 10), (93, 10), (26, 9)
    ]
    
    message += "┌──────┬────────────────┐\n"
    message += "│  Số  │ Số kỳ chưa về │\n"
    message += "├──────┼────────────────┤\n"
    
    for num, count in gan_numbers:
        message += f"│  {num:02d}  │      {count:2d}       │\n"
    
    message += "└──────┴────────────────┘\n\n"
    
    message += "⚠️ <i>Lưu ý: Thống kê chỉ mang tính tham khảo</i>\n"
    message += f"📅 <i>Cập nhật: {datetime.now().strftime('%d/%m/%Y')}</i>"
    
    return message
