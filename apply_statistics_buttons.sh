#!/bin/bash

set -e

echo "🚀 Applying 4 Statistics Buttons Feature..."
echo ""

# 1. Add keyboard function
echo "📝 Step 1: Adding keyboard function..."
cat >> app/ui/keyboards.py << 'EOKB'


def get_statistics_buttons_keyboard(province_code: str) -> InlineKeyboardMarkup:
    """
    Get statistics buttons keyboard with 4 main analysis options
    
    Layout:
    ┌──────────────┬──────────────┐
    │ 📊 Lô 2 số   │ 🎰 Lô 3 số   │
    ├──────────────┼──────────────┤
    │ 🔢 Đầu Lô    │ 🔢 Đuôi Lô   │
    └──────────────┴──────────────┘
    """
    keyboard = [
        [
            InlineKeyboardButton("📊 Lô 2 số", callback_data=f"stats_lo2_{province_code}"),
            InlineKeyboardButton("🎰 Lô 3 số", callback_data=f"stats_lo3_{province_code}"),
        ],
        [
            InlineKeyboardButton("🔢 Đầu Lô", callback_data=f"stats_dau_{province_code}"),
            InlineKeyboardButton("🔢 Đuôi Lô", callback_data=f"stats_duoi_{province_code}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
EOKB

echo "✅ Keyboard function added"
echo ""

# 2. Show next steps
echo "📋 Next Steps:"
echo "  1. Manually add 4 callback handlers to app/handlers/callbacks.py"
echo "  2. Update result_ callback to use get_statistics_buttons_keyboard()"
echo "  3. Run tests"
echo "  4. Test on Telegram"
echo ""

echo "✅ Step 1 complete!"
echo ""
echo "📝 I'll provide the callback handlers code next..."
