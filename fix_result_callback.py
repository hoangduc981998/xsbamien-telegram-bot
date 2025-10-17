#!/usr/bin/env python3

with open('app/handlers/callbacks.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line 227 (around there)
changed = False
for i in range(200, 230):
    if i < len(lines) and 'get_province_detail_keyboard(province_key)' in lines[i]:
        # Check if this is in result_ callback (should be around line 204-230)
        if i >= 204 and i <= 230:
            print(f"Found at line {i+1}: {lines[i].strip()}")
            # Replace with statistics keyboard
            lines[i] = lines[i].replace(
                'get_province_detail_keyboard(province_key)',
                'get_statistics_buttons_keyboard(province_key)'
            )
            changed = True
            print(f"✅ Updated to: {lines[i].strip()}")
            break

if changed:
    with open('app/handlers/callbacks.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("\n✅ Successfully updated result_ callback!")
else:
    print("\n⚠️  Could not find the line to update")
    print("Line 227 should have: get_province_detail_keyboard(province_key)")
