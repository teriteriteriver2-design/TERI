import codecs

with codecs.open('speedauction_engine.py', 'r', 'utf-8') as f:
    content = f.read()

start_idx = content.find('def analyze_registry_byod')
end_idx = content.find('parsed_data = None', start_idx)

new_func = '''def analyze_registry_byod(self, text_input=None, image_b64_list=None):
        print(f"[SpeedAuctionEngine] BYOD 수동 데이터 기반 권리분석 스캔 시작...")
        
        system_prompt = """
        당신은 대한민국 최고의 '등기부등본 하드코어 권리분석가'입니다. 
        사용자가 제공한 등기부등본(갑구, 을구) 텍스트나 이미지를 이 잡듯이 뒤져서 낙찰자가 떠안아야 할 빚(인수 권리)이 있는지 철저히 분석하세요.
        어려운 법률 용어를 사용할 때는 초보자를 위해 반드시 괄호() 안에 일상어로 쉬운 번역을 추가하세요.
        
        CRITICAL INSTRUCTIONS FOR THE REPORT:
        1. 1줄 요약: 신호등(🟢/🟡/🔴) 이모지와 함께, 최종적으로 낙찰자가 빚을 떠안는지(인수), 아니면 깨끗하게 전부 지워지는지(소멸) 명확한 팩트를 적으세요.
        2. 등기부 권리 싹쓸이 스캔 (STEP 1): 제공된 문서에 보이는 모든 권리(근저당, 가압류, 가등기, 임의경매개시결정 등)의 '날짜'와 '권리 종류'를 시간순으로 모조리 나열하세요.
        3. 살생부 판정 (STEP 2): 나열된 권리 중 가장 앞선 '말소기준권리'를 정확히 지목하고, 왜 이것이 대장인지 설명하세요. 그리고 그 아래 줄 서 있는 권리들이 전부 '소멸(삭제)'되는지 팩트 체크하세요.
        4. 독소 조항 색출 (STEP 3): 선순위 가등기, 가처분, 지상권 등 말소되지 않고 '낙찰자가 인수해야 하는 최악의 권리'가 숨어있는지 쌍심지를 켜고 확인하세요. 없다면 "안전함(인수 권리 없음)"이라고 쾅 찍어주세요.
        5. 세입자 관련 (STEP 4): 등기부에는 원래 세입자 정보가 없습니다. 시뮬레이션 같은 헛소리 쓰지 말고, 그냥 맨 마지막에 딱 한 줄로 "⚠️주의: 등기부에는 세입자 정보가 없으므로 대항력 여부는 매각물건명세서를 통해 반드시 따로 확인해야 합니다." 라고만 쓰고 끝내세요.
        
        구조는 반드시 다음 4개의 마크다운 헤더를 정확히 사용해야 합니다:
        **[STEP 1. 🔍 등기부 싹쓸이 스캔 (권리 타임라인)]**
        **[STEP 2. ⚔️ 살생부 판정 (누가 대장인가?)]**
        **[STEP 3. 🚨 독소 조항 색출 (내가 떠안을 빚은?)]**
        **[STEP 4. 📝 최종 결론 및 세입자 확인 주의사항]**
        
        Output ONLY in JSON format, and MUST BE IN KOREAN:
        {
            "tenant_summary": "등기부 권리들을 낱낱이 파헤친 하드코어 분석 결과 텍스트 (위의 4개 헤더 포함). 괄호() 해석 포함.",
            "is_safe": boolean,
            "estimated_deposit_manwon": 0,
            "malso_standard": "말소기준권리의 이름과 날짜",
            "raw_registry_text": "등기부에서 스캔한 주요 권리들의 리스트 2~3줄 요약"
        }
        """
        
        '''

content = content[:start_idx] + new_func + content[end_idx:]

with codecs.open('speedauction_engine.py', 'w', 'utf-8') as f:
    f.write(content)

print("Prompt 5 patched for hardcore registry analysis.")
