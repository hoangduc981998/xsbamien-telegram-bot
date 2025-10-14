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
        Dict chứa kết quả các giải
        - Miền Bắc: 27 giải (ĐB, G1-G7)
        - Miền Nam/Trung: 18 giải (G8-ĐB, thứ tự ngược)
    """
    from app.data.mock_results import MOCK_RESULTS
    
    # Lấy từ mock data file
    if province_key in MOCK_RESULTS:
        return MOCK_RESULTS[province_key]
    
    # Fallback: Generate random nếu không có trong MOCK_RESULTS
    from datetime import datetime
    import random
    
    random.seed(hash(province_key + datetime.now().strftime("%Y%m%d")))
    
    # Xác định miền
    from app.config import PROVINCES
    region = None
    for prov in PROVINCES:
        if prov['key'] == province_key:
            region = prov['region']
            break
    
    if not region:
        region = "MN"  # Default
    
    # Generate theo region
    result = {
        "date": datetime.now().strftime("%d/%m/%Y"),
        "province": province_key
    }
    
    if region == "MB":
        # Miền Bắc: 27 giải
        result["DB"] = f"{random.randint(0, 99999):05d}"
        result["G1"] = f"{random.randint(0, 99999):05d}"
        result["G2"] = [f"{random.randint(0, 99999):05d}" for _ in range(2)]
        result["G3"] = [f"{random.randint(0, 9999):04d}" for _ in range(6)]
        result["G4"] = [f"{random.randint(0, 9999):04d}" for _ in range(4)]
        result["G5"] = [f"{random.randint(0, 9999):04d}" for _ in range(6)]
        result["G6"] = [f"{random.randint(0, 999):03d}" for _ in range(3)]
        result["G7"] = [f"{random.randint(0, 99):02d}" for _ in range(4)]
    else:
        # Miền Nam/Trung: 18 giải
        result["G8"] = [f"{random.randint(0, 99):02d}"]
        result["G7"] = [f"{random.randint(0, 999):03d}"]
        result["G6"] = [f"{random.randint(0, 9999):04d}" for _ in range(3)]
        result["G5"] = [f"{random.randint(0, 9999):04d}"]
        result["G4"] = [f"{random.randint(0, 99999):05d}" for _ in range(7)]
        result["G3"] = [f"{random.randint(0, 99999):05d}" for _ in range(2)]
        result["G2"] = [f"{random.randint(0, 99999):05d}"]
        result["G1"] = [f"{random.randint(0, 99999):05d}"]
        result["DB"] = [f"{random.randint(0, 999999):06d}"]
    
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
