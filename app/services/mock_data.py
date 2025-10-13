"""Mock data - Dữ liệu giả để demo UI/UX"""
import random
from datetime import datetime
from typing import Dict


def get_mock_lottery_result(province_key: str) -> Dict:
    """
    Trả về kết quả xổ số giả (mock) cho demo
    
    Args:
        province_key: Mã tỉnh/thành (VD: "TPHCM", "MB", "DANA")
    
    Returns:
        Dict chứa kết quả các giải từ G8→ĐB
    """
    # Seed để có kết quả nhất quán cho mỗi tỉnh
    random.seed(hash(province_key + datetime.now().strftime("%Y%m%d")))
    
    result = {
        "date": datetime.now().strftime("%d/%m/%Y"),
        "province": province_key,
        
        # Giải đặc biệt (6 số)
        "DB": str(random.randint(100000, 999999)),
        
        # Giải nhất (5 số)
        "G1": str(random.randint(10000, 99999)),
        
        # Giải nhì (2 số 5 chữ số)
        "G2": [
            str(random.randint(10000, 99999)),
            str(random.randint(10000, 99999)),
        ],
        
        # Giải ba (6 số 5 chữ số)
        "G3": [
            str(random.randint(10000, 99999)),
            str(random.randint(10000, 99999)),
            str(random.randint(10000, 99999)),
            str(random.randint(10000, 99999)),
            str(random.randint(10000, 99999)),
            str(random.randint(10000, 99999)),
        ],
        
        # Giải tư (4 số 4 chữ số)
        "G4": [
            str(random.randint(1000, 9999)),
            str(random.randint(1000, 9999)),
            str(random.randint(1000, 9999)),
            str(random.randint(1000, 9999)),
        ],
        
        # Giải năm (6 số 4 chữ số)
        "G5": [
            str(random.randint(1000, 9999)),
            str(random.randint(1000, 9999)),
            str(random.randint(1000, 9999)),
            str(random.randint(1000, 9999)),
            str(random.randint(1000, 9999)),
            str(random.randint(1000, 9999)),
        ],
        
        # Giải sáu (3 số 3 chữ số)
        "G6": [
            str(random.randint(100, 999)),
            str(random.randint(100, 999)),
            str(random.randint(100, 999)),
        ],
        
        # Giải bảy (4 số 2 chữ số)
        "G7": [
            str(random.randint(10, 99)),
            str(random.randint(10, 99)),
            str(random.randint(10, 99)),
            str(random.randint(10, 99)),
        ],
    }
    
    return result


def get_mock_stats_2digit(region: str) -> Dict:
    """
    Trả về thống kê lô 2 số giả (mock)
    
    Args:
        region: Miền (MB, MT, MN)
    
    Returns:
        Dict chứa thống kê top frequent và rare numbers
    """
    random.seed(hash(region + "2digit"))
    
    # Tạo danh sách 100 số từ 00-99
    all_numbers = list(range(100))
    random.shuffle(all_numbers)
    
    # Top 15 số hay về (số xuất hiện nhiều)
    top_frequent = []
    for i in range(15):
        num = all_numbers[i]
        count = random.randint(30, 50)  # Số lần xuất hiện
        top_frequent.append((num, count))
    
    # Sắp xếp theo số lần giảm dần
    top_frequent.sort(key=lambda x: x[1], reverse=True)
    
    # Top 10 số ít về
    rare_numbers = []
    for i in range(85, 95):  # Lấy 10 số cuối
        num = all_numbers[i]
        count = random.randint(10, 20)
        rare_numbers.append((num, count))
    
    # Sắp xếp theo số lần tăng dần
    rare_numbers.sort(key=lambda x: x[1])
    
    return {
        "region": region,
        "top_frequent": top_frequent,
        "rare": rare_numbers[:5],  # Top 5 ít về nhất
    }


def get_mock_stats_3digit(province_key: str) -> Dict:
    """
    Trả về thống kê lô 3 số giả (mock)
    
    Args:
        province_key: Mã tỉnh/thành
    
    Returns:
        Dict chứa thống kê giải đặc biệt và bộ 3 số
    """
    random.seed(hash(province_key + "3digit"))
    
    # Giải đặc biệt hay về
    db_frequent = []
    for _ in range(10):
        num = random.randint(0, 999)
        count = random.randint(2, 8)
        db_frequent.append((num, count))
    
    db_frequent.sort(key=lambda x: x[1], reverse=True)
    
    # Bộ 3 số hay ra cùng nhau
    triples = []
    for _ in range(5):
        n1 = str(random.randint(10, 99))
        n2 = str(random.randint(10, 99))
        n3 = str(random.randint(10, 99))
        count = random.randint(5, 12)
        triples.append((n1, n2, n3, count))
    
    triples.sort(key=lambda x: x[3], reverse=True)
    
    return {
        "province": province_key,
        "db_frequent": db_frequent[:5],
        "triples": triples[:3],
    }
