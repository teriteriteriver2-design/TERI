import os

backup_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/auto_backup.py'
with open(backup_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Allow .github folder but still ignore other hidden folders like .git, .vscode, etc.
old_logic = "dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.startswith('.')]"
new_logic = "dirs[:] = [d for d in dirs if d not in ignored_dirs and (not d.startswith('.') or d == '.github')]"

content = content.replace(old_logic, new_logic)

with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed auto_backup.py to include .github folder!")
