import codecs

with codecs.open('app_restored.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(481, 531):
    # Only indent lines that are not empty and not already fully indented (though we want to add 16 spaces to everything effectively? No, wait)
    # The current lines are at indent level 0 or 4. We need to add 16 spaces to the base level.
    # Actually, let's just add 16 spaces if it doesn't start with whitespace, and add 16 spaces to the existing whitespace.
    # Wait, some lines have 4 spaces.
    # Let's just prefix 16 spaces to every line from 481 to 530 if it's not a newline.
    if lines[i].strip():
        lines[i] = "                " + lines[i]

with codecs.open('app_restored.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
