#!/usr/bin/env python3
"""Insert 4 new callback handlers into callbacks.py"""

# Read the backup file
with open('app/handlers/callbacks.py.backup', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the position to insert (before the last else or at end of elif chain)
# Look for the line with "else:" or the last "elif" before closing the function

# New handlers code
new_handlers = '''
    # ========== NEW: 4 Statistics Buttons Handlers ==========
    
    elif callback_data.startswith("stats_lo2_"):
        """Handle Lô 2 số button"""
        province_code = callback_data.replace("stats_lo2_", "")
        await query.answer()
        
        try:
            result = await lottery_service.get_latest_result(province_code)
            if not result:
                await query.edit_message_text(
                    text=f"❌ Không tìm thấy kết quả cho {province_code}",
                    reply_markup=get_back_to_results_keyboard(),
                    parse_mode=ParseMode.HTML
                )
                return
            
            region = result.get('region', 'MN')
            
            if region == 'MB':
                from app.ui.formatters import format_lo_2_so_mb
                text = format_lo_2_so_mb(result)
            else:
                from app.ui.formatters import format_lo_2_so_mn_mt
                text = format_lo_2_so_mn_mt(result)
            
            keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data=f"result_{province_code}")]]
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in stats_lo2: {e}")
            await query.edit_message_text(
                text="❌ Có lỗi xảy ra",
                reply_markup=get_back_to_results_keyboard(),
                parse_mode=ParseMode.HTML
            )
    
    elif callback_data.startswith("stats_lo3_"):
        """Handle Lô 3 số button"""
        province_code = callback_data.replace("stats_lo3_", "")
        await query.answer()
        
        try:
            result = await lottery_service.get_latest_result(province_code)
            if not result:
                await query.edit_message_text(
                    text=f"❌ Không tìm thấy kết quả cho {province_code}",
                    reply_markup=get_back_to_results_keyboard(),
                    parse_mode=ParseMode.HTML
                )
                return
            
            region = result.get('region', 'MN')
            
            if region == 'MB':
                from app.ui.formatters import format_lo_3_so_mb
                text = format_lo_3_so_mb(result)
            else:
                from app.ui.formatters import format_lo_3_so_mn_mt
                text = format_lo_3_so_mn_mt(result)
            
            keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data=f"result_{province_code}")]]
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in stats_lo3: {e}")
            await query.edit_message_text(
                text="❌ Có lỗi xảy ra",
                reply_markup=get_back_to_results_keyboard(),
                parse_mode=ParseMode.HTML
            )
    
    elif callback_data.startswith("stats_dau_"):
        """Handle Đầu Lô button"""
        province_code = callback_data.replace("stats_dau_", "")
        await query.answer()
        
        try:
            result = await lottery_service.get_latest_result(province_code)
            if not result:
                await query.edit_message_text(
                    text=f"❌ Không tìm thấy kết quả cho {province_code}",
                    reply_markup=get_back_to_results_keyboard(),
                    parse_mode=ParseMode.HTML
                )
                return
            
            from app.ui.formatters import format_dau_lo
            text = format_dau_lo(result)
            
            keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data=f"result_{province_code}")]]
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in stats_dau: {e}")
            await query.edit_message_text(
                text="❌ Có lỗi xảy ra",
                reply_markup=get_back_to_results_keyboard(),
                parse_mode=ParseMode.HTML
            )
    
    elif callback_data.startswith("stats_duoi_"):
        """Handle Đuôi Lô button"""
        province_code = callback_data.replace("stats_duoi_", "")
        await query.answer()
        
        try:
            result = await lottery_service.get_latest_result(province_code)
            if not result:
                await query.edit_message_text(
                    text=f"❌ Không tìm thấy kết quả cho {province_code}",
                    reply_markup=get_back_to_results_keyboard(),
                    parse_mode=ParseMode.HTML
                )
                return
            
            from app.ui.formatters import format_duoi_lo
            text = format_duoi_lo(result)
            
            keyboard = [[InlineKeyboardButton("🔙 Quay lại", callback_data=f"result_{province_code}")]]
            
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error in stats_duoi: {e}")
            await query.edit_message_text(
                text="❌ Có lỗi xảy ra",
                reply_markup=get_back_to_results_keyboard(),
                parse_mode=ParseMode.HTML
            )
'''

# Find insertion point - before the "else:" clause or before closing the function
# Look for pattern like "    else:\n        logger"
import re

# Find the else clause
else_pattern = r'(\n    else:\n        logger\.warning)'
match = re.search(else_pattern, content)

if match:
    # Insert before the else
    insert_pos = match.start()
    new_content = content[:insert_pos] + new_handlers + content[insert_pos:]
    print("✅ Found 'else:' clause, inserting handlers before it")
else:
    print("❌ Could not find 'else:' clause")
    print("Please insert handlers manually")
    exit(1)

# Write to file
with open('app/handlers/callbacks.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Successfully inserted 4 callback handlers!")
print("")
print("Handlers added:")
print("  - stats_lo2_*  → Lô 2 số")
print("  - stats_lo3_*  → Lô 3 số")
print("  - stats_dau_*  → Đầu Lô")
print("  - stats_duoi_* → Đuôi Lô")
