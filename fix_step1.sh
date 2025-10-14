#!/bin/bash
set -e

echo "🔧 BƯỚC 1: FIX ALL CODE ISSUES"

# ========== VẤN ĐỀ 1: Import ==========
echo "📦 Fix 1: Add missing import in callbacks.py..."
sed -i '/from app.services.mock_data import (/,/)/ c\
from app.services.mock_data import (\
    get_mock_lottery_result,\
)' app/handlers/callbacks.py

# ========== VẤN ĐỀ 2: Long Lines ==========
echo "📏 Fix 2: Break long lines..."

# Line 266
sed -i '266s/  #.*$//' app/handlers/callbacks.py  # Remove comment first

# Line 268
sed -i '268s/  #.*$//' app/handlers/callbacks.py

# Line 275
sed -i '275s/  #.*$//' app/handlers/callbacks.py

# Line 88 in messages.py
sed -i '88s/  #.*$//' app/ui/messages.py

# ========== VẤN ĐỀ 3: Argument Order ==========
echo "🔄 Fix 3: Fix argument order in commands.py..."

# Check current state
echo "Before:"
sed -n '48p;69p;88p' app/handlers/commands.py

# Fix all 3 lines
# Pattern: format_lottery_result(A, B) → format_lottery_result(B, A)
sed -i '48s/format_lottery_result(\([^)]*\))/format_lottery_result(\2, \1)/' app/handlers/commands.py 2>/dev/null || \
sed -i '48s/format_lottery_result([^,]*, \(.*\))/format_lottery_result(\1, result_data)/' app/handlers/commands.py

sed -i '69s/format_lottery_result([^,]*, \(.*\))/format_lottery_result(\1, result_data)/' app/handlers/commands.py
sed -i '88s/format_lottery_result([^,]*, \(.*\))/format_lottery_result(\1, result_data)/' app/handlers/commands.py

echo "After:"
sed -n '48p;69p;88p' app/handlers/commands.py

# ========== AUTO-FIXES ==========
echo "🎨 Fix 4: Format & sort..."
isort app/ --profile black
black app/

# Remove unused imports
sed -i '/get_mock_stats_2digit/d' app/handlers/callbacks.py
sed -i '/get_mock_stats_3digit/d' app/handlers/callbacks.py
sed -i '/get_schedule_message/d' app/ui/messages.py

# Fix f-string
sed -i 's/f"Đang phát triển"/Đang phát triển/' app/handlers/callbacks.py

# Fix bare except
sed -i 's/except:/except Exception:/' app/handlers/callbacks.py

# Fix trailing whitespace
find app/ -name "*.py" -exec sed -i 's/[[:space:]]*$//' {} +

# Fix type annotations
python3 << 'PY'
import re

# Fix formatters.py
with open('app/ui/formatters.py', 'r') as f:
    content = f.read()

content = re.sub(
    r'dau_lo_dict = \{\}',
    r'dau_lo_dict: Dict[str, List[str]] = {}',
    content
)
content = re.sub(
    r'duoi_lo_dict = \{\}',
    r'duoi_lo_dict: Dict[str, List[str]] = {}',
    content
)

with open('app/ui/formatters.py', 'w') as f:
    f.write(content)

print("✅ Type annotations fixed")
PY

echo ""
echo "✅ BƯỚC 1 HOÀN TẤT!"
echo ""
echo "🔍 Kiểm tra lại..."
