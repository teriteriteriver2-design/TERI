import codecs

with codecs.open('app_restored.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(534, 611):
    if lines[i].strip():
        lines[i] = "    " + lines[i]

for i in range(988, 1038):
    if lines[i].strip():
        if 988 <= i <= 1001:
            lines[i] = "        " + lines[i].lstrip() if i == 988 else "        " + lines[i]
        else:
            lines[i] = "        " + lines[i]

with codecs.open('app_restored.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
