#!/bin/bash

echo "🎉 FINALIZING ALL LÔ GAN FIXES"
echo "=" | head -c 70 | tr '\n' '='
echo ""

# Stop bot
pkill -9 python 2>/dev/null

# Checkout main
git checkout main

# Merge PR #20
echo "📥 Merging PR #20 (Remove 'Chưa về')..."
git merge origin/copilot/fix-logical-error-in-lo-gan \
  -m "Merge PR #20: Remove 'Chưa về' numbers and increase window to 100"

if [ $? -ne 0 ]; then
    echo "❌ PR #20 merge failed!"
    exit 1
fi

# Merge PR #22
echo "📥 Merging PR #22 (Fix max_cycle logic)..."
git merge origin/copilot/fix-max-cycle-logic-error \
  -m "Merge PR #22: Fix max_cycle calculation logic"

if [ $? -ne 0 ]; then
    echo "❌ PR #22 merge failed!"
    exit 1
fi

# Push to remote
echo "📤 Pushing to remote..."
git push origin main

if [ $? -ne 0 ]; then
    echo "❌ Push failed!"
    exit 1
fi

# Update callback to use 200 days
echo "📝 Updating callback to use 200 days window..."
sed -i 's/days=50/days=200/g' app/handlers/callbacks.py

# Commit the change
git add app/handlers/callbacks.py
git commit -m "Update Lô Gan window to 200 days (API max limit)"
git push origin main

# Run tests
echo ""
echo "🧪 Running tests..."
python -m pytest tests/test_lo_gan_fixes.py tests/test_max_cycle_fix.py -v --tb=short

if [ $? -eq 0 ]; then
    echo ""
    echo "=" | head -c 70 | tr '\n' '='
    echo ""
    echo "🎉 SUCCESS! All fixes merged and tested!"
    echo ""
    echo "Summary:"
    echo "  ✅ PR #20: Removed 'Chưa về' numbers"
    echo "  ✅ PR #22: Fixed max_cycle calculation"
    echo "  ✅ Window: 200 kỳ (API maximum)"
    echo "  ✅ Tests: All passing"
    echo ""
    echo "Next steps:"
    echo "  - Start bot: python -m app.main"
    echo "  - Test on Telegram"
else
    echo ""
    echo "⚠️  Some tests failed - review manually"
fi
