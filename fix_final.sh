#!/bin/bash
set -e

echo "🔧 FINAL FIX - V2"

# 1. Restore broken files
echo "📥 Restoring files from git..."
git checkout app/ui/messages.py
git checkout app/handlers/commands.py

# 2. Fix imports properly
echo "📦 Fixing imports..."

# Add missing import in callbacks.py
cat > /tmp/fix_import.py << 'PY'
with open('app/handlers/callbacks.py', 'r') as f:
    lines = f.readlines()

# Find and fix import section
for i, line in enumerate(lines):
    if 'from app.services.mock_data import (' in line:
        # Replace empty import with proper one
        j = i
        while j < len(lines) and ')' not in lines[j]:
            j += 1
        # Replace lines i to j with correct import
        lines[i:j+1] = [
            'from app.services.mock_data import get_mock_lottery_result\n'
        ]
        break

with open('app/handlers/callbacks.py', 'w') as f:
    f.writelines(lines)

print("✅ Import fixed")
PY

python3 /tmp/fix_import.py

# 3. Fix long lines in callbacks.py
echo "📏 Fixing long lines..."

# Line 264
sed -i '264s/\(await query.edit_message_text(\)\(.*\), \(reply_markup=.*\), \(parse_mode=.*\))/\1\n        \2,\n        \3,\n        \4\n    )/' app/handlers/callbacks.py

# 4. Format & sort
echo "🎨 Formatting..."
isort app/ --profile black --force-single-line-imports
black app/ --line-length 120

# 5. Fix type annotations
python3 << 'PY'
with open('app/ui/formatters.py', 'r') as f:
    content = f.read()

# Add typing imports if missing
if 'from typing import' not in content:
    content = 'from typing import Dict, List\n\n' + content

# Fix annotations
content = content.replace(
    'dau_lo_dict = {}',
    'dau_lo_dict: Dict[str, List[str]] = {}'
)
content = content.replace(
    'duoi_lo_dict = {}', 
    'duoi_lo_dict: Dict[str, List[str]] = {}'
)

with open('app/ui/formatters.py', 'w') as f:
    f.write(content)

print("✅ Type annotations fixed")
PY

# 6. Remove unused imports
echo "🗑️ Removing unused imports..."
sed -i '/^from app.services.mock_data import get_mock_stats/d' app/handlers/callbacks.py
sed -i '/^from app.ui.messages import get_schedule_message/d' app/handlers/callbacks.py

# 7. Fix f-string
sed -i 's/f"\([^{]*\)"/"\1"/g' app/handlers/callbacks.py

# 8. Fix bare except
sed -i 's/except:/except Exception:/g' app/handlers/callbacks.py

echo ""
echo "✅ ALL FIXES COMPLETE!"
