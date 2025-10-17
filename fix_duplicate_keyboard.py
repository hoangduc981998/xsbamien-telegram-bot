#!/usr/bin/env python3

with open('app/ui/keyboards.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Count occurrences
count = content.count('def get_statistics_buttons_keyboard')
print(f"Found {count} definitions of get_statistics_buttons_keyboard")

if count > 1:
    # Find all positions
    import re
    pattern = r'def get_statistics_buttons_keyboard.*?(?=\ndef |\Z)'
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    print(f"Found {len(matches)} function definitions")
    
    # Keep only the first one, remove others
    # Remove from end to beginning to preserve positions
    new_content = content
    for match in reversed(matches[1:]):
        start = match.start()
        end = match.end()
        print(f"Removing duplicate at position {start}-{end}")
        new_content = new_content[:start] + new_content[end:]
    
    with open('app/ui/keyboards.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Removed duplicate keyboard function")
else:
    print("✅ No duplicates found")
