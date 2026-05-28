# --------------------------------------------------------
with tab_calc:
    if 'selected_prop' in st.session_state and st.session_state['selected_prop']:
        p_case = st.session_state['selected_prop'].get('case_number', 'unknown')
        p_name = st.session_state['selected_prop'].get('prop_name', 'unknown')
        
        try:
            p_min_val = int(st.session_state['selected_prop'].get('price_min', 0) or 0)
        except (ValueError, TypeError):
            p_min_val = 0
        lat = st.session_state['selected_prop'].get('lat', 37.5665)
        lon = st.session_state['selected_prop'].get('lon', 126.9780)
    else:
        p_case = "unknown"
        p_name = "unknown"
        p_min_val = 64000
        lat = 37.5665
        lon = 126.9780
        
    col_sim, col_note = st.columns([1, 1.2])
    
    with col_sim:
        st.markdown("<div class='card-title'>투자 수익 계산기 (상세 세팅)</div>", unsafe_allow_html=True)
        st.info("입찰 보증금과 세부 세팅을 통해 '순수익' 및 '매월 현금흐름'을 계산합니다.")
        
        bid_price = st.number_input("예상 입찰가 (만원)", value=p_min_val, step=1000, key=f"bid_{p_case}")
        loan_amt = st.number_input("대출금 (만원)", value=int(bid_price*0.8), step=1000, key=f"loan_{p_case}")
        loan_rate = st.number_input("금융 대출금리 (%)", value=4.5, step=0.1, key=f"rate_{p_case}")
        
        st.markdown("---")
        rent_deposit = st.number_input("임대 세팅: 받을 보증금(만원)", value=5000, step=500, key=f"dep_{p_case}")
        rent_monthly = st.number_input("임대 세팅: 받을 월세 (만원)", value=120, step=5, key=f"mon_{p_case}")
        
        tax_amt = bid_price * 0.011
        monthly_interest = (loan_amt * 10000 * (loan_rate / 100)) / 12
        net_monthly_cashflow = (rent_monthly * 10000) - monthly_interest
        
        actual_investment = (bid_price - loan_amt - rent_deposit) + tax_amt 
        if actual_investment <= 0:
            yield_str = "무한대 (무피/무비 세팅 완료)"
            yield_monthly_won = net_monthly_cashflow
        else:
            annual_net_profit = net_monthly_cashflow * 12
            yield_pct = (annual_net_profit / (actual_investment * 10000)) * 100
            yield_str = f"{round(yield_pct, 2)}%"
            yield_monthly_won = net_monthly_cashflow / (actual_investment / 1000)
            
        st.markdown(f"""
        <div style='background:#F8FAFC; border:1px solid #CBD5E1; padding:20px; border-radius:12px; font-size:15px;'>
        <b style='color:#475569;'>취득 비용/세금:</b> 1가구 1주택 취득세율(1.1%) 적용 = <b>취득세 {int(tax_amt):,}원</b><br>
        <span style='font-size:13px; color:gray;'>(계산 근거: 입찰가 {format_price(bid_price)} × 1.1%)</span><br><br>
        <b>월 이자상환액:</b> {int(monthly_interest):,}원<span style='font-size:13px; color:gray;'>(대출금 {format_price(loan_amt)} × 이자율 {loan_rate}% ÷ 12개월)</span><br>
        <b>월 매월 순수익이 꽂히는 금액은</b> <span style='color:#2563EB; font-size:22px; font-weight:900;'>{int(net_monthly_cashflow):,}원</span><br>
        <span style='font-size:13px; color:gray;'>(계산 근거: 월세 {int(rent_monthly):,}만원 - 이자 {int(monthly_interest):,}원)</span><br><br>
        <b>연 수익률(ROI):</b> <span style='color:red; font-size:18px; font-weight:800;'>{yield_str}</span> <span style='font-size:13px; color:gray;'>(투자금 1,000만원 당 매월 {int(yield_monthly_won):,}원 수익)</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 감정평가 실 추적
        prop_price_eval = st.session_state['selected_prop'].get('price_eval', 0) if 'selected_prop' in st.session_state and st.session_state['selected_prop'] else 0
        try:
            eval_price_num = int(prop_price_eval) if prop_price_eval not in (None, 'None') else 0
        except:
            eval_price_num = 0
        if eval_price_num > 0:
            peak_price = int(eval_price_num * 1.2) # 감정가의 120%로 2021 최고가 추정
            loss_amt = peak_price - bid_price
            st.markdown(f"<br><div class='card-title' style='font-size:14px; color:#DC2626;'>투자 손실 추정 (최고가 매입 체크)</div>", unsafe_allow_html=True)
            st.info(f"**최고가 예상 매수금액:** 약 {format_price(peak_price)} (2021년 최고기록, 감정가의 120% 추정)\n\n"
                    f"**최고가 매입 손실 예상:** 약 **-{format_price(loss_amt)}** (최고가 매입 후 현재 감정가({format_price(bid_price)})에 팔 경우 예상 손실)\n\n"
                    "이 물건은 기존주의 막연한 기대감에 의해 경매에 나온 '초급매 가격'을 산정하니 유의하세요.")
            
    with col_note:
        st.markdown("<div class='card-title'>주변 인프라 시설 / 프롭테크 초정밀 분석</div>", unsafe_allow_html=True)
        st.info("지역 지도를 통해 카카오 API 기반 반경 500m 내 주요 인프라 시설 브리핑입니다.")
        infra_notes = []
        if sa_engine:
            with st.spinner("커뮤니티 거주자 의견 수집 중.."):
                infra_notes = sa_engine.fetch_infrastructure_notes(p_name, lat, lon)
                
        if infra_notes:
            for note in infra_notes:
                q = note.get("exact_quote", "")
                s = note.get("source", "")
                st.markdown(f"""
                <div style='border-left: 4px solid #10B981; padding-left:15px; margin-bottom:15px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                    <div style='font-style: normal; color: #1F2937; font-size: 14px; font-weight:500;'>{q}</div>
                    <div style='margin-top: 10px;'>
                        <a href='{s}' target='_blank' style='display:inline-block; background:#E5E7EB; color:#374151; padding:4px 10px; border-radius:4px; font-size:11px; font-weight:bold; text-decoration:none;'>가장 가까운 매장 카카오맵 상세 보기</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("관련 인프라 정보를 찾지 못했습니다.")
        
        st.markdown("<div class='card-title' style='margin-top: 20px;'>커뮤니티 의견 발췌 (AI 분석/설명 자료 활용)</div>", unsafe_allow_html=True)
        st.info("돈벌자 봇이 맘카페, 부동산 커뮤니티, 블로그에서 해당 지역의 실제 거주 경험 문구를 발췌했습니다.")
        
        reviews = []
        if 'selected_prop' in st.session_state and st.session_state['selected_prop'] is not None and sa_engine:
            with st.spinner("커뮤니티 거주기록 수집 중.."):
                reviews = sa_engine.fetch_community_reviews(st.session_state['selected_prop']['prop_name'])
                
        if reviews:
            for r in reviews:
                quote = r.get("exact_quote", "")
                src = r.get("source", "")
                st.markdown(f"""
                <div style='border-left: 4px solid #3B82F6; padding-left:15px; margin-bottom:15px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                    <div style='font-style: italic; color: #1F2937; font-size: 15px; font-weight:500;'>"{quote}"</div>
                    <div style='margin-top: 10px;'>
                        <a href='{src}' target='_blank' style='display:inline-block; background:#E5E7EB; color:#374151; padding:4px 10px; border-radius:4px; font-size:11px; font-weight:bold; text-decoration:none;'>원본 글 직접 확인하기 (체크)</a>
                    </div>
