import codecs

lines = codecs.open('app_v2.py', encoding='utf-8').read()

old_expander_1 = """        with st.expander("💸 대출 및 레버리지 설정", expanded=True):
            loan_amt = st.number_input("대출금 (만원)", value=int(bid_price*0.8), step=1000, key=f"loan_{p_case}")
            loan_rate = st.slider("금융 대출금리 (%)", min_value=2.0, max_value=8.0, value=4.5, step=0.1, key=f"rate_{p_case}")
        
        with st.expander("📉 취득세 및 부대비용 세팅", expanded=False):
            tax_rate_type = st.selectbox("취득세 부과 기준", ["무주택/1주택자 (1.1~3.5%)", "조정지역 2주택 (8.4%)", "조정지역 3주택 이상 (12.4%)"])
            if "1주택" in tax_rate_type:
                tax_rate = 0.011 if bid_price < 60000 else 0.022
            elif "8.4%" in tax_rate_type:
                tax_rate = 0.084
            else:
                tax_rate = 0.124
                
            repair_cost = st.number_input("명도 및 수리/인테리어 비용 (만원)", value=2000, step=100)
            legal_cost = st.number_input("법무사/중개 수수료 등 (만원)", value=300, step=50)
            
        with st.expander("🏠 임대 수익 설정", expanded=True):
            rent_deposit = st.number_input("받을 보증금 (만원)", value=5000, step=500, key=f"dep_{p_case}")
            rent_monthly = st.number_input("받을 월세 (만원)", value=120, step=5, key=f"mon_{p_case}")"""

new_expander_1 = """        st.markdown("<br><b style='color:#1E40AF;'>[1] 대출 및 레버리지 설정</b>", unsafe_allow_html=True)
        col_L1, col_L2 = st.columns(2)
        with col_L1:
            loan_amt = st.number_input("대출금 (만원)", value=int(bid_price*0.8), step=1000, key=f"loan_{p_case}")
        with col_L2:
            loan_rate = st.number_input("금융 대출금리 (%)", value=4.5, step=0.1, key=f"rate_{p_case}")
            
        st.markdown("<br><b style='color:#1E40AF;'>[2] 취득세 및 부대비용</b>", unsafe_allow_html=True)
        tax_rate_type = st.selectbox("취득세 부과 기준", ["무주택/1주택자 (1.1~3.5%)", "조정지역 2주택 (8.4%)", "조정지역 3주택 이상 (12.4%)"])
        if "1주택" in tax_rate_type:
            tax_rate = 0.011 if bid_price < 60000 else 0.022
        elif "8.4%" in tax_rate_type:
            tax_rate = 0.084
        else:
            tax_rate = 0.124
            
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            repair_cost = st.number_input("수리/명도 비용 (만원)", value=2000, step=100)
        with col_c2:
            legal_cost = st.number_input("법무/중개 등 (만원)", value=300, step=50)
            
        st.markdown("<br><b style='color:#1E40AF;'>[3] 임대 수익 설정</b>", unsafe_allow_html=True)
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            rent_deposit = st.number_input("받을 보증금 (만원)", value=5000, step=500, key=f"dep_{p_case}")
        with col_r2:
            rent_monthly = st.number_input("받을 월세 (만원)", value=120, step=5, key=f"mon_{p_case}")"""

new_text = lines.replace(old_expander_1, new_expander_1)

codecs.open('app_v2.py', 'w', encoding='utf-8').write(new_text)
codecs.open('app.py', 'w', encoding='utf-8').write(new_text)
codecs.open('app_restored.py', 'w', encoding='utf-8').write(new_text)

print("SUCCESS")
