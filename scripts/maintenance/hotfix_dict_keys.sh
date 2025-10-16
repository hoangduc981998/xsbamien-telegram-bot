#!/bin/bash

echo "🔧 Applying hotfix for dict key type error..."

# Stop bot
pkill -9 python 2>/dev/null
echo "✅ Bot stopped"

# Backup file
cp app/services/statistics_service.py app/services/statistics_service.py.backup
echo "✅ Backup created"

# Apply fix
sed -i "103s/'by_head': {i:/'by_head': {str(i):/" app/services/statistics_service.py
sed -i "104s/'by_tail': {i:/'by_tail': {str(i):/" app/services/statistics_service.py

echo "✅ Fix applied"

# Verify
echo ""
echo "After fix (lines 103-104):"
sed -n '103,104p' app/services/statistics_service.py

# Check if fix worked
if grep -q "str(i)" app/services/statistics_service.py; then
    echo ""
    echo "✅ Fix verified!"
    
    # Commit
    git add app/services/statistics_service.py
    git commit -m "Hotfix: Use str() for dict keys in error fallback"
    git push origin main
    
    echo "✅ Changes committed"
else
    echo ""
    echo "❌ Fix failed! Restoring backup..."
    mv app/services/statistics_service.py.backup app/services/statistics_service.py
    exit 1
fi

# Restart bot
echo ""
echo "🚀 Restarting bot..."
python -m app.main &

sleep 2
echo ""
echo "✅ Bot restarted (PID: $!)"
echo ""
echo "Monitor logs:"
echo "  tail -f logs/app.log"
