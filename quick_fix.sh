#!/bin/bash
set -e

echo "🔧 Starting auto-fix..."

# 1. Fix code formatting
echo "📝 Formatting code with black..."
black app/

# 2. Fix import sorting
echo "📦 Sorting imports with isort..."
isort app/ --profile black

# 3. Fix flake8 dependency issue
echo "🔧 Fixing flake8..."
pip install --upgrade importlib-metadata flake8==6.1.0

# 4. Fix config.py type hint
echo "🔍 Fixing config.py..."
sed -i 's/def get_province_by_code(code: str) -> Dict:/def get_province_by_code(code: str) -> Optional[Dict]:/' app/config.py
sed -i '2a from typing import Dict, List, Optional' app/config.py

# 5. Fix formatters.py type annotations
echo "🔍 Fixing formatters.py..."
sed -i '389s/dau_lo_dict = {}/dau_lo_dict: Dict[str, List[str]] = {}/' app/ui/formatters.py
sed -i '442s/duoi_lo_dict = {}/duoi_lo_dict: Dict[str, List[str]] = {}/' app/ui/formatters.py

# 6. Remove duplicate import in callbacks.py
echo "🔍 Fixing callbacks.py..."
sed -i '8d' app/handlers/callbacks.py

echo "✅ Auto-fix complete!"
echo "📊 Running checks..."

# Verify
black app/ --check
isort app/ --check-only
echo "🎉 All fixes applied successfully!"
