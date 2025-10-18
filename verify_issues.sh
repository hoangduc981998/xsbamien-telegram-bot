#!/bin/bash

echo "🔍 VERIFYING ALL ISSUES..."
echo ""

# 1. Syntax errors
echo "1️⃣ Checking syntax errors..."
find app -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | grep -i "error" || echo "   ✅ No syntax errors"

# 2. Token in git
echo ""
echo "2️⃣ Checking token security..."
git log --all --oneline | grep -i token && echo "   ⚠️ Token mentioned in commits!" || echo "   ✅ No token in git history"

# 3. Import in functions
echo ""
echo "3️⃣ Checking imports in functions..."
grep -A 30 "async def " app/handlers/*.py | grep -c "    from \|    import " && echo "   ⚠️ Found imports inside functions"

# 4. Callback file size
echo ""
echo "4️⃣ Checking callback handler size..."
wc -l app/handlers/callbacks.py

# 5. Error handling
echo ""
echo "5️⃣ Checking error handling..."
grep -c "logger.exception" app/handlers/*.py && echo "   ✅ Using logger.exception" || echo "   ⚠️ Not using logger.exception"

# 6. Cache usage
echo ""
echo "6️⃣ Checking cache..."
grep -r "redis" app/ && echo "   ✅ Redis found" || echo "   ⚠️ No Redis cache"

# 7. Input validation
echo ""
echo "7️⃣ Checking input sanitization..."
grep -r "html.escape\|sanitize" app/handlers/ && echo "   ✅ Found sanitization" || echo "   ⚠️ No input sanitization"

echo ""
echo "✅ Verification complete!"
