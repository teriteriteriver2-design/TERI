import os
import re

file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

# Helper function code
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

# Insert the helper function right before it's needed (before the for loop)
old_loop_start = "            for idx, item in enumerate(market_data_list[:10]):"
if "def format_korean_money" not in content:
    content = content.replace(old_loop_start, helper_func + "\n" + old_loop_start)

# Now replace the formatting in the HTML block
# {sale_min:,}만원 -> {format_korean_money(sale_min)}
content = content.replace("{sale_min:,}만원", "{format_korean_money(sale_min)}")
content = content.replace("{jeonse_min:,}만원", "{format_korean_money(jeonse_min)}")
content = content.replace("{gap:,}만원", "{format_korean_money(gap)}")

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Money format patched!")
