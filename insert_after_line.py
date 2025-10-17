#!/usr/bin/env python3
"""Insert handlers after specific line number"""

# Read file
with open('app/handlers/callbacks.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line with 'results_MN' - should be around line 544
insert_after_line = -1
for i, line in enumerate(lines):
    if 'elif callback_data == "results_MN"' in line:
        # Find the end of this block (until next elif or else)
        for j in range(i + 1, len(lines)):
            if lines[j].strip().startswith('elif ') or lines[j].strip().startswith('else:'):
                insert_after_line = j
                break
            # If we find the closing of the function (less indentation)
            if lines[j].strip() and not lines[j].startswith(' ' * 8):
                insert_after_line = j
                break
        break

if insert_after_line == -1:
    print("❌ Could not find insertion point")
    print("Searching for 'results_MN'...")
    for i, line in enumerate(lines):
        if 'results_MN' in line:
            print(f"Found at line {i+1}: {line.strip()}")
    exit(1)

print(f"✅ Will insert after line {insert_after_line}")
print(f"\n📄 Context (lines {insert_after_line-2} to {insert_after_line+2}):")
for i in range(max(0, insert_after_line-2), min(len(lines), insert_after_line+2)):
    marker = ">>> INSERT AFTER" if i == insert_after_line - 1 else "   "
    print(f"{marker} {i+1:4d}: {lines[i].rstrip()}")

# New handlers
new_handlers = '''
        # ========== NEW: 4 Statistics Buttons ==========
        
        elif callback_data.startswith("stats_lo2_"):
            """📊 Lô 2 số button"""
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
            """🎰 Lô 3 số button"""
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
                
                keyboard = [[InlineKeyboardButton("�� Quay lại", callback_data=f"result_{province_code}")]]
                
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
            """🔢 Đầu Lô button"""
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
            """🔢 Đuôi Lô button"""
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

# Insert
new_lines = lines[:insert_after_line] + [new_handlers] + lines[insert_after_line:]

# Write
with open('app/handlers/callbacks.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("\n✅ Successfully inserted 4 callback handlers!")
print("\n📊 Summary:")
print("  Added handlers:")
print("    - stats_lo2_*  → 📊 Lô 2 số")
print("    - stats_lo3_*  → 🎰 Lô 3 số")
print("    - stats_dau_*  → 🔢 Đầu Lô")
print("    - stats_duoi_* → 🔢 Đuôi Lô")
