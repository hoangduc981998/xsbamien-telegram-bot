import os
from typing import Dict, List, Optional

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# API Configuration
MU88_API_BASE = "https://mu88.live/api/front/open/lottery/history/list/game"
API_TIMEOUT = 10
API_RETRY_TIMES = 3
API_LIMIT_NUM = 30

# Cache Configuration
CACHE_TYPE = os.getenv("CACHE_TYPE", "sqlite")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = 600  # 10 phút

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://lottery_user:lottery_pass@localhost:5432/lottery_db"
)
USE_DATABASE = os.getenv("USE_DATABASE", "false").lower() == "true"

# Giờ quay thưởng (HH:MM format)
DRAW_TIMES = {
    "MB": {"start": "18:15", "end": "18:30"},
    "MT": {"start": "17:15", "end": "17:45"},
    "MN": {"start": "16:15", "end": "16:45"},
}

# Mapping tỉnh/thành và mã code (36 tỉnh)
PROVINCES = {
    # Miền Bắc
    "MB": {"name": "Miền Bắc", "code": "miba", "region": "MB", "emoji": "🔴"},
    # Miền Nam (21 tỉnh)
    "TPHCM": {"name": "TP. Hồ Chí Minh", "code": "tphc", "region": "MN", "emoji": "🏙️"},
    "BALI": {"name": "Bạc Liêu", "code": "bali", "region": "MN", "emoji": "📍"},
    "BETR": {"name": "Bến Tre", "code": "betr", "region": "MN", "emoji": "📍"},
    "ANGI": {"name": "An Giang", "code": "angi", "region": "MN", "emoji": "📍"},
    "BIDU": {"name": "Bình Dương", "code": "bidu", "region": "MN", "emoji": "📍"},
    "BIPH": {"name": "Bình Phước", "code": "biph", "region": "MN", "emoji": "📍"},
    "BITH": {"name": "Bình Thuận", "code": "bith", "region": "MN", "emoji": "📍"},
    "CAMA": {"name": "Cà Mau", "code": "cama", "region": "MN", "emoji": "📍"},
    "CATH": {"name": "Cần Thơ", "code": "cath", "region": "MN", "emoji": "📍"},
    "DALAT": {"name": "Đà Lạt", "code": "dalat", "region": "MN", "emoji": "📍"},
    "DONA": {"name": "Đồng Nai", "code": "dona", "region": "MN", "emoji": "📍"},
    "DOTH": {"name": "Đồng Tháp", "code": "doth", "region": "MN", "emoji": "📍"},
    "HAGI": {"name": "Hậu Giang", "code": "hagi", "region": "MN", "emoji": "📍"},
    "KIGI": {"name": "Kiên Giang", "code": "kigi", "region": "MN", "emoji": "📍"},
    "LOAN": {"name": "Long An", "code": "loan", "region": "MN", "emoji": "📍"},
    "SOTR": {"name": "Sóc Trăng", "code": "sotr", "region": "MN", "emoji": "📍"},
    "TANI": {"name": "Tây Ninh", "code": "tani", "region": "MN", "emoji": "📍"},
    "TIGI": {"name": "Tiền Giang", "code": "tigi", "region": "MN", "emoji": "📍"},
    "TRVI": {"name": "Trà Vinh", "code": "trvi", "region": "MN", "emoji": "📍"},
    "VILO": {"name": "Vĩnh Long", "code": "vilo", "region": "MN", "emoji": "📍"},
    "VUTA": {"name": "Vũng Tàu", "code": "vuta", "region": "MN", "emoji": "📍"},
    # Miền Trung (14 tỉnh)
    "DANA": {"name": "Đà Nẵng", "code": "dana", "region": "MT", "emoji": "📍"},
    "BIDI": {"name": "Bình Định", "code": "bidi", "region": "MT", "emoji": "📍"},
    "DALAK": {"name": "Đắk Lắk", "code": "dalak", "region": "MT", "emoji": "📍"},
    "DANO": {"name": "Đắk Nông", "code": "dano", "region": "MT", "emoji": "📍"},
    "GILA": {"name": "Gia Lai", "code": "gila", "region": "MT", "emoji": "📍"},
    "KHHO": {"name": "Khánh Hòa", "code": "khho", "region": "MT", "emoji": "📍"},
    "KOTU": {"name": "Kon Tum", "code": "kotu", "region": "MT", "emoji": "📍"},
    "NITH": {"name": "Ninh Thuận", "code": "nith", "region": "MT", "emoji": "📍"},
    "PHYE": {"name": "Phú Yên", "code": "phye", "region": "MT", "emoji": "📍"},
    "QUBI": {"name": "Quảng Bình", "code": "qubi", "region": "MT", "emoji": "📍"},
    "QUNA": {"name": "Quảng Nam", "code": "quna", "region": "MT", "emoji": "📍"},
    "QUNG": {"name": "Quảng Ngãi", "code": "qung", "region": "MT", "emoji": "📍"},
    "QUTR": {"name": "Quảng Trị", "code": "qutr", "region": "MT", "emoji": "📍"},
    "THTH": {"name": "Thừa T. Huế", "code": "thth", "region": "MT", "emoji": "📍"},
}

# Lịch quay số theo ngày (schedule_day: 0=CN, 1=T2, ..., 6=T7)
SCHEDULE = {
    "MB": {
        0: ["MB"],  # Chủ nhật
        1: ["MB"],  # Thứ 2
        2: ["MB"],  # Thứ 3
        3: ["MB"],  # Thứ 4
        4: ["MB"],  # Thứ 5
        5: ["MB"],  # Thứ 6
        6: ["MB"],  # Thứ 7
    },
    "MN": {
        0: ["TIGI", "KIGI", "DALAT"],           # Chủ nhật: Tiền Giang, Kiên Giang, Đà Lạt
        1: ["TPHCM", "DOTH", "CAMA"],           # Thứ 2: TP.HCM, Đồng Tháp, Cà Mau
        2: ["BETR", "VUTA", "BALI"],            # Thứ 3: Bến Tre, Vũng Tàu, Bạc Liêu
        3: ["DONA", "CATH", "SOTR"],            # Thứ 4: Đồng Nai, Cần Thơ, Sóc Trăng
        4: ["TANI", "ANGI", "BITH"],            # Thứ 5: Tây Ninh, An Giang, Bình Thuận
        5: ["VILO", "BIDU", "TRVI"],            # Thứ 6: Vĩnh Long, Bình Dương, Trà Vinh
        6: ["TPHCM", "LOAN", "BIPH", "HAGI"],   # Thứ 7: TP.HCM, Long An, Bình Phước, Hậu Giang
    },
    "MT": {
        0: ["THTH", "KHHO", "KOTU"],            # Chủ nhật: Thừa T.Huế, Khánh Hòa, Kon Tum
        1: ["THTH", "PHYE"],                    # Thứ 2: Thừa T.Huế, Phú Yên
        2: ["QUNA", "DALAK"],                   # Thứ 3: Quảng Nam, Đắk Lắk
        3: ["DANA", "KHHO"],                    # Thứ 4: Đà Nẵng, Khánh Hòa
        4: ["BIDI", "QUBI", "QUTR"],            # Thứ 5: Bình Định, Quảng Bình, Quảng Trị
        5: ["GILA", "NITH"],                    # Thứ 6: Gia Lai, Ninh Thuận
        6: ["DANA", "QUNG", "DANO"],            # Thứ 7: Đà Nẵng, Quảng Ngãi, Đắk Nông
    },
}


def get_province_by_code(code: str) -> Optional[Dict]:
    """Lấy thông tin tỉnh theo code"""
    for key, value in PROVINCES.items():
        if value["code"] == code.lower():
            return value
    return None


def get_provinces_by_region(region: str) -> List[Dict]:
    """Lấy danh sách tỉnh theo miền"""
    return [v for v in PROVINCES.values() if v["region"] == region]
