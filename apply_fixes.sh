#!/bin/bash
set -e

echo "🔧 Applying code quality fixes to PR #5..."

# Fix 1: Import
sed -i '/from app.services.mock_data import (/,/)/c\
from app.services.mock_data import get_mock_lottery_result' app/handlers/callbacks.py

# Fix 2: Type hints
if ! grep -q "from typing import Dict, List" app/ui/formatters.py; then
    sed -i '1i from typing import Dict, List\n' app/ui/formatters.py
fi
sed -i 's/dau_lo_dict = {}/dau_lo_dict: Dict[str, List[str]] = {}/g' app/ui/formatters.py
sed -i 's/duoi_lo_dict = {}/duoi_lo_dict: Dict[str, List[str]] = {}/g' app/ui/formatters.py

# Fix 3: Format
pip install -q black isort
isort app/ --profile black
black app/ --line-length 120

# Commit
git add -A
git commit -m "fix: Apply automated code quality fixes

✅ Fixed empty import in callbacks.py
✅ Added type hints in formatters.py  
✅ Formatted all files with black (120 line length)
✅ Sorted imports with isort (black profile)

All code quality checks should now pass."

git push origin fix/code-quality-1760433922

echo ""
echo "✅ Fixes pushed to PR #5!"
echo "🔗 https://github.com/hoangduc981998/xsbamien-telegram-bot/pull/5"
