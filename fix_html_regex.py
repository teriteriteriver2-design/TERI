import re
file_path = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace any sequence of newlines/spaces between the </div> and the next <div style='display:flex
content = re.sub(r"(출처:[^<]+</div>)\s+<div style='display:flex", r"\1\n<div style='display:flex", content)
content = re.sub(r"(</span></h3>)\s+<div style='color:#6B7280", r"\1\n<div style='color:#6B7280", content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Regex replacement successful!")
