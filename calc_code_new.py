# --------------------------------------------------------
# STEP 4: 초정밀 투자 분석 & 수익 계산기 (상세 세팅)
# --------------------------------------------------------
with tab_calc:
    if 'selected_prop' in st.session_state and st.session_state['selected_prop']:
        p_case = st.session_state['selected_prop'].get('case_number', 'unknown')
        p_name = st.session_state['selected_prop'].get('prop_name', 'unknown')
        
        try:
            p_min_val = int(st.session_state['selected_prop'].get('price_min', 0) or 0)
        except (ValueError, TypeError):
            p_min_val = 0
            
        try:
            p_eval_val = int(st.session_state['selected_prop'].get('price_eval', 0) or 0)
        except (ValueError, TypeError):
            p_eval_val = 0
            
        lat = st.session_state['selected_prop'].get('lat', 37.5665)
        lon = st.session_state['selected_prop'].get('lon', 126.9780)
    else:
        p_case = "unknown"
        p_name = "unknown"
        p_min_val = 64000
        p_eval_val = 80000
        lat = 37.5665
        lon = 126.9780
        
    col_sim, col_chart = st.columns([1, 1.2])
    
    with col_sim:
        st.markdown("<div class='card-title'>💰 초정밀 수익률 계산기</div>", unsafe_allow_html=True)
        st.info("세금, 부대비용 등을 모두 고려한 실 투자 수익률을 산출합니다.")
        
        bid_price = st.number_input("예상 입찰가 (만원)", value=p_min_val if p_min_val > 0 else 50000, step=1000, key=f"bid_{p_case}")
        
        with st.expander("💸 대출 및 레버리지 설정", expanded=True):
            loan_amt = st.number_input("대출금 (만원)", value=int(bid_price*0.8), step=1000, key=f"loan_{p_case}")
            loan_rate = st.slider("금융 대출금리 (%)", min_value=2.0, max_value=8.0, value=4.5, step=0.1, key=f"rate_{p_case}")
        
        with st.expander("📉 취득세 및 부대비용 세팅", expanded=False):
            tax_rate_type = st.selectbox("취득세 부과 기준", ["무주택/1주택자 (1.1~3.5%)", "조정지역 2주택 (8.4%)", "조정지역 3주택 이상 (12.4%)"])
            if "1주택" in tax_rate_type:
                tax_rate = 0.011 if bid_price < 60000 else 0.022 # Simplified
            elif "8.4%" in tax_rate_type:
                tax_rate = 0.084
            else:
                tax_rate = 0.124
                
            repair_cost = st.number_input("명도 및 수리/인테리어 비용 (만원)", value=2000, step=100)
            legal_cost = st.number_input("법무사/중개 수수료 등 (만원)", value=300, step=50)
            
        with st.expander("🏠 임대 수익 설정", expanded=True):
            rent_deposit = st.number_input("받을 보증금 (만원)", value=5000, step=500, key=f"dep_{p_case}")
            rent_monthly = st.number_input("받을 월세 (만원)", value=120, step=5, key=f"mon_{p_case}")
        
        tax_amt = bid_price * tax_rate
        total_additional_cost = tax_amt + repair_cost + legal_cost
        
        monthly_interest = (loan_amt * 10000 * (loan_rate / 100)) / 12
        net_monthly_cashflow = (rent_monthly * 10000) - monthly_interest
        
        actual_investment = (bid_price - loan_amt - rent_deposit) + total_additional_cost 
        
        if actual_investment <= 0:
            yield_str = "무한대 (무피 투자 달성!)"
        else:
            annual_net_profit = net_monthly_cashflow * 12
            yield_pct = (annual_net_profit / (actual_investment * 10000)) * 100
            yield_str = f"{round(yield_pct, 2)}%"
            
        st.markdown(f"""
        <div style='background:#F8FAFC; border:1px solid #CBD5E1; padding:20px; border-radius:12px; font-size:15px; margin-top:15px;'>
        <b style='color:#475569;'>실 투자금 (Equity):</b> {int(actual_investment):,} 만원<br>
        <span style='font-size:13px; color:gray;'>(입찰가 - 대출 - 보증금 + 취득세 + 수리/부대비용)</span><br><br>
        <b>매월 순수익 (Cash Flow):</b> <span style='color:#2563EB; font-size:22px; font-weight:900;'>{int(net_monthly_cashflow):,}원</span><br>
        <span style='font-size:13px; color:gray;'>(월세 {int(rent_monthly):,}만원 - 이자상환 {int(monthly_interest):,}원)</span><br><br>
        <b>연 수익률 (ROI):</b> <span style='color:red; font-size:18px; font-weight:800;'>{yield_str}</span>
        </div>
        """, unsafe_allow_html=True)
            
    with col_chart:
        st.markdown("<div class='card-title'>📈 미래 가치 및 스트레스 테스트</div>", unsafe_allow_html=True)
        st.info("향후 5년 간의 시세 변동 예측 및 리스크를 시뮬레이션합니다.")
        
        # Valuation Modeling
        growth_rate = st.slider("연평균 예상 매매가 상승률 (%)", min_value=-5.0, max_value=15.0, value=3.0, step=0.5)
        
        import pandas as pd
        import numpy as np
        
        base_price = bid_price if bid_price > 0 else 50000
        years = [0, 1, 2, 3, 4, 5]
        
        # 보수적, 중도적, 낙관적 시나리오
        prices_base = [base_price * ((1 + (growth_rate)/100) ** y) for y in years]
        prices_optimistic = [base_price * ((1 + (growth_rate + 3)/100) ** y) for y in years]
        prices_pessimistic = [base_price * ((1 + (growth_rate - 3)/100) ** y) for y in years]
        
        df_future = pd.DataFrame({
            "연도": [f"{2024+y}년" for y in years],
            "예상 시세 (중립)": prices_base,
            "예상 시세 (호재반영)": prices_optimistic,
            "예상 시세 (보수적)": prices_pessimistic
        }).set_index("연도")
        
        st.line_chart(df_future, height=250)
        
        st.markdown("#### 🚨 스트레스 테스트 (금리 인상 리스크)")
        stress_rate = loan_rate + 2.0
        stress_interest = (loan_amt * 10000 * (stress_rate / 100)) / 12
        stress_cashflow = (rent_monthly * 10000) - stress_interest
        
        if stress_cashflow > 0:
            status_html = f"<span style='color:green; font-weight:bold;'>안전 마진 확보 (+{int(stress_cashflow):,}원)</span>"
        else:
            status_html = f"<span style='color:red; font-weight:bold;'>위험 (역마진 발생: {int(stress_cashflow):,}원)</span>"
            
        st.markdown(f"""
        <div style='background:#FEF2F2; border:1px solid #FCA5A5; padding:15px; border-radius:8px; font-size:14px;'>
        만약 금리가 <b>{stress_rate}%</b> (+2.0%p) 로 급등한다면?<br>
        월 이자는 <b>{int(stress_interest):,}원</b>으로 증가하며,<br>
        월 현금흐름 상태는 {status_html} 입니다.
        </div>
        """, unsafe_allow_html=True)
