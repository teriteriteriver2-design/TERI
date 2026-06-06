import os

engine_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/speedauction_engine.py'
with open(engine_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_fetch = False
for i, line in enumerate(lines):
    if line.startswith('def fetch_jeonse_heatmap_data(self):'):
        in_fetch = True
        new_lines.append('    ' + line)
        continue
    
    if in_fetch:
        if line.startswith('def '):
            in_fetch = False
            new_lines.append(line)
        else:
            if line.strip() != "":
                if not line.startswith('        '):
                    new_lines.append('    ' + line.lstrip())
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
    else:
        new_lines.append(line)

with open(engine_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Indentation fixed")
