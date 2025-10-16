#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Creating Lô Gan Backup Files${NC}"
echo "======================================"

# Create backup directory
BACKUP_DIR="tests/lo_gan_backups"
mkdir -p "$BACKUP_DIR"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Files to backup
declare -a FILES=(
    "app/services/db/statistics_db_service.py:core_logic"
    "app/utils/lottery_helpers.py:helpers"
    "app/constants/draw_schedules.py:schedules"
    "app/ui/formatters.py:formatter"
    "app/handlers/callbacks.py:handler"
)

# Counter
count=1

# Copy each file
for file_info in "${FILES[@]}"; do
    IFS=':' read -r filepath name <<< "$file_info"
    
    if [ -f "$filepath" ]; then
        backup_name="${BACKUP_DIR}/${name}_backup_${count}_${TIMESTAMP}.py"
        cp "$filepath" "$backup_name"
        echo -e "${GREEN}✅ [$count/5] Created: ${backup_name}${NC}"
        echo "   Source: $filepath"
        echo "   Size: $(stat -f%z "$backup_name" 2>/dev/null || stat -c%s "$backup_name") bytes"
        echo ""
        ((count++))
    else
        echo "⚠️  File not found: $filepath"
    fi
done

echo "======================================"
echo -e "${BLUE}📂 Summary:${NC}"
echo "   Backup directory: $BACKUP_DIR"
echo "   Files created: $((count - 1))"
echo ""
echo "📋 List of backups:"
ls -lh "$BACKUP_DIR" | tail -n +2

echo ""
echo "🔍 To restore a file:"
echo "   cp tests/lo_gan_backups/core_logic_backup_1_${TIMESTAMP}.py app/services/db/statistics_db_service.py"
