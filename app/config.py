import os
from typing import Dict, List

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

# Lịch quay theo ngày trong tuần (0=CN, 6=T7)
SCHEDULE = {
    "MN": {
        0: ["TIGI", "KIGI", "DALAT"],  # Chủ nhật
        1: ["TPHCM", "DOTH", "CAMA"],  # Thứ 2
        2: ["BETR", "VUTA", "BALI"],   # Thứ 3
        3: ["DONA", "CATH", "SOTR"],   # Thứ 4
        4: ["TANI", "ANGI", "BITH"],   # Thứ 5
        5: ["VILO", "BIDU", "TRVI"],   # Thứ 6
        6: ["TPHCM", "LOAN", "BIPH", "HAGI"],  # Thứ 7
    },
    "MT": {
        0: ["THTH", "KHHO", "KOTU"],
        1: ["THTH", "PHYE"],
        2: ["QUNA", "DALAK"],
        3: ["DANA", "KHHO"],
        4: ["BIDI", "QUBI", "QUTR"],
        5: ["GILA", "NITH"],
        6: ["DANA", "QUNG", "DANO"],
    },
    "MB": {
        0: ["MB"], 1: ["MB"], 2: ["MB"], 3: ["MB"],
        4: ["MB"], 5: ["MB"], 6: ["MB"],  # Hàng ngày
    }
}

def get_province_by_code(code: str) -> Dict:
    """Lấy thông tin tỉnh theo code"""
    for key, value in PROVINCES.items():
        if value["code"] == code.lower():
            return value
    return None

def get_provinces_by_region(region: str) -> List[Dict]:
    """Lấy danh sách tỉnh theo miền"""
    return [v for v in PROVINCES.values() if v["region"] == region]
