import codecs

with codecs.open('app_restored.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(390, 430):
    if lines[i].strip():
        lines[i] = "                    " + lines[i] # 20 spaces inside for loop

lines[430] = "                html_map = f\"\"\"\n" # 16 spaces
for i in range(431, 481):
    pass # html string content doesn't need python indentation technically, but we can leave it.

with codecs.open('app_restored.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
