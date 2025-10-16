"""Result formatters - Format kết quả xổ số với các kiểu hiển thị khác nhau"""


def format_result_mb_full(result_data: dict) -> str:
    """
    Format kết quả XS Miền Bắc - 27 giải đầy đủ

    Args:
        result_data: Dict chứa prizes và date

    Returns:
        Message formatted với HTML
    """
    date = result_data.get("date", "")

    # ✅ FIX: Lấy prizes trực tiếp từ result_data nếu không có key "prizes"
    if "prizes" in result_data:
        prizes = result_data["prizes"]
    else:
        prizes = result_data  # Mock data có G1, G2, ... trực tiếp trong root

    message = "🎰 <b>KẾT QUẢ XỔ SỐ MIỀN BẮC 27 GIẢI</b>\n"
    message += f"📅 Ngày: {date}\n\n"

    # Đặc biệt (1 số, 5 chữ số)
    if "DB" in prizes and prizes["DB"]:
        message += f"🏆 <b>Đặc Biệt:</b> {prizes['DB'][0]}\n"

    # Giải Nhất (1 số, 5 chữ số)
    if "G1" in prizes and prizes["G1"]:
        message += f"🥇 <b>Giải Nhất:</b> {prizes['G1'][0]}\n"

    # Giải Nhì (2 số, 5 chữ số)
    if "G2" in prizes and prizes["G2"]:
        message += f"🥈 <b>Giải Nhì:</b> {','.join(prizes['G2'])}\n"

    # Giải Ba (6 số, 5 chữ số)
    if "G3" in prizes and prizes["G3"]:
        message += f"🥉 <b>Giải Ba:</b> {','.join(prizes['G3'])}\n"

    # Giải Tư (4 số, 4 chữ số)
    if "G4" in prizes and prizes["G4"]:
        message += f"🎖️ <b>Giải Tư:</b> {','.join(prizes['G4'])}\n"

    # Giải Năm (6 số, 4 chữ số)
    if "G5" in prizes and prizes["G5"]:
        message += f"🏅 <b>Giải Năm:</b> {','.join(prizes['G5'])}\n"

    # Giải Sáu (3 số, 3 chữ số)
    if "G6" in prizes and prizes["G6"]:
        message += f"🎗️ <b>Giải Sáu:</b> {','.join(prizes['G6'])}\n"

    # Giải Bảy (4 số, 2 chữ số)
    if "G7" in prizes and prizes["G7"]:
        message += f"🎪 <b>Giải Bảy:</b> {','.join(prizes['G7'])}\n"

    return message


def format_result_mn_mt_full(result_data: dict) -> str:
    """
    Format kết quả XS Miền Nam/Trung - 18 giải đầy đủ
    Thứ tự ngược: G8 → ĐB (từ dưới lên trên)

    Args:
        result_data: Dict chứa prizes, date, và province_name

    Returns:
        Message formatted với HTML
    """
    date = result_data.get("date", "")
    province_name = result_data.get("province", "MIỀN NAM")  # ← Sửa "province_name" thành "province"

    # ✅ FIX: Lấy prizes trực tiếp từ result_data
    if "prizes" in result_data:
        prizes = result_data["prizes"]
    else:
        prizes = result_data

    message = f"🎰 <b>KẾT QUẢ XỔ SỐ {province_name.upper()} 18 GIẢI</b>\n"
    message += f"📅 Ngày: {date}\n\n"

    # Giải Tám (1 số, 2 chữ số)
    if "G8" in prizes and prizes["G8"]:
        message += f"🎊 <b>Giải Tám:</b> {prizes['G8'][0]}\n"

    # Giải Bảy (1 số, 3 chữ số)
    if "G7" in prizes and prizes["G7"]:
        message += f"🎪 <b>Giải Bảy:</b> {prizes['G7'][0]}\n"

    # Giải Sáu (3 số, 4 chữ số)
    if "G6" in prizes and prizes["G6"]:
        message += f"🎗️ <b>Giải Sáu:</b> {','.join(prizes['G6'])}\n"

    # Giải Năm (1 số, 4 chữ số)
    if "G5" in prizes and prizes["G5"]:
        message += f"🏅 <b>Giải Năm:</b> {prizes['G5'][0]}\n"

    # Giải Tư (7 số, 5 chữ số)
    if "G4" in prizes and prizes["G4"]:
        message += f"🎖️ <b>Giải Tư:</b> {','.join(prizes['G4'])}\n"

    # Giải Ba (2 số, 5 chữ số)
    if "G3" in prizes and prizes["G3"]:
        message += f"🥉 <b>Giải Ba:</b> {','.join(prizes['G3'])}\n"

    # Giải Nhì (1 số, 5 chữ số)
    if "G2" in prizes and prizes["G2"]:
        message += f"🥈 <b>Giải Nhì:</b> {prizes['G2'][0]}\n"

    # Giải Nhất (1 số, 5 chữ số)
    if "G1" in prizes and prizes["G1"]:
        message += f"🥇 <b>Giải Nhất:</b> {prizes['G1'][0]}\n"

    # Đặc Biệt (1 số, 6 chữ số)
    if "DB" in prizes and prizes["DB"]:
        message += f"🏆 <b>Đặc Biệt:</b> {prizes['DB'][0]}\n"

    return message


def format_lo_2_so_mb(result_data: dict) -> str:
    """
    Format Lô 2 số Miền Bắc - Lấy 2 chữ số cuối

    Logic:
    - ĐB (5 số): Lấy 2 số cuối
    - G1 (5 số): Lấy 2 số cuối
    - G2-G6: Lấy 2 số cuối mỗi số
    - G7 (2 số): Giữ nguyên (đã là 2 số)
    """
    date = result_data.get("date", "")
    if "prizes" in result_data:
        prizes = result_data["prizes"]
    else:
        prizes = result_data

    message = "🎯 <b>KẾT QUẢ LÔ 2 SỐ</b>\n"
    message += f"📅 Ngày: {date}\n\n"

    # ĐB
    if "DB" in prizes and prizes["DB"]:
        lo2 = prizes["DB"][0][-2:]
        message += f"🏆 <b>ĐB:</b> {lo2}\n"

    # G1
    if "G1" in prizes and prizes["G1"]:
        lo2 = prizes["G1"][0][-2:]
        message += f"🥇 <b>G1:</b> {lo2}\n"

    # G2
    if "G2" in prizes and prizes["G2"]:
        lo2_list = [num[-2:] for num in prizes["G2"]]
        message += f"🥈 <b>G2:</b> {' '.join(lo2_list)}\n"

    # G3
    if "G3" in prizes and prizes["G3"]:
        lo2_list = [num[-2:] for num in prizes["G3"]]
        message += f"🥉 <b>G3:</b> {' '.join(lo2_list)}\n"

    # G4
    if "G4" in prizes and prizes["G4"]:
        lo2_list = [num[-2:] for num in prizes["G4"]]
        message += f"🎖️ <b>G4:</b> {' '.join(lo2_list)}\n"

    # G5
    if "G5" in prizes and prizes["G5"]:
        lo2_list = [num[-2:] for num in prizes["G5"]]
        message += f"🏅 <b>G5:</b> {' '.join(lo2_list)}\n"

    # G6
    if "G6" in prizes and prizes["G6"]:
        lo2_list = [num[-2:] for num in prizes["G6"]]
        message += f"🎗️ <b>G6:</b> {' '.join(lo2_list)}\n"

    # G7
    if "G7" in prizes and prizes["G7"]:
        message += f"🎪 <b>G7:</b> {' '.join(prizes['G7'])}\n"

    return message


def format_lo_2_so_mn_mt(result_data: dict) -> str:
    """
    Format Lô 2 số Miền Nam/Trung - Lấy 2 chữ số cuối
    Thứ tự: G8 → ĐB
    """
    date = result_data.get("date", "")
    if "prizes" in result_data:
        prizes = result_data["prizes"]
    else:
        prizes = result_data

    message = "🎯 <b>KẾT QUẢ LÔ 2 SỐ</b>\n"
    message += f"📅 Ngày: {date}\n\n"

    # G8
    if "G8" in prizes and prizes["G8"]:
        lo2 = prizes["G8"][0][-2:]
        message += f"🎊 <b>G8:</b> {lo2}\n"

    # G7
    if "G7" in prizes and prizes["G7"]:
        lo2 = prizes["G7"][0][-2:]
        message += f"🎪 <b>G7:</b> {lo2}\n"

    # G6
    if "G6" in prizes and prizes["G6"]:
        lo2_list = [num[-2:] for num in prizes["G6"]]
        message += f"🎗️ <b>G6:</b> {' '.join(lo2_list)}\n"

    # G5
    if "G5" in prizes and prizes["G5"]:
        lo2 = prizes["G5"][0][-2:]
        message += f"🏅 <b>G5:</b> {lo2}\n"

    # G4
    if "G4" in prizes and prizes["G4"]:
        lo2_list = [num[-2:] for num in prizes["G4"]]
        message += f"🎖️ <b>G4:</b> {' '.join(lo2_list)}\n"

    # G3
    if "G3" in prizes and prizes["G3"]:
        lo2_list = [num[-2:] for num in prizes["G3"]]
        message += f"🥉 <b>G3:</b> {' '.join(lo2_list)}\n"

    # G2
    if "G2" in prizes and prizes["G2"]:
        lo2 = prizes["G2"][0][-2:]
        message += f"🥈 <b>G2:</b> {lo2}\n"

    # G1
    if "G1" in prizes and prizes["G1"]:
        lo2 = prizes["G1"][0][-2:]
        message += f"🥇 <b>G1:</b> {lo2}\n"

    # ĐB
    if "DB" in prizes and prizes["DB"]:
        lo2 = prizes["DB"][0][-2:]
        message += f"🏆 <b>ĐB:</b> {lo2}\n"

    return message


def format_lo_3_so_mb(result_data: dict) -> str:
    """
    Format Lô 3 số Miền Bắc - Lấy 3 chữ số cuối
    G7 không có (chỉ 2 số)
    """
    date = result_data.get("date", "")
    if "prizes" in result_data:
        prizes = result_data["prizes"]
    else:
        prizes = result_data

    message = "🎯 <b>KẾT QUẢ LÔ 3 SỐ</b>\n"
    message += f"📅 Ngày: {date}\n\n"

    # ĐB
    if "DB" in prizes and prizes["DB"]:
        lo3 = prizes["DB"][0][-3:]
        message += f"🏆 <b>ĐB:</b> {lo3}\n"

    # G1
    if "G1" in prizes and prizes["G1"]:
        lo3 = prizes["G1"][0][-3:]
        message += f"🥇 <b>G1:</b> {lo3}\n"

    # G2
    if "G2" in prizes and prizes["G2"]:
        lo3_list = [num[-3:] for num in prizes["G2"]]
        message += f"🥈 <b>G2:</b> {' '.join(lo3_list)}\n"

    # G3
    if "G3" in prizes and prizes["G3"]:
        lo3_list = [num[-3:] for num in prizes["G3"]]
        message += f"🥉 <b>G3:</b> {' '.join(lo3_list)}\n"

    # G4
    if "G4" in prizes and prizes["G4"]:
        lo3_list = [num[-3:] for num in prizes["G4"]]
        message += f"🎖️ <b>G4:</b> {' '.join(lo3_list)}\n"

    # G5
    if "G5" in prizes and prizes["G5"]:
        lo3_list = [num[-3:] for num in prizes["G5"]]
        message += f"🏅 <b>G5:</b> {' '.join(lo3_list)}\n"

    # G6
    if "G6" in prizes and prizes["G6"]:
        message += f"🎗️ <b>G6:</b> {' '.join(prizes['G6'])}\n"

    # G7 - Không có
    message += "🎪 <b>G7:</b> không có\n"

    return message


def format_lo_3_so_mn_mt(result_data: dict) -> str:
    """
    Format Lô 3 số Miền Nam/Trung - Lấy 3 chữ số cuối
    G8 không có (chỉ 2 số)
    Thứ tự: G8 → ĐB
    """
    date = result_data.get("date", "")
    if "prizes" in result_data:
        prizes = result_data["prizes"]
    else:
        prizes = result_data

    message = "🎯 <b>KẾT QUẢ LÔ 3 SỐ</b>\n"
    message += f"📅 Ngày: {date}\n\n"

    # G8 - Không có
    message += "🎊 <b>G8:</b> Không có\n"

    # G7
    if "G7" in prizes and prizes["G7"]:
        message += f"🎪 <b>G7:</b> {prizes['G7'][0]}\n"

    # G6
    if "G6" in prizes and prizes["G6"]:
        lo3_list = [num[-3:] for num in prizes["G6"]]
        message += f"🎗️ <b>G6:</b> {' '.join(lo3_list)}\n"

    # G5
    if "G5" in prizes and prizes["G5"]:
        lo3 = prizes["G5"][0][-3:]
        message += f"🏅 <b>G5:</b> {lo3}\n"

    # G4
    if "G4" in prizes and prizes["G4"]:
        lo3_list = [num[-3:] for num in prizes["G4"]]
        message += f"🎖️ <b>G4:</b> {' '.join(lo3_list)}\n"

    # G3
    if "G3" in prizes and prizes["G3"]:
        lo3_list = [num[-3:] for num in prizes["G3"]]
        message += f"🥉 <b>G3:</b> {' '.join(lo3_list)}\n"

    # G2
    if "G2" in prizes and prizes["G2"]:
        lo3 = prizes["G2"][0][-3:]
        message += f"🥈 <b>G2:</b> {lo3}\n"

    # G1
    if "G1" in prizes and prizes["G1"]:
        lo3 = prizes["G1"][0][-3:]
        message += f"🥇 <b>G1:</b> {lo3}\n"

    # ĐB
    if "DB" in prizes and prizes["DB"]:
        lo3 = prizes["DB"][0][-3:]
        message += f"🏆 <b>ĐB:</b> {lo3}\n"

    return message


def format_dau_lo(result_data: dict) -> str:
    """
    Thống kê Đầu Lô - Nhóm theo chữ số đầu (0-9)

    Logic:
    1. Lấy tất cả lô 2 số từ các giải
    2. Nhóm theo chữ số đầu
    3. Sắp xếp chữ số đuôi trong mỗi nhóm
    """
    date = result_data.get("date", "")
    if "prizes" in result_data:
        prizes = result_data["prizes"]
    else:
        prizes = result_data

    # Thu thập tất cả lô 2 số
    lo2_list = []

    # Danh sách giải cần xử lý (bao gồm cả G8 cho MN/MT)
    prize_keys = ["DB", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]

    for prize_key in prize_keys:
        if prize_key in prizes and prizes[prize_key]:
            for num in prizes[prize_key]:
                if len(num) >= 2:
                    lo2 = num[-2:]  # Lấy 2 số cuối
                    lo2_list.append(lo2)

    # Nhóm theo đầu
    dau_lo_dict = {i: [] for i in range(10)}

    for lo2 in lo2_list:
        dau = int(lo2[0])  # Chữ số đầu
        duoi = lo2[1]  # Chữ số đuôi
        dau_lo_dict[dau].append(duoi)

    # Sắp xếp
    for key in dau_lo_dict:
        dau_lo_dict[key].sort()

    # Format message
    message = "📊 <b>THỐNG KÊ ĐẦU LÔ</b>\n"
    message += f"📅 Ngày: {date}\n\n"

    for i in range(10):
        if dau_lo_dict[i]:
            duoi_list = ",".join(dau_lo_dict[i])
            message += f"🔢 <b>{i}</b> : {duoi_list}\n"
        else:
            message += f"🔢 <b>{i}</b> : không có\n"

    return message


def format_duoi_lo(result_data: dict) -> str:
    """
    Thống kê Đuôi Lô - Nhóm theo chữ số đuôi (0-9)

    Logic:
    1. Lấy tất cả lô 2 số từ các giải
    2. Nhóm theo chữ số đuôi
    3. Sắp xếp chữ số đầu trong mỗi nhóm
    """
    date = result_data.get("date", "")
    if "prizes" in result_data:
        prizes = result_data["prizes"]
    else:
        prizes = result_data

    # Thu thập tất cả lô 2 số
    lo2_list = []

    prize_keys = ["DB", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]

    for prize_key in prize_keys:
        if prize_key in prizes and prizes[prize_key]:
            for num in prizes[prize_key]:
                if len(num) >= 2:
                    lo2 = num[-2:]
                    lo2_list.append(lo2)

    # Nhóm theo đuôi
    duoi_lo_dict = {i: [] for i in range(10)}

    for lo2 in lo2_list:
        dau = lo2[0]  # Chữ số đầu
        duoi = int(lo2[1])  # Chữ số đuôi
        duoi_lo_dict[duoi].append(dau)

    # Sắp xếp
    for key in duoi_lo_dict:
        duoi_lo_dict[key].sort()

    # Format message
    message = "📊 <b>THỐNG KÊ ĐUÔI LÔ</b>\n"
    message += f"📅 Ngày: {date}\n\n"

    for i in range(10):
        if duoi_lo_dict[i]:
            dau_list = ",".join(duoi_lo_dict[i])
            message += f"🔢 <b>{i}</b> : {dau_list}\n"
        else:
            message += f"🔢 <b>{i}</b> : không có\n"

    return message


# Legacy function - Keep for backward compatibility
def format_lottery_result(result_data: dict, region: str = "MN") -> str:
    """
    Legacy formatter - Giữ để backward compatible
    Redirect to new formatters

    DEBUG VERSION
    """
    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"🔍 format_lottery_result called: region={region}")
    logger.info(f"🔍 result_data keys: {result_data.keys() if isinstance(result_data, dict) else 'NOT A DICT'}")

    if region == "MB":
        logger.info("🔍 Calling format_result_mb_full()")
        result = format_result_mb_full(result_data)
        logger.info(f"🔍 MB result first 100 chars: {result[:100]}")
        return result
    else:
        logger.info("🔍 Calling format_result_mn_mt_full()")
        result = format_result_mn_mt_full(result_data)
        logger.info(f"🔍 MN/MT result first 100 chars: {result[:100]}")
        return result


def format_lo_2_so_stats(stats_data: dict, province_name: str = "") -> str:
    """
    Format Lô 2 Số statistics for display
    
    Args:
        stats_data: Dict from StatisticsService.analyze_lo_2_so()
        province_name: Optional province name override
        
    Returns:
        Formatted HTML message for Telegram
    """
    date = stats_data.get("date", "")
    province = province_name or stats_data.get("province", "")
    all_numbers = stats_data.get("all_numbers", [])
    frequency = stats_data.get("frequency", {})
    
    message = f"📊 <b>THỐNG KÊ LÔ 2 SỐ - {province.upper()}</b>\n"
    message += f"📅 Ngày: {date}\n\n"
    
    if not all_numbers:
        message += "⚠️ Chưa có dữ liệu\n"
        return message
    
    # Show all numbers that appeared
    message += "🎯 <b>Các con số đã về:</b>\n"
    message += ", ".join(all_numbers)
    message += "\n\n"
    
    # Show frequency (top 10)
    if frequency:
        message += "📈 <b>Tần suất xuất hiện:</b>\n"
        sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        for num, count in sorted_freq[:10]:
            if count > 1:
                message += f"• <b>{num}</b>: {count} lần\n"
    
    message += "\n📝 <i>Dữ liệu từ kết quả ngày hôm nay</i>"
    
    return message


def format_lo_3_so_stats(stats_data: dict, province_name: str = "") -> str:
    """
    Format Lô 3 Số statistics for display
    
    Args:
        stats_data: Dict from StatisticsService.analyze_lo_3_so()
        province_name: Optional province name override
        
    Returns:
        Formatted HTML message for Telegram
    """
    date = stats_data.get("date", "")
    province = province_name or stats_data.get("province", "")
    all_numbers = stats_data.get("all_numbers", [])
    frequency = stats_data.get("frequency", {})
    
    message = f"📊 <b>THỐNG KÊ LÔ 3 SỐ (BA CÀNG) - {province.upper()}</b>\n"
    message += f"📅 Ngày: {date}\n\n"
    
    if not all_numbers:
        message += "⚠️ Chưa có dữ liệu\n"
        return message
    
    # Show all 3-digit numbers
    message += "🎯 <b>Các bộ 3 số đã về:</b>\n"
    message += ", ".join(all_numbers)
    message += "\n\n"
    
    # Show frequency
    if frequency:
        message += "📈 <b>Tần suất xuất hiện:</b>\n"
        sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        for num, count in sorted_freq[:10]:
            if count > 1:
                message += f"• <b>{num}</b>: {count} lần\n"
    
    message += "\n📝 <i>Dữ liệu từ kết quả ngày hôm nay</i>"
    
    return message


def format_lo_gan(gan_data: list, province_name: str) -> str:
    """
    Format Lô Gan message với phân loại màu sắc
    
    Args:
        gan_data: List of gan numbers with metadata
        province_name: Province name
        
    Returns:
        Formatted HTML message
    """
    if not gan_data:
        return f"📊 <b>LÔ GAN {province_name.upper()}</b>\n\n⚠️ Chưa có dữ liệu"
    
    # Determine unit and display text based on first item
    is_daily = gan_data[0].get('is_daily', True)
    unit = "ngày" if is_daily else "kỳ"
    analysis_unit = "ngày" if is_daily else "kỳ quay"
    
    # Get window size from data
    window_size = gan_data[0].get('analysis_window', 50)
    
    message = f"📊 <b>LÔ GAN {province_name.upper()}</b>\n"
    message += f"📅 Phân tích {window_size} {analysis_unit} (chỉ số đã từng về)\n\n"
    
    message += "🔢 <b>Top 15 Lô Gan Dài Nhất:</b>\n"
    message += "━━━━━━━━━━━━━━━━━━━━\n"
    
    for i, item in enumerate(gan_data[:15], 1):
        # Icon theo category
        if item["category"] == "cuc_gan":
            icon = "🔴"  # Cực gan
        elif item["category"] == "gan_lon":
            icon = "🟠"  # Gan lớn
        else:
            icon = "🟢"  # Gan thường
        
        value = item['gan_value']
        message += f"{icon} {i:2d}. <code>{item['number']}</code> - "
        message += f"<b>{value}</b> {unit}\n"
        message += f"     └ Lần cuối: {item['last_seen_date']}\n"
        message += f"     └ Gan max: {item['max_cycle']} {unit}\n"
    
    message += "\n━━━━━━━━━━━━━━━━━━━━\n"
    
    # Different thresholds for daily vs periodic draws
    if is_daily:
        message += "🟢 Gan thường (10-15 ngày)\n"
        message += "🟠 Gan lớn (16-20 ngày)\n"
        message += "🔴 Cực gan (21+ ngày)\n"
    else:
        message += "🟢 Gan thường (3-5 kỳ)\n"
        message += "🟠 Gan lớn (6-8 kỳ)\n"
        message += "🔴 Cực gan (9+ kỳ)\n"
    
    message += f"\n💡 <i>Dữ liệu từ database</i>"
    
    return message
