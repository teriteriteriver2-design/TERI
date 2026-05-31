import os
import re

file_path = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/gap_sniper.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add import report_generator
if 'import report_generator' not in content:
    content = content.replace('import json', 'import json\nimport report_generator')

# 2. Add send_sniper_telegram_pdf function right after send_sniper_telegram_alert
pdf_func = """
def send_sniper_telegram_pdf(message, pdf_bytes, filename):
    url = f"https://api.telegram.org/bot{SNIPER_BOT_TOKEN}/sendDocument"
    files = {"document": (filename, pdf_bytes, "application/pdf")}
    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data, files=files, timeout=10)
    except Exception as e:
        print(f"Telegram PDF 전송 에러: {e}")
"""
if 'def send_sniper_telegram_pdf' not in content:
    content = content.replace('def load_history():', pdf_func + '\ndef load_history():')

# 3. Modify check_new_alerts logic
# Instead of new_alerts.append(msg), we do new_alerts.append((msg, title))
content = content.replace('new_alerts.append(msg)', 'new_alerts.append((msg, title))')

# 4. Modify the sending loop at the end
old_send_loop = """        for alert_msg in new_alerts[:5]:
            send_sniper_telegram_alert(alert_msg)"""

new_send_loop = """        for alert_msg, alert_title in new_alerts[:5]:
            try:
                # 임장노트 PDF 생성
                prop_data = {"prop_name": alert_title, "sell_price": "정보없음", "jeonse_price": "정보없음", "address": "확인필요"}
                pdf_bytes = report_generator.generate_pdf_report(prop_data, "급매물(갭투자) 스나이퍼 봇 발견 매물입니다.")
                send_sniper_telegram_pdf(alert_msg, pdf_bytes, f"임장보고서_{alert_title[:10]}.pdf")
            except Exception as e:
                print(f"PDF 생성/전송 실패: {e}")
                send_sniper_telegram_alert(alert_msg)"""

content = content.replace(old_send_loop, new_send_loop)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Sniper bot successfully patched with Imjang Note PDF!")
