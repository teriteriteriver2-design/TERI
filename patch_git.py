import os

file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/.github/workflows/sniper_cron.yml'
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = """
          git add sniper_history.txt market_data.json pending_analysis.json || true
          git diff --quiet && git diff --staged --quiet || (git commit -m "Update sniper history" && git push)
"""

new_logic = """
          git add sniper_history.txt || true
          git add market_data.json || true
          git add pending_analysis.json || true
          git add billing.sqlite || true
          git diff --quiet && git diff --staged --quiet || (git commit -m "Update sniper history" && git push)
"""

content = content.replace(old_logic.strip(), new_logic.strip())

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated git add logic to be atomic and safe!")
