import os

file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/.github/workflows/sniper_cron.yml'
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('uses: actions/checkout@v3', 'uses: actions/checkout@v4')
content = content.replace('uses: actions/setup-python@v4', 'uses: actions/setup-python@v5')

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated actions to v4/v5 in sniper_cron.yml!")
