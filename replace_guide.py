import codecs
import re

content = codecs.open('app_v2.py', encoding='utf-8').read()

old_block = """    with st.expander("[안내] AI 비서는 언제 토큰(비용)을 소모하나요?"):
        st.markdown(\"""
**1. 사용자의 의도 분석 (가장 적게 소모):**
사용자가 채팅창에 입력한 자연어 문장을 분석하여 어떤 동작을 해야 할지 판단할 때 (평균 100~300 토큰)

**2. 대법원 경매 매물 딥스캔 & 요약:**
특정 지역의 경매 물건 리스트와 상세 정보(감정가, 최저가 등)를 가져오고 정리할 때 (평균 500~1,000 토큰)

**3. 재개발/재건축 구역 분석:**
해당 지역의 재개발 진행 단계와 호재, 커뮤니티 의견을 분석하여 답변을 생성할 때 (평균 800~1,500 토큰)

**4. 권리분석 및 등기부등본 스캔 (가장 많이 소모):**
등기부등본 텍스트를 통째로 읽거나 카카오맵 인프라 요약을 종합적으로 판단할 때 (평균 1,500~3,000 토큰 이상)
        \""")"""

new_block = """    st.markdown('''
    <div style="background-color: #1E293B; border-left: 4px solid #38BDF8; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
        <h4 style="color: #38BDF8; margin-top: 0; font-size: 15px;">[안내] AI 비서는 언제 토큰(비용)을 소모하나요?</h4>
        <ul style="color: #CBD5E1; font-size: 13px; line-height: 1.6; margin-bottom: 0; padding-left: 20px;">
            <li><b>1. 사용자의 의도 분석 (가장 적게 소모):</b> 채팅창에 입력한 문장을 분석하여 동작을 판단할 때 (평균 100~300 토큰)</li>
            <li><b>2. 매물 딥스캔 & 요약:</b> 특정 지역의 물건 리스트와 상세 정보를 가져오고 정리할 때 (평균 500~1,000 토큰)</li>
            <li><b>3. 재개발/재건축 구역 분석:</b> 재개발 진행 단계와 호재, 커뮤니티 의견을 분석하여 답변할 때 (평균 800~1,500 토큰)</li>
            <li><b>4. 권리분석 및 등기부 스캔 (가장 많이 소모):</b> 등기부등본 전체를 읽거나 인프라 요약을 종합 판단할 때 (평균 1,500~3,000 토큰 이상)</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)"""

if old_block in content:
    content = content.replace(old_block, new_block)
    codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
    codecs.open('app.py', 'w', encoding='utf-8').write(content)
    codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
    print("Replaced expander with HTML successfully!")
else:
    print("Block not found. Trying regex.")
    # Fallback to regex if exact match fails due to line endings
    content = re.sub(r'with st\.expander\("\[안내\].*?"\):\s*st\.markdown\("""\s*\*\*1.*?\s*"""\)', new_block, content, flags=re.DOTALL)
    codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
    codecs.open('app.py', 'w', encoding='utf-8').write(content)
    codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
    print("Replaced using regex.")
