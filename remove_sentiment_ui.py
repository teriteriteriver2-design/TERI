import re

with open('C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Delete everything from # --- FOMO / FUD to components.html(...)
start_str = "# --- FOMO / FUD Sentiment Gauge ---"
end_str = "components.html(\"<body style=\\\"margin:0; padding:10px; font-family:sans-serif;\\\">\" + gauge_html + \"</body>\", height=420)"

start_idx = content.find(start_str)
end_idx = content.find(end_str)

if start_idx != -1 and end_idx != -1:
    end_idx += len(end_str)
    
    new_content = content[:start_idx] + "st.info('👉 오늘의 민심 데이터는 매일 아침 7:37 텔레그램 데일리 브리핑에 통합되어 함께 발송됩니다! (API 비용 절약)')\n" + content[end_idx:]
    with open('C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully removed Sentiment UI from app_v2.py")
else:
    print("Could not find start or end index.")
