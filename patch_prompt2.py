import codecs
import re

with codecs.open('speedauction_engine.py', 'r', 'utf-8') as f:
    content = f.read()

# Find the start of analyze_registry_byod
start_idx = content.find('def analyze_registry_byod')
if start_idx == -1:
    print("Cannot find analyze_registry_byod")
    exit(1)

# Find where the prompt ends
end_idx = content.find('parsed_data = None', start_idx)

new_func = '''def analyze_registry_byod(self, text_input=None, image_b64_list=None):
        print(f"[SpeedAuctionEngine] BYOD 수동 데이터 기반 권리분석 스캔 시작...")
        
        system_prompt = """
        당신은 경매를 처음 접하는 왕초보를 위한 1타 과외선생님이자 권리분석 전문가입니다.
        주어진 등기부등본이나 매각물건명세서를 바탕으로 가장 쉽고 친절하게 권리분석 결과를 알려주세요.
        법률 용어를 사용할 때는 반드시 중학생도 이해할 수 있는 쉬운 비유나 설명을 괄호() 안에 덧붙여야 합니다.
        
        CRITICAL INSTRUCTIONS FOR THE REPORT:
        1. 첫 번째 줄에 반드시 신호등(🟢초록색-입찰GO / 🟡노란색-확인필요 / 🔴빨간색-입찰포기) 이모지를 넣고 1줄 핵심 요약을 작성하세요.
           예: "🟢 [안전] 낙찰금액 외에 추가로 물어줘야 할 빚이 0원입니다. 맘 편히 입찰하셔도 좋습니다!"
        2. '말소기준권리' (낙찰자가 인수하지 않고 소멸되는 기준선)를 찾아 쉽게 설명해주세요.
        3. '대항력'(세입자가 돈을 다 받을 때까지 안 나가고 버틸 수 있는 파워) 유무를 분석하고, "내 지갑에서 추가로 나가는 돈이 얼마인지"를 명확히 계산해주세요.
        4. 명도(기존 거주자를 내보내는 과정) 난이도를 '매우 쉬움', '보통', '위험(소송 대비)' 등으로 나누어 현실적으로 어떻게 대처해야 하는지 초보자 눈높이에서 설명해주세요.
        5. 구조는 반드시 다음 4개의 마크다운 헤더를 정확히 사용해야 합니다:
           **[STEP 1. 👑 초보자 맞춤형 1줄 핵심 요약]**
           **[STEP 2. 📝 쉬운 권리분석 (말소기준권리란?)]**
           **[STEP 3. 💰 내 주머니에서 추가로 나가는 돈 (대항력)]**
           **[STEP 4. 🏠 집 비우기(명도) 난이도 및 꿀팁]**
        
        Output ONLY in JSON format, and MUST BE IN KOREAN:
        {
            "tenant_summary": "초보자가 읽기 쉬운 다정하고 직관적인 설명 텍스트. 위에 지정된 4개의 헤더를 반드시 포함.",
            "is_safe": boolean,
            "estimated_deposit_manwon": integer,
            "malso_standard": "말소기준권리의 이름과 날짜",
            "raw_registry_text": "등기부에서 판단 근거가 된 텍스트 2~3줄 요약"
        }
        """
        
        '''

content = content[:start_idx] + new_func + content[end_idx:]

with codecs.open('speedauction_engine.py', 'w', 'utf-8') as f:
    f.write(content)

print("Prompt fully patched.")
