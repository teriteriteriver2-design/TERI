import os

# 1. Fix auto_backup.py to push to master instead of main
backup_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/auto_backup.py'
with open(backup_file, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("b'refs/heads/main'", "b'refs/heads/master'")
content = content.replace("Rename branch to main", "Rename branch to master")
content = content.replace("Push to origin main", "Push to origin master")

with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Fix daily_scan.yml to run at 8:17 AM instead of 8:00 AM
daily_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/.github/workflows/daily_scan.yml'
with open(daily_file, 'r', encoding='utf-8') as f:
    daily_content = f.read()

daily_content = daily_content.replace("- cron: '0 23 * * *'", "- cron: '17 23 * * *'")

with open(daily_file, 'w', encoding='utf-8') as f:
    f.write(daily_content)

print("Branch and Cron fixed!")
