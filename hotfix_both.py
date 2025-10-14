import re

# Fix 1: mock_data.py - Fix PROVINCES iteration
with open('app/services/mock_data.py', 'r') as f:
    content = f.read()

# Replace wrong iteration
content = re.sub(
    r'for prov in PROVINCES:.*?if prov\[\'key\'\] == province_key:.*?region = prov\[\'region\'\].*?break',
    '''# PROVINCES is a list of dicts
    region = None
    for prov in PROVINCES:
        if isinstance(prov, dict) and prov.get('key') == province_key:
            region = prov.get('region')
            break''',
    content,
    flags=re.DOTALL
)

with open('app/services/mock_data.py', 'w') as f:
    f.write(content)

print("✅ Fix 1: Fixed PROVINCES iteration")

# Fix 2: Unwrap 'prizes' for MB
with open('app/services/mock_data.py', 'r') as f:
    lines = f.readlines()

# Find where MB result is returned and flatten it
for i, line in enumerate(lines):
    if '"prizes":' in line:
        print(f"Found 'prizes' at line {i+1}")
        # This is the nested structure - need to flatten

# Better approach: Use MOCK_RESULTS directly
with open('app/services/mock_data.py', 'r') as f:
    content = f.read()

# Completely rewrite to use MOCK_RESULTS properly
new_function = '''def get_mock_lottery_result(province_key: str) -> Dict:
    """
    Trả về kết quả xổ số giả (mock) cho demo
    """
    from app.data.mock_results import MOCK_RESULTS
    
    # Return from MOCK_RESULTS if exists (already in correct format)
    if province_key in MOCK_RESULTS:
        result = MOCK_RESULTS[province_key]
        # Ensure flat structure (unwrap 'prizes' if nested)
        if 'prizes' in result and isinstance(result['prizes'], dict):
            # Flatten: move prizes content to top level
            flat_result = {
                'date': result.get('date'),
                'province': result.get('province_name', result.get('province', province_key))
            }
            flat_result.update(result['prizes'])
            return flat_result
        return result
    
    # Fallback: Generate random
    from datetime import datetime
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
        "DB": [f"{random.randint(0, 999999):06d}"]
    }
    return result'''

# Replace the function
content = re.sub(
    r'def get_mock_lottery_result\(province_key: str\) -> Dict:.*?(?=\n\ndef |\nclass |\Z)',
    new_function + '\n\n',
    content,
    flags=re.DOTALL
)

with open('app/services/mock_data.py', 'w') as f:
    f.write(content)

print("✅ Fix 2: Flattened prizes structure")
