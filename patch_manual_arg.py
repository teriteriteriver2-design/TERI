import os

file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = 'subprocess.run(["python", "gap_sniper.py"], check=True)'
new_code = 'subprocess.run(["python", "gap_sniper.py", "--manual"], check=True)'
content = content.replace(old_code, new_code)

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app_v2.py to use --manual mode!")
