import codecs
import re

with codecs.open('speedauction_engine.py', 'r', 'utf-8') as f:
    content = f.read()

# Replace Instructions 1-6
old_inst = """        CRITICAL INSTRUCTIONS FOR THE REPORT:
        1. Write an EXTREMELY DETAILED, multi-paragraph professional legal report (at least 500 words) in Korean.
        2. Identify the '말소기준권리' (e.g., 근저당, 가압류, 압류, 담보가등기, 경매개시결정 중 가장 앞선 것). If all previous rights in 을구 are canceled (말소), the 경매개시결정 becomes the Malso standard.
        3. If there is no mention of a tenant (임차인/전입세대) in the provided text, YOU MUST EXPLICITLY WARN the user that "전입세대열람 내역 및 매각물건명세서가 누락되어 임차인 대항력 유무를 확정할 수 없으므로 반드시 추가 확인이 필요하다"고 작성할 것.
        4. Cite specific laws (e.g. 민사집행법 제91조, 주택임대차보호법 제3조) to explain why rights are extinguished or assumed.
        5. Evaluate the eviction (명도) difficulty based on the available data.
        6. Structure your `tenant_summary` output EXACTLY with these 3 Markdown headers:
           **[STEP 2. AI 딥 권리분석 요약]**
           **[STEP 3. 인수 보증금 및 대항력 분석]**
           **[STEP 4. 명도 시뮬레이션 및 소송 전략]**"""

new_inst = """        CRITICAL INSTRUCTIONS FOR THE REPORT:
        1. 첫 번째 줄에 반드시 신호등(🟢초록색-입찰GO / 🟡노란색-확인필요 / 🔴빨간색-입찰포기) 이모지를 넣고 1줄 핵심 요약을 작성하세요.
           예: "🟢 [안전] 낙찰금액 외에 추가로 물어줘야 할 빚이 0원입니다. 맘 편히 입찰하셔도 좋습니다!"
        2. '말소기준권리' (낙찰자가 인수하지 않고 소멸되는 기준선)를 찾아 쉽게 설명해주세요.
        3. '대항력'(세입자가 돈을 다 받을 때까지 안 나가고 버틸 수 있는 파워) 유무를 분석하고, "내 지갑에서 추가로 나가는 돈이 얼마인지"를 명확히 계산해주세요.
        4. 명도(기존 거주자를 내보내는 과정) 난이도를 '매우 쉬움', '보통', '위험(소송 대비)' 등으로 나누어 현실적으로 어떻게 대처해야 하는지 초보자 눈높이에서 설명해주세요.
        5. 구조는 반드시 다음 4개의 마크다운 헤더를 정확히 사용해야 합니다:
           **[STEP 1. 👑 초보자 맞춤형 1줄 핵심 요약]**
           **[STEP 2. 📝 쉬운 권리분석 (말소기준권리란?)]**
           **[STEP 3. 💰 내 주머니에서 추가로 나가는 돈 (대항력)]**
           **[STEP 4. 🏠 집 비우기(명도) 난이도 및 꿀팁]**"""

content = content.replace(old_inst, new_inst)

# Replace JSON block
old_json = """        Output ONLY in JSON format, and MUST BE IN KOREAN:
        {
            "tenant_summary": "A highly detailed, robust, multi-paragraph professional legal report (very long and specific). Use Markdown formatting.",
            "is_safe": boolean,
            "estimated_deposit_manwon": integer,
            "malso_standard": "Name and date of the right that acts as the Malso standard (e.g. 2024.07.19 임의경매개시결정)",
            "raw_registry_text": "Extract only the most critical 5-10 lines of the registry (갑구 and 을구) that determine the Malso standard. DO NOT transcribe the entire text to avoid output limits. If no text can be extracted, output '⚠️ 등기부 텍스트 판독 실패'."
        }"""

new_json = """        Output ONLY in JSON format, and MUST BE IN KOREAN:
        {
            "tenant_summary": "초보자가 읽기 쉬운 다정하고 직관적인 설명 텍스트. 위에 지정된 4개의 헤더를 반드시 포함할 것.",
            "is_safe": boolean,
            "estimated_deposit_manwon": integer,
            "malso_standard": "말소기준권리의 이름과 날짜",
            "raw_registry_text": "등기부에서 판단 근거가 된 텍스트 2~3줄 요약"
        }"""

content = content.replace(old_json, new_json)

# Also update app_v2.py to remove the old STEP 1 hardcoded text if it exists.
with codecs.open('speedauction_engine.py', 'w', 'utf-8') as f:
    f.write(content)

print("Patch complete.")
