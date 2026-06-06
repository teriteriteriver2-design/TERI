import os

app_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'

with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """
    <div style="margin-top:20px; background:#F8FAFC; padding:15px; border-radius:12px; border-left:4px solid {text_color}; font-size:14px; color:#475569; line-height:1.6;">
        <b>🤖 GPT-4o 분석 요약:</b> {summary}
    </div>
</div>
"""

new_code = """
    <div style="margin-top:20px; background:#F8FAFC; padding:15px; border-radius:12px; border-left:4px solid {text_color}; font-size:14px; color:#475569; line-height:1.6;">
        <b>🤖 GPT-4o 분석 요약:</b> {summary}
"""

evidence_builder = """
evidence = sentiment_data.get("evidence", [])
evidence_html = ""
if evidence:
    evidence_html += "<div style='margin-top:15px; padding-top:15px; border-top:1px dashed #CBD5E1;'>"
    evidence_html += "<b style='color:#1E293B; font-size:13px;'>📝 커뮤니티 민심 팩트체크 (실제 인용구):</b><ul style='margin-top:8px; margin-bottom:0; padding-left:20px; font-size:13px; color:#64748B;'>"
    for item in evidence:
        q = item.get("quote", "").replace("<", "&lt;").replace(">", "&gt;")
        evidence_html += f"<li>{q}</li>"
    evidence_html += "</ul></div>"

gauge_html = gauge_html.replace('<b>🤖 GPT-4o 분석 요약:</b> {summary}', '<b>🤖 GPT-4o 분석 요약:</b> {summary}' + evidence_html)
"""

if old_code in content:
    content = content.replace(old_code, new_code + '    </div>\n</div>\n')

    # Now we need to append the evidence_builder logic right before `components.html(..., gauge_html)`
    
    comp_old = 'import streamlit.components.v1 as components\ncomponents.html("<body style=\\"margin:0; padding:10px; font-family:sans-serif;\\">" + gauge_html + "</body>", height=280)'
    
    comp_new = f"""
{evidence_builder}

import streamlit.components.v1 as components
components.html("<body style=\\"margin:0; padding:10px; font-family:sans-serif;\\">" + gauge_html + "</body>", height=320)
"""
    content = content.replace(comp_old, comp_new)
    
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patch applied!")
else:
    print("Could not find old code block.")
