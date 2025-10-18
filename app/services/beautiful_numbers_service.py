"""Beautiful Numbers Service - Tìm số đẹp trong kết quả xổ số"""

import logging
from typing import List, Dict, Set
from collections import Counter

logger = logging.getLogger(__name__)


class BeautifulNumbersService:
    """Service phân tích và tìm số đẹp"""
    
    def __init__(self):
        pass
    
    def is_symmetric(self, number: str) -> bool:
        """Kiểm tra số đối xứng (đọc xuôi = đọc ngược)"""
        return number == number[::-1]
    
    def is_ascending(self, number: str) -> bool:
        """Kiểm tra số tăng dần liên tiếp"""
        if len(number) < 2:
            return False
        for i in range(len(number) - 1):
            if int(number[i+1]) != int(number[i]) + 1:
                return False
        return True
    
    def is_descending(self, number: str) -> bool:
        """Kiểm tra số giảm dần liên tiếp"""
        if len(number) < 2:
            return False
        for i in range(len(number) - 1):
            if int(number[i+1]) != int(number[i]) - 1:
                return False
        return True
    
    def is_same_digits(self, number: str) -> bool:
        """Kiểm tra toàn bộ chữ số giống nhau"""
        return len(set(number)) == 1
    
    def is_double_pair(self, number: str) -> bool:
        """Kiểm tra số có 2 cặp đôi (AABB, ABAB)"""
        if len(number) != 4:
            return False
        # AABB
        if number[0] == number[1] and number[2] == number[3] and number[0] != number[2]:
            return True
        # ABAB
        if number[0] == number[2] and number[1] == number[3] and number[0] != number[1]:
            return True
        return False
    
    def is_taxi_number(self, number: str) -> bool:
        """Kiểm tra số taxi (3 chữ số cuối giống nhau)"""
        if len(number) < 3:
            return False
        return number[-3:] == number[-1] * 3
    
    def has_lucky_pattern(self, number: str) -> bool:
        """Kiểm tra số có chứa các con số may mắn (68, 86, 88, 99)"""
        lucky_patterns = ['68', '86', '88', '99', '666', '888', '999']
        return any(pattern in number for pattern in lucky_patterns)
    
    def count_digit_frequency(self, number: str) -> Dict[str, int]:
        """Đếm tần suất xuất hiện của mỗi chữ số"""
        return dict(Counter(number))
    
    def analyze_number(self, number: str) -> Dict:
        """
        Phân tích một số và trả về các thuộc tính
        
        Args:
            number: Số cần phân tích (string)
            
        Returns:
            Dict với các thuộc tính của số
        """
        properties = []
        
        if self.is_symmetric(number):
            properties.append("Đối xứng")
        
        if self.is_same_digits(number):
            properties.append("Toàn bộ giống nhau")
        elif self.is_ascending(number):
            properties.append("Tăng dần")
        elif self.is_descending(number):
            properties.append("Giảm dần")
        
        if len(number) == 4 and self.is_double_pair(number):
            properties.append("Số đôi")
        
        if self.is_taxi_number(number):
            properties.append("Số taxi")
        
        if self.has_lucky_pattern(number):
            properties.append("Có số may mắn")
        
        return {
            'number': number,
            'properties': properties,
            'is_beautiful': len(properties) > 0
        }
    
    def find_beautiful_numbers(self, result_data: Dict) -> Dict:
        """
        Tìm tất cả số đẹp trong kết quả xổ số
        
        Args:
            result_data: Dữ liệu kết quả xổ số
            
        Returns:
            Dict với các số đẹp được phân loại
        """
        prizes = result_data.get('prizes', {})
        
        beautiful_numbers = {
            'symmetric': [],      # Đối xứng
            'same_digits': [],    # Toàn bộ giống nhau
            'ascending': [],      # Tăng dần
            'descending': [],     # Giảm dần
            'double_pair': [],    # Số đôi
            'taxi': [],           # Số taxi
            'lucky': [],          # Có số may mắn
        }
        
        all_numbers = []
        
        # Thu thập tất cả các số
        for prize_name, numbers in prizes.items():
            if isinstance(numbers, list):
                all_numbers.extend(numbers)
            else:
                all_numbers.append(numbers)
        
        # Phân tích từng số
        for number in all_numbers:
            number_str = str(number).strip()
            
            # ✅ Chỉ xử lý nếu là số thuần túy
            if not number_str.isdigit():
                continue
            
            if self.is_symmetric(number_str):
                beautiful_numbers['symmetric'].append(number_str)
            
            if self.is_same_digits(number_str):
                beautiful_numbers['same_digits'].append(number_str)
            elif self.is_ascending(number_str):
                beautiful_numbers['ascending'].append(number_str)
            elif self.is_descending(number_str):
                beautiful_numbers['descending'].append(number_str)
            
            if len(number_str) == 4 and self.is_double_pair(number_str):
                beautiful_numbers['double_pair'].append(number_str)
            
            if self.is_taxi_number(number_str):
                beautiful_numbers['taxi'].append(number_str)
            
            if self.has_lucky_pattern(number_str):
                beautiful_numbers['lucky'].append(number_str)
        
        # Loại bỏ trùng lặp
        for key in beautiful_numbers:
            beautiful_numbers[key] = sorted(list(set(beautiful_numbers[key])))
        
        return beautiful_numbers
    
    def format_beautiful_numbers(self, beautiful_numbers: Dict, province_name: str) -> str:
        """
        Format kết quả số đẹp thành message
        
        Args:
            beautiful_numbers: Dict các số đẹp
            province_name: Tên tỉnh
            
        Returns:
            String message đã format
        """
        message = f"✨ <b>SỐ ĐẸP - {province_name.upper()}</b>\n\n"
        
        categories = [
            ('symmetric', '🔄 Số đối xứng', 'VD: 121, 1331, 12321'),
            ('same_digits', '🎯 Toàn bộ giống nhau', 'VD: 111, 2222, 55555'),
            ('ascending', '📈 Tăng dần', 'VD: 123, 1234, 456'),
            ('descending', '📉 Giảm dần', 'VD: 321, 4321, 654'),
            ('double_pair', '🎲 Số đôi', 'VD: 1122, 1212, 2233'),
            ('taxi', '�� Số taxi', 'VD: 1888, 2999, 5666'),
            ('lucky', '🍀 Số may mắn', 'VD: 68, 86, 88, 99'),
        ]
        
        found_any = False
        
        for key, title, example in categories:
            numbers = beautiful_numbers.get(key, [])
            if numbers:
                found_any = True
                message += f"{title}:\n"
                message += f"  <code>{', '.join(numbers)}</code>\n"
                message += f"  <i>{example}</i>\n\n"
        
        if not found_any:
            message += "ℹ️ <i>Không tìm thấy số đẹp đặc biệt</i>\n\n"
            message += "💡 <b>Số đẹp bao gồm:</b>\n"
            message += "  • Đối xứng (121, 1221)\n"
            message += "  • Tăng/giảm dần (123, 321)\n"
            message += "  • Toàn bộ giống nhau (111, 888)\n"
            message += "  • Số đôi (1122, 1212)\n"
            message += "  • Số may mắn (68, 86, 88, 99)\n"
        
        return message
