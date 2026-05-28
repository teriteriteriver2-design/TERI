# 탭 6: 지능형 AI 부동산 비서 (Agentic UI)
# --------------------------------------------------------
with tab_agent:
    st.markdown("<div class='premium-title' style='font-size:24px; margin-bottom:10px;'>🤖 AI 프롭테크 개인 비서 (V3.0 Beta)</div>", unsafe_allow_html=True)
    st.caption("자연어로 매물 검색 및 권리분석 요청, 또는 재개발 현황에 대한 질문을 보낼 수 있습니다.")
    
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [{"role": "assistant", "content": "안녕하세요! 자산과 관련된 지식이 궁금하시거나 경매 매물에 대해 말씀해주시면 직접 스캔하고 분석해드리겠습니다. (예: '서울 강남구 경매 아파트 찾아줘')!"}]

    # Display chat messages
    for i, msg in enumerate(st.session_state["chat_history"]):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)
            if "results" in msg and msg["results"]:
                for j, auc in enumerate(msg["results"]):
                    with st.expander(f"🔹 {auc.get('prop_name', '알수없음')} ({auc.get('case_number', 'unknown')})"):
                        try:
                            p_eval = int(float(str(auc.get('price_eval', '0')).replace(',', '').replace('None', '0')))
                        except:
                            p_eval = 0
                        try:
                            p_min = int(float(str(auc.get('price_min', '0')).replace(',', '').replace('None', '0')))
                        except:
                            p_min = 0
                        
                        st.markdown(f"- ⚖️ 법원 감정가: {format_price(p_eval)}")
                        st.markdown(f"- 📉 현재 최저가: {format_price(p_min)} ({auc.get('status', '진행')})")
                        if st.button(f"✅ {auc.get('prop_name', '매물')} 정밀 분석 시작", key=f"btn_analyze_{i}_{j}_{auc.get('case_number', 'x')}"):
                            st.session_state['selected_prop'] = {
                                "prop_name": auc.get('prop_name', '알수없음'),
                                "case_number": auc.get('case_number', 'unknown'),
                                "price_eval": p_eval,
                                "price_min": p_min,
                                "lat": auc.get('lat', 37.5665),
                                "lon": auc.get('lon', 126.9780)
                            }
                            st.success("매물 분석 데이터가 연동되었습니다. 화면 상단의 **[3. 지도 & 권리분석]** 또는 **[4. 투자 분석 & 계산기]** 탭으로 이동하세요!")

    # Chat Input
    if prompt := st.chat_input("하실 매물이나 궁금한 점을 자연어로 입력하세요"):
        # Add user message to state
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        st.rerun()

    # 프로세싱이 필요한 새로운 메시지가 있는지 확인 (마지막 메시지가 유저일 때)
    if st.session_state["chat_history"] and st.session_state["chat_history"][-1]["role"] == "user":
        prompt = st.session_state["chat_history"][-1]["content"]
        with st.chat_message("assistant"):
            with st.spinner("사용자님의 의도를 분석 중입니다..."):
                if sa_engine:
                    parsed_intent = sa_engine.process_chat_intent(prompt, st.session_state["chat_history"])
                    intent = parsed_intent.get("intent", "general_chat")
                    keyword = parsed_intent.get("keyword", "")
                    reply = parsed_intent.get("reply", "네, 잠시만 기다려주세요.")
                    
                    st.markdown(reply)
                    
                    new_msg = {"role": "assistant", "content": reply}

                    # Execute Agentic Action
                    if intent == "search_auction" and keyword:
                        st.info(f"🔍 '{keyword}' 기반으로 대법원 경매 및 네이버 실시간 매물을 딥스캔합니다...")
                        results = sa_engine.fetch_live_auctions(keyword=keyword, limit=3)
                        if results:
                            new_msg["content"] += f"\n\n총 {len(results)}건의 추천 매물을 스캔 완료했습니다. 아래 매물을 확인하고 분석 버튼을 눌러보세요!"
                            new_msg["results"] = results
                            
                            # 바로 렌더링
                            for j, auc in enumerate(results):
                                with st.expander(f"🔹 {auc.get('prop_name', '알수없음')} ({auc.get('case_number', 'unknown')})"):
                                    st.markdown(f"- ⚖️ 법원 감정가: {format_price(auc.get('price_eval', 0))}")
                                    st.markdown(f"- 📉 현재 최저가: {format_price(auc.get('price_min', 0))} ({auc.get('status', '진행')})")
                                    # 버튼은 다음 rerun에서 생성됨
                        else:
                            st.warning("해당 지역에 진행 중인 적합한 경매 매물이 없습니다.")
                            new_msg["content"] += "\n\n스캔 결과 해당 지역에 매물이 발견되지 않았습니다."
                            
                    elif intent == "search_redev" and keyword:
                        st.info(f"🔍 '{keyword}' 기반 재개발/재건축 구역 분석을 시작합니다...")
                        r_info = sa_engine.fetch_redevelopment_info(keyword)
                        if r_info:
                            st.success(f"📍 {r_info.get('process_status')} 단계 진행 중")
                            st.markdown(f"- **핵심 추천 이유:** {r_info.get('recommendation_reason')}")
                            new_msg["content"] += f"\n\n스캔 결과: **{r_info.get('process_status')}** 단계로 분석됩니다.\n핵심 이유: {r_info.get('recommendation_reason')}"
                        else:
                            st.warning("해당 지역의 유효한 재개발 정보를 찾을 수 없습니다.")
                            new_msg["content"] += "\n\n해당 지역의 유효한 재개발 정보를 찾을 수 없습니다."
                            
                    st.session_state["chat_history"].append(new_msg)
                    st.rerun()
                else:
                    st.error("AI 엔진을 불러올 수 없습니다.")
