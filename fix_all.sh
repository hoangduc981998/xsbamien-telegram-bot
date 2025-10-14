#!/bin/bash
cd ~/xsbamien-telegram-bot
git checkout main && git pull
git checkout -b fix/code-quality-$(date +%s)
mkdir -p .github
echo "# Fix Instructions
Fix these:
1. app/handlers/callbacks.py line 7-9: Add import
2. app/handlers/callbacks.py lines 264,266,273: Break long lines
3. app/ui/formatters.py: Add type hints
4. Run: isort app/ --profile black
5. Run: black app/ --line-length 120" > .github/FIX.md
git add .github/FIX.md
git commit -m "docs: Fix instructions"
git push -u origin HEAD
echo ""
echo "✅ Branch pushed! Now create PR manually at:"
echo "https://github.com/hoangduc981998/xsbamien-telegram-bot/compare/main...$(git branch --show-current)"
