#!/usr/bin/env python3
"""Update result_ callback to show 4 statistics buttons"""

with open('app/handlers/callbacks.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the result_ callback (starts with "elif callback_data.startswith("result_"):")
# We need to find where it calls edit_message_text with result text

import re

# Pattern: Look for result_ callback and its edit_message_text
# We want to replace the reply_markup parameter

# Find all occurrences of result_ callback
pattern = r'(elif callback_data\.startswith\("result_"\):.*?)(await query\.edit_message_text\([^)]*?reply_markup=)([^,\)]+)'

matches = list(re.finditer(pattern, content, re.DOTALL))

if not matches:
    print("❌ Could not find result_ callback")
    print("\nSearching manually...")
    if 'elif callback_data.startswith("result_")' in content:
        print("✅ Found result_ callback")
        # Find the line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'elif callback_data.startswith("result_")' in line:
                print(f"Found at line {i+1}")
                # Show context
                for j in range(i, min(len(lines), i + 30)):
                    print(f"{j+1:4d}: {lines[j]}")
                break
    exit(1)

print(f"✅ Found {len(matches)} result_ callback(s)")

# Replace reply_markup with statistics keyboard
def replace_markup(match):
    prefix = match.group(1)
    edit_call = match.group(2)
    old_markup = match.group(3)
    
    # Check if this is in result_ callback
    if 'result_' not in match.group(0):
        return match.group(0)
    
    # Replace with statistics keyboard
    return f"{prefix}{edit_call}get_statistics_buttons_keyboard(province_key)"

new_content = re.sub(pattern, replace_markup, content, flags=re.DOTALL)

if new_content != content:
    with open('app/handlers/callbacks.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ Updated result_ callback!")
else:
    print("⚠️  No changes made - manual update needed")
