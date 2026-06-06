import os

with open('C:/Users/뀽제/OneDrive/바탕 화면/BU/inference_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
idx = next(i for i, l in enumerate(lines) if 'def summarize_daily_briefing' in l)
new_lines = lines[:idx]
    
new_func = '''def summarize_daily_briefing(news_list):
    """
    Summarizes a list of daily real estate news into a Telegram-friendly morning briefing.
    """
    if not news_list:
        return "최신 부동산 뉴스를 수집하지 못했습니다."
        
    import os, requests, datetime
    today_str = datetime.datetime.now().strftime("%Y년 %m월 %d일")
    context = "\\n".join([f"- 제목: {n.get('title', '')}\\n  내용: {n.get('description', '')}" for n in news_list])
    
    system_prompt = f"""
    당신은 대한민국 최고의 부동산 및 재개발/재건축 애널리스트입니다.
    오늘 날짜는 {today_str} 입니다. 절대로 과거 날짜(예: 2023년)를 브리핑에 적지 마세요.
    주어진 최신 뉴스 기사들을 바탕으로, 텔레그램으로 매일 아침 전송될 '일일 부동산 시황 브리핑'을 작성해 주세요.
    가독성이 매우 중요하므로 이모지를 적절히 사용하고, 아래의 4가지 핵심 섹션으로 나누어 서울과 지방을 분리해서 요약해 주세요.

    1. 📰 **오늘의 부동산 핵심 이슈 (세금/정책/법령/전국 동향)**
    2. 🏙️ **[서울/수도권] 동향 및 핫플레이스 요약**
    3. 🏞️ **[지방/기타지역] 동향 및 핫플레이스 요약**
    4. 💡 **오늘의 투자 인사이트 (애널리스트 한 줄 평)**

    주의사항:
    - 마크다운 문법(```)은 사용하지 마세요. 텔레그램 HTML 포맷에 맞게 <b>굵게</b> 태그를 사용해도 됩니다.
    - 너무 길지 않게, 모바일 화면에서 한눈에 읽히도록 핵심만 짚어주세요.
    - 브리핑 제목에 반드시 오늘 날짜({today_str})를 포함하세요.
    """
    
    try:
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}', 'Content-Type': 'application/json'}
        data = {'model': 'gpt-4o-mini', 'messages': [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': context}], 'temperature': 0.5}
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"브리핑 생성 중 오류 발생: {e}"
'''
new_lines.append(new_func)
with open('C:/Users/뀽제/OneDrive/바탕 화면/BU/inference_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Fixed inference_engine.py')
