"""Mock data - Dữ liệu giả để demo UI/UX"""

import random
from datetime import datetime
from typing import Dict


def get_mock_lottery_result(province_key: str) -> Dict:
    """
    Trả về kết quả xổ số giả (mock) cho demo
    """
    from app.data.mock_results import MOCK_RESULTS

    # Return from MOCK_RESULTS if exists (already in correct format)
    if province_key in MOCK_RESULTS:
        result = MOCK_RESULTS[province_key]
        # Ensure flat structure (unwrap 'prizes' if nested)
        if "prizes" in result and isinstance(result["prizes"], dict):
            # Flatten: move prizes content to top level
            flat_result = {
                "date": result.get("date"),
                "province": result.get(
                    "province_name", result.get("province", province_key)
                ),
            }
            flat_result.update(result["prizes"])
            return flat_result
        return result

    # Fallback: Generate random
    import random

    random.seed(hash(province_key + datetime.now().strftime("%Y%m%d")))

    # Default to MN region
    result = {
        "date": datetime.now().strftime("%d/%m/%Y"),
        "province": province_key,
        "G8": [f"{random.randint(0, 99):02d}"],
        "G7": [f"{random.randint(0, 999):03d}"],
        "G6": [f"{random.randint(0, 9999):04d}" for _ in range(3)],
        "G5": [f"{random.randint(0, 9999):04d}"],
        "G4": [f"{random.randint(0, 99999):05d}" for _ in range(7)],
        "G3": [f"{random.randint(0, 99999):05d}" for _ in range(2)],
        "G2": [f"{random.randint(0, 99999):05d}"],
        "G1": [f"{random.randint(0, 99999):05d}"],
        "DB": [f"{random.randint(0, 999999):06d}"],
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
