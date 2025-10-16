"""Draw schedules for lottery provinces.

This module defines which days of the week each province draws their lottery.
The weekday mapping follows Python's datetime.weekday() convention:
0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
"""

# Draw schedules: weekday mapping (0=Monday, 6=Sunday)
PROVINCE_DRAW_SCHEDULE = {
    # Miền Bắc - daily
    'MB': [0, 1, 2, 3, 4, 5, 6],  # Every day

    # Miền Nam (quay 1-2 lần/tuần)
    'ANGI': [3],        # Thursday only
    'BALI': [2, 5],     # Wednesday, Saturday
    'BETR': [1],        # Tuesday (Bến Tre)
    'CAMA': [3],        # Thursday
    'CATH': [2],        # Wednesday (Cần Thơ)
    'DALAT': [6],       # Sunday
    'DONA': [2],        # Wednesday (Đồng Nai)
    'HAGI': [5],        # Saturday (Hậu Giang)
    'KIGI': [6],        # Sunday (Kiên Giang)
    'LOAN': [5],        # Saturday (Long An)
    'SOTR': [0],        # Monday (Sóc Trăng)
    'TANI': [3],        # Thursday (Tây Ninh)
    'TIGI': [6],        # Sunday (Tiền Giang)
    'TRVI': [4],        # Friday (Trà Vinh)
    'VILO': [4],        # Friday (Vĩnh Long)
    'VUTA': [1],        # Tuesday (Vũng Tàu)
    'TPHCM': [0, 5],    # Monday, Saturday
    'BIDU': [4],        # Friday (Bình Dương)
    'BIPH': [5],        # Saturday (Bình Phước)
    'BITH': [3],        # Thursday (Bình Thuận)
    'DOTH': [0],        # Monday (Đồng Tháp)

    # Miền Trung
    'BIDI': [3],        # Thursday (Bình Định)
    'DALAK': [1],       # Tuesday (Đắk Lắk)
    'DANA': [2],        # Wednesday (Đà Nẵng)
    'DANO': [5],        # Saturday (Đắk Nông)
    'GILA': [4],        # Friday (Gia Lai)
    'KHHO': [6],        # Sunday (Khánh Hòa)
    'KOTU': [6],        # Sunday (Kon Tum)
    'PHYE': [0],        # Monday (Phú Yên)
    'QUBI': [3],        # Thursday (Quảng Bình)
    'QUNA': [1],        # Tuesday (Quảng Nam)
    'QUNG': [5],        # Saturday (Quảng Ngãi)
    'QUTR': [3],        # Thursday (Quảng Trị)
    'NITH': [4],        # Friday (Ninh Thuận)
    'THTH': [0],        # Monday (Huế)
}
