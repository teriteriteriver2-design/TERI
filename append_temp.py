func_code = """
def summarize_daily_briefing(news_list):
    if not news_list:
        return "최신 부동산 뉴스를 수집하지 못했습니다."
    import os, requests
    context = "\\n".join([f"- 제목: {n.get('title', '')}\\n  내용: {n.get('description', '')}" for n in news_list])
    system_prompt = '''
    당신은 대한민국 최고의 부동산 및 재개발/재건축 애널리스트입니다.
    주어진 최신 뉴스 기사들을 바탕으로, 텔레그램으로 매일 아침 전송될 '일일 부동산 시황 브리핑'을 작성해 주세요.
    가독성이 매우 중요하므로 이모지를 적절히 사용하고, 3가지 핵심 섹션으로 나누어 주세요.
    1. 📰 **오늘의 부동산 핫이슈 (재개발/정책/시장 동향)**
    2. 🔥 **현재 사람들이 가장 많이 언급하는 핫한 동네/지역**
    3. 💡 **오늘의 투자 인사이트 (전문가의 한 줄 평)**
    '''
    try:
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}', 'Content-Type': 'application/json'}
        data = {'model': 'gpt-4o-mini', 'messages': [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': context}], 'temperature': 0.5}
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"브리핑 생성 중 오류 발생: {e}"
"""
with open('inference_engine.py', 'a', encoding='utf-8') as f:
    f.write('\n' + func_code)
