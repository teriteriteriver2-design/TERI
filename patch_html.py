import os

file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the blank line issue in markdown HTML block
# Remove all double newlines inside that specific HTML block
# Actually, I'll just replace the specific section to ensure we remove blank lines
old_html = """                    <div style='color:#6B7280; font-size:13px; margin-bottom:15px; margin-top:5px;'>출처: {m_info.get('source', '네이버 시세')}</div>

                    <div style='display:flex; justify-content:space-between; align-items:center;'>"""

new_html = """                    <div style='color:#6B7280; font-size:13px; margin-bottom:15px; margin-top:5px;'>출처: {m_info.get('source', '네이버 시세')}</div>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>"""

content = content.replace(old_html, new_html)

old_html2 = """                    </div>
                    <div style='margin-top:15px; text-align:right;'>"""

new_html2 = """                    </div>
                    <div style='margin-top:15px; text-align:right;'>"""
# Wait, this one didn't have a blank line. The only blank line was after the 출처.

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Streamlit HTML blank line fixed!")
