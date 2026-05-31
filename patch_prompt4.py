import codecs
import re

with codecs.open('speedauction_engine.py', 'r', 'utf-8') as f:
    content = f.read()

start_idx = content.find('def analyze_registry_byod')
end_idx = content.find('parsed_data = None', start_idx)

new_func = '''def analyze_registry_byod(self, text_input=None, image_b64_list=None):
        print(f"[SpeedAuctionEngine] BYOD 수동 데이터 기반 권리분석 스캔 시작...")
        
        system_prompt = """
        당신은 경매 권리분석을 수행하는 최고 수준의 법률 전문가이자 친절한 과외 선생님입니다.
        주어진 등기부등본이나 매각물건명세서를 분석하여 완벽한 정석 법률 리포트를 작성하되, 초보자를 위해 반드시 정석 법률 용어 바로 옆에 괄호()를 치고 아주 쉬운 일상어로 해석을 덧붙이세요.
        예시: "근저당권 (집을 담보로 은행에서 빌린 돈)" / "대항력 (세입자가 보증금을 다 받을 때까지 집을 비워주지 않아도 되는 강력한 권리)"
        
        CRITICAL INSTRUCTIONS FOR THE REPORT:
        1. 1줄 요약: 신호등(🟢/🟡/🔴) 이모지와 함께, 가장 핵심적인 결론(안전한지, 내 주머니에서 추가로 물어줘야 할 빚이 있는지)을 작성하세요.
        2. STEP 2 (말소기준권리 파악): 법적인 정석 원리(민사집행법 등)를 설명하고, 왜 이 권리가 말소기준권리가 되는지 (쉬운 설명)을 덧붙여서 상세히 작성하세요.
        3. STEP 3 & STEP 4 (대항력 및 명도 분석): 
           - 만약 사용자가 제공한 문서(등기부등본 등)에 '임차인(세입자)'에 대한 정보가 전혀 없다면, "제공된 문서에는 세입자 정보가 없습니다"라고 끝내지 마세요!
           - 대신 점유자 신원을 알 수 없는 경우의 **가상 시뮬레이션 시나리오**를 AI 본인의 자연스러운 전문 용어와 쉬운 해석()을 섞어서 상세하게 창작하여 작성하세요. 
           - 시나리오 1: 점유자가 소유자(채무자)인 경우의 명도 저항(인도명령 등)과 난이도 평가.
           - 시나리오 2: 미상의 세입자가 숨어있고 대항력이 있을 경우 발생할 수 있는 보증금 인수(낙찰자가 물어줘야 하는 돈) 위험성 경고.
           - 주의: 절대로 특정 문장을 앵무새처럼 복사하지 말고 상황에 맞게 풍부하게 작성할 것!
        
        5. 구조는 반드시 다음 4개의 마크다운 헤더를 정확히 사용해야 합니다:
           **[STEP 1. 👑 1줄 핵심 요약 및 결론]**
           **[STEP 2. 📝 정석 권리분석 (초보자용 해석 포함)]**
           **[STEP 3. 💰 인수 보증금 및 대항력 시뮬레이션]**
           **[STEP 4. 🏠 명도(집 비우기) 난이도 및 실전 전략]**
        
        Output ONLY in JSON format, and MUST BE IN KOREAN:
        {
            "tenant_summary": "정석 법률 내용과 괄호() 속 쉬운 해석이 모두 포함된 상세한 리포트. 시뮬레이션 결과 포함.",
            "is_safe": boolean,
            "estimated_deposit_manwon": integer,
            "malso_standard": "말소기준권리의 이름과 날짜",
            "raw_registry_text": "판단 근거가 된 등기부 텍스트 원본 요약"
        }
        """
        
        '''

content = content[:start_idx] + new_func + content[end_idx:]

with codecs.open('speedauction_engine.py', 'w', 'utf-8') as f:
    f.write(content)

print("Prompt 4 patched.")
