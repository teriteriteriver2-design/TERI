import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

if 'import billing_db' not in content:
    content = 'import billing_db\n' + content

old_tracker = """    # API 한도 및 토큰 사용량 트래커
    try:
        used_tokens = sa_engine.API_USAGE_TOKENS
    except:
        used_tokens = 0
        
    monthly_limit = 500000 # 임의의 월 한도 (50만 토큰)
    remain_tokens = max(0, monthly_limit - used_tokens)
    usage_percent = (used_tokens / monthly_limit) * 100 if monthly_limit > 0 else 0
    est_cost = (used_tokens / 1000) * 0.01 * 1350 # 대략 $0.01/1k 토큰, 1350원/달러
    
    st.markdown(f\"\"\"
    <div style='background:#1E293B; padding:15px; border-radius:8px; margin-bottom:20px; color:white; display:flex; justify-content:space-between; align-items:center;'>
        <div>
            <span style='font-size:12px; color:#94A3B8; display:block;'>실시간 API 사용량 (GPT-4o)</span>
            <span style='font-size:18px; font-weight:bold; color:#38BDF8;'>{used_tokens:,} <span style='font-size:13px; color:#94A3B8; font-weight:normal;'>Tokens 소모</span></span>
        </div>
        <div style='text-align:right;'>
            <span style='font-size:12px; color:#94A3B8; display:block;'>남은 한도: {remain_tokens:,} Tokens (과금액: 약 {int(est_cost):,}원)</span>
            <div style='width: 150px; background: #334155; border-radius: 4px; height: 8px; margin-top:5px; overflow:hidden;'>
                <div style='width: {usage_percent}%; background: #38BDF8; height: 100%;'></div>
            </div>
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

content = content.replace(old_tracker, new_tracker)

codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
codecs.open('app.py', 'w', encoding='utf-8').write(content)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)

print('Patched app_v2.py successfully!')
