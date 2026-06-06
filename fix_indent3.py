import codecs

with codecs.open('app_restored.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(788, 860):
    if lines[i].startswith("            "):
        lines[i] = lines[i][8:]

with codecs.open('app_restored.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
