#!/bin/bash

echo "🧹 Cleaning up temporary files..."

# Remove backups
rm -f app/services/statistics_service.py.backup

# Remove temporary scripts (keep them or delete?)
rm -f fix_dict_keys.patch
rm -f fix_mock_data.py

# Optional: Keep scripts for future reference
mkdir -p scripts/maintenance
mv crawl_200_correct.sh scripts/maintenance/ 2>/dev/null
mv crawl_all_200.sh scripts/maintenance/ 2>/dev/null
mv finalize_all.sh scripts/maintenance/ 2>/dev/null
mv fix_tests.sh scripts/maintenance/ 2>/dev/null
mv hotfix_dict_keys.sh scripts/maintenance/ 2>/dev/null
mv create_lo_gan_backups.sh scripts/maintenance/ 2>/dev/null

echo "✅ Cleanup complete!"
echo ""
echo "Scripts moved to: scripts/maintenance/"
ls -la scripts/maintenance/
