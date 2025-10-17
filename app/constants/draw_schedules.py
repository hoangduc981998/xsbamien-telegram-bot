"""
Draw schedules for all provinces
Based on official lottery schedule from Vietnam
"""

# Weekday mapping: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday

PROVINCE_DRAW_SCHEDULE = {
    # Miền Bắc - daily
    'MB': [0, 1, 2, 3, 4, 5, 6],  # Every day (18h15-18h30)

    # ========== MIỀN NAM (16h15-16h45) ==========
    
    # Chủ nhật (Sunday)
    'TIGI': [6],        # Tiền Giang
    'KIGI': [6],        # Kiên Giang
    'DALAT': [6],       # Đà Lạt (Lâm Đồng)
    
    # Thứ 2 (Monday)
    'TPHCM': [0, 5],    # TP.HCM (Thứ 2 & Thứ 7) - 2 lần/tuần
    'DOTH': [0],        # Đồng Tháp
    'CAMA': [0],        # Cà Mau
    
    # Thứ 3 (Tuesday)
    'BETR': [1],        # Bến Tre
    'VUTA': [1],        # Vũng Tàu
    'BALI': [1],        # Bạc Liêu
    
    # Thứ 4 (Wednesday)
    'DONA': [2],        # Đồng Nai
    'CATH': [2],        # Cần Thơ
    'SOTR': [2],        # Sóc Trăng
    
    # Thứ 5 (Thursday)
    'TANI': [3],        # Tây Ninh
    'ANGI': [3],        # An Giang
    'BITH': [3],        # Bình Thuận
    
    # Thứ 6 (Friday)
    'VILO': [4],        # Vĩnh Long
    'BIDU': [4],        # Bình Dương
    'TRVI': [4],        # Trà Vinh
    
    # Thứ 7 (Saturday)
    # TPHCM already listed above (2 draws/week)
    'LOAN': [5],        # Long An
    'BIPH': [5],        # Bình Phước
    'HAGI': [5],        # Hậu Giang

    # ========== MIỀN TRUNG (17h15-17h45) ==========
    
    # Chủ nhật (Sunday)
    'THTH': [0, 6],     # Thừa Thiên Huế (Thứ 2 & CN) - 2 lần/tuần
    'KHHO': [2, 6],     # Khánh Hòa (Thứ 4 & CN) - 2 lần/tuần
    'KOTU': [6],        # Kon Tum
    
    # Thứ 2 (Monday)
    # THTH already listed above (2 draws/week)
    'PHYE': [0],        # Phú Yên
    
    # Thứ 3 (Tuesday)
    'QUNA': [1],        # Quảng Nam
    'DALAK': [1],       # Đắk Lắk
    
    # Thứ 4 (Wednesday)
    'DANA': [2, 5],     # Đà Nẵng (Thứ 4 & Thứ 7) - 2 lần/tuần
    # KHHO already listed above (2 draws/week)
    
    # Thứ 5 (Thursday)
    'BIDI': [3],        # Bình Định
    'QUBI': [3],        # Quảng Bình
    'QUTR': [3],        # Quảng Trị
    
    # Thứ 6 (Friday)
    'GILA': [4],        # Gia Lai
    'NITH': [4],        # Ninh Thuận
    
    # Thứ 7 (Saturday)
    # DANA already listed above (2 draws/week)
    'QUNG': [5],        # Quảng Ngãi
    'DANO': [5],        # Đắk Nông
}

# Validation: Check all provinces are defined
ALL_PROVINCES = [
    'MB',
    # Miền Nam
    'TPHCM', 'DOTH', 'CAMA', 'BETR', 'VUTA', 'BALI', 
    'DONA', 'CATH', 'SOTR', 'ANGI', 'TANI', 'BITH',
    'VILO', 'BIDU', 'TRVI', 'LOAN', 'BIPH', 'HAGI',
    'TIGI', 'KIGI', 'DALAT',
    # Miền Trung
    'THTH', 'PHYE', 'DALAK', 'QUNA', 'KHHO', 'DANA',
    'BIDI', 'QUTR', 'QUBI', 'GILA', 'NITH', 'QUNG',
    'DANO', 'KOTU'
]

# Verify all provinces have schedules
missing = set(ALL_PROVINCES) - set(PROVINCE_DRAW_SCHEDULE.keys())
if missing:
    print(f"⚠️  WARNING: Missing schedules for: {missing}")
