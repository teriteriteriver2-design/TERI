import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

old_tracker = """    # API 한도 및 토큰 사용량 트래커 (자체 DB 연동)
    try:
        used_tokens = sa_engine.API_USAGE_TOKENS
    except:
        used_tokens = 0
        
    try:
        balance_krw = billing_db.get_balance('test_user_01')
    except:
        balance_krw = 8100.0
        
    INITIAL_CREDIT = 8100.0
    usage_percent = min(100, max(0, ((INITIAL_CREDIT - balance_krw) / INITIAL_CREDIT) * 100)) if INITIAL_CREDIT > 0 else 0
    
    if balance_krw <= 0:
        bar_color = "#EF4444" # Red when empty
        st.error("⚠️ 충전된 크레딧(포인트)이 모두 소진되었습니다. AI 비서 기능이 제한될 수 있습니다.")
    elif balance_krw < 1000:
        bar_color = "#F59E0B" # Orange when low
    else:
        bar_color = "#38BDF8" # Blue normally
    
    st.markdown(f\"\"\"
    <div style='background:#1E293B; padding:15px; border-radius:8px; margin-bottom:20px; color:white; display:flex; justify-content:space-between; align-items:center;'>
        <div>
            <span style='font-size:12px; color:#94A3B8; display:block;'>실시간 API 사용량 (세션 누적)</span>
            <span style='font-size:18px; font-weight:bold; color:#38BDF8;'>{used_tokens:,} <span style='font-size:13px; color:#94A3B8; font-weight:normal;'>Tokens 소모</span></span>
        </div>
        <div style='text-align:right;'>
            <span style='font-size:13px; color:#94A3B8; display:block;'>내 지갑 남은 잔액: <b style='color:white; font-size:16px;'>{int(balance_krw):,}원</b></span>
            <div style='width: 150px; background: #334155; border-radius: 4px; height: 8px; margin-top:5px; overflow:hidden;'>
                <div style='width: {usage_percent}%; background: {bar_color}; height: 100%; transition: width 0.3s ease;'></div>
            </div>
            <span style='font-size:10px; color:#64748B;'>초기 자본: {int(INITIAL_CREDIT):,}원</span>
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)"""

new_tracker = """    # API 한도 및 토큰 사용량 트래커 (자체 DB 연동)
    try:
        used_tokens = sa_engine.API_USAGE_TOKENS
    except:
        used_tokens = 0
        
    try:
        balance_krw = billing_db.get_balance('test_user_01')
    except:
        balance_krw = 6723.0
        
    INITIAL_CREDIT = 8100.0 # 6 dollars * 1350
    remain_usd = balance_krw / 1350.0
    
    usage_percent = min(100, max(0, ((INITIAL_CREDIT - balance_krw) / INITIAL_CREDIT) * 100)) if INITIAL_CREDIT > 0 else 0
    
    if balance_krw <= 0:
        bar_color = "#EF4444" # Red when empty
        st.error("⚠️ 충전된 크레딧이 모두 소진되었습니다.")
    elif balance_krw < 1000:
        bar_color = "#F59E0B" # Orange when low
    else:
        bar_color = "#38BDF8" # Blue normally
    
    st.markdown(f\"\"\"
    <div style='background:#1E293B; padding:15px; border-radius:8px; margin-bottom:10px; color:white; display:flex; justify-content:space-between; align-items:center;'>
        <div>
            <span style='font-size:12px; color:#94A3B8; display:block;'>실시간 세션 누적 토큰 (GPT-4o)</span>
            <span style='font-size:18px; font-weight:bold; color:#38BDF8;'>{used_tokens:,} <span style='font-size:13px; color:#94A3B8; font-weight:normal;'>Tokens 소모</span></span>
        </div>
        <div style='text-align:right;'>
            <span style='font-size:13px; color:#94A3B8; display:block;'>실제 잔액: <b style='color:white; font-size:16px;'>${remain_usd:.2f}</b> <span style='font-size:11px;'>(약 {int(balance_krw):,}원)</span></span>
            <div style='width: 150px; background: #334155; border-radius: 4px; height: 8px; margin-top:5px; overflow:hidden;'>
                <div style='width: {usage_percent}%; background: {bar_color}; height: 100%; transition: width 0.3s ease;'></div>
            </div>
            <span style='font-size:10px; color:#64748B;'>총 결제 한도: $6.00</span>
        </div>
    </div>
    \"\"\", unsafe_allow_html=True)
    
    with st.expander("ℹ️ AI 비서는 언제 토큰(비용)을 소모하나요?"):
        st.markdown(\"\"\"
        **1. 사용자의 의도 분석 (가장 적게 소모):**
        사용자가 채팅창에 입력한 자연어 문장을 분석하여 어떤 동작을 해야 할지 판단할 때 (평균 100~300 토큰)
        
        **2. 대법원 경매 매물 딥스캔 & 요약:**
        특정 지역의 경매 물건 리스트와 상세 정보(감정가, 최저가 등)를 가져오고 정리할 때 (평균 500~1,000 토큰)
        
        **3. 재개발/재건축 구역 분석:**
        해당 지역의 재개발 진행 단계와 호재, 커뮤니티 의견을 분석하여 답변을 생성할 때 (평균 800~1,500 토큰)
        
        **4. 권리분석 및 등기부등본 스캔 (가장 많이 소모):**
        등기부등본 텍스트를 통째로 읽거나 카카오맵 인프라 요약을 종합적으로 판단할 때 (평균 1,500~3,000 토큰 이상)
        \"\"\")
"""

content = content.replace(old_tracker, new_tracker)

codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
codecs.open('app.py', 'w', encoding='utf-8').write(content)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)

print('Patched app_v2.py successfully!')
