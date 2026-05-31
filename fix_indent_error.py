import os

file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the bad helper function
helper_func = """
def format_korean_money(amount_manwon):
    if amount_manwon == 0:
        return "0만원"
    is_negative = amount_manwon < 0
    abs_amt = abs(amount_manwon)
    uk = abs_amt // 10000
    man = abs_amt % 10000
    
    parts = []
    if uk > 0:
        parts.append(f"{uk:,}억")
    if man > 0:
        parts.append(f"{man:,}만")
    
    result = " ".join(parts) + "원"
    if is_negative:
        result = "-" + result
    return result
"""

# Remove it from its current location
content = content.replace(helper_func, "")

# Insert it at the top after imports (around line 15 where report_generator is)
if "def format_korean_money" not in content:
    content = content.replace("import report_generator", "import report_generator\n" + helper_func)

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Indentation fixed!")
