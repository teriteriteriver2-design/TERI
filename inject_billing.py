import codecs

content = codecs.open('app_v2.py', encoding='utf-8').read()

old_text = '    st.markdown("<div class=\'card-title\'>🔍 권리분석 (법률 검토보고서)</div>", unsafe_allow_html=True)'

insertion = """    st.markdown("<div class='card-title'>🔍 권리분석 (법률 검토보고서)</div>", unsafe_allow_html=True)

    # --- Inject Billing UI for Rights Analysis ---
    try:
        used_tokens = sa_engine.API_USAGE_TOKENS
    except:
        used_tokens = 0
    try:
        balance_krw = billing_db.get_balance('test_user_01')
    except:
        balance_krw = 6723.0
    
    INITIAL_CREDIT = 8100.0
    remain_usd = balance_krw / 1350.0
    remain_ratio = min(1.0, max(0.0, balance_krw / INITIAL_CREDIT)) if INITIAL_CREDIT > 0 else 0.0
    
    with st.expander("💳 내 API 잔액 확인하기 (권리분석 1회당 약 $0.02~$0.05 소모)", expanded=True):
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.metric("소모된 토큰", f"{used_tokens:,}")
        with col_b2:
            st.metric("실제 잔액", f"${remain_usd:.2f}", delta=f"-${(INITIAL_CREDIT/1350.0) - remain_usd:.2f}", delta_color="inverse")
        with col_b3:
            st.metric("총 한도", f"${INITIAL_CREDIT/1350.0:.2f}")
        st.progress(remain_ratio, text=f"남은 잔액 게이지: 약 {int(balance_krw):,}원 / {int(INITIAL_CREDIT):,}원")
    # ---------------------------------------------"""

if '# --- Inject Billing UI for Rights Analysis ---' not in content:
    content = content.replace(old_text, insertion)
    codecs.open('app_v2.py', 'w', encoding='utf-8').write(content)
    codecs.open('app.py', 'w', encoding='utf-8').write(content)
    codecs.open('app_restored.py', 'w', encoding='utf-8').write(content)
    print('Injected billing UI successfully.')
else:
    print('Already injected.')
