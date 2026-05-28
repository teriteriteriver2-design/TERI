import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

old_markdown = """        **1. 사용자의 의도 분석 (가장 적게 소모):**
        사용자가 채팅창에 입력한 자연어 문장을 분석하여 어떤 동작을 해야 할지 판단할 때 (평균 100~300 토큰)
        
        **2. 대법원 경매 매물 딥스캔 & 요약:**
        특정 지역의 경매 물건 리스트와 상세 정보(감정가, 최저가 등)를 가져오고 정리할 때 (평균 500~1,000 토큰)
        
        **3. 재개발/재건축 구역 분석:**
        해당 지역의 재개발 진행 단계와 호재, 커뮤니티 의견을 분석하여 답변을 생성할 때 (평균 800~1,500 토큰)
        
        **4. 권리분석 및 등기부등본 스캔 (가장 많이 소모):**
        등기부등본 텍스트를 통째로 읽거나 카카오맵 인프라 요약을 종합적으로 판단할 때 (평균 1,500~3,000 토큰 이상)"""

new_markdown = """**1. 사용자의 의도 분석 (가장 적게 소모):**
사용자가 채팅창에 입력한 자연어 문장을 분석하여 어떤 동작을 해야 할지 판단할 때 (평균 100~300 토큰)

**2. 대법원 경매 매물 딥스캔 & 요약:**
특정 지역의 경매 물건 리스트와 상세 정보(감정가, 최저가 등)를 가져오고 정리할 때 (평균 500~1,000 토큰)

**3. 재개발/재건축 구역 분석:**
해당 지역의 재개발 진행 단계와 호재, 커뮤니티 의견을 분석하여 답변을 생성할 때 (평균 800~1,500 토큰)

**4. 권리분석 및 등기부등본 스캔 (가장 많이 소모):**
등기부등본 텍스트를 통째로 읽거나 카카오맵 인프라 요약을 종합적으로 판단할 때 (평균 1,500~3,000 토큰 이상)"""

if old_markdown in content:
    content = content.replace(old_markdown, new_markdown)
    codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
    codecs.open('app.py', 'w', encoding='utf-8').write(content)
    codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
    print('Fixed markdown indentation!')
else:
    print('Markdown not found.')
