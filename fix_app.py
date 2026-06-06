import codecs

with codecs.open('C:\\Users\\뀽제\\OneDrive\\바탕 화면\\BU\\app.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

good_lines = lines[:1073]

appended_code = """            with st.spinner("사용자님의 의도를 분석 중입니다..."):
                if sa_engine:
                    parsed_intent = sa_engine.process_chat_intent(prompt, st.session_state["chat_history"])
                    intent = parsed_intent.get("intent", "general_chat")
                    keyword = parsed_intent.get("keyword", "")
                    reply = parsed_intent.get("reply", "네, 잠시만 기다려주세요.")
                    
                    st.markdown(reply)
                    st.session_state["chat_history"].append({"role": "assistant", "content": reply})

                    # Execute Agentic Action
                    if intent == "search_auction" and keyword:
                        st.info(f"🔍 '{keyword}' 기반으로 대법원 경매 및 네이버 실시간 매물을 딥스캔합니다...")
                        results = sa_engine.fetch_live_auctions(keyword=keyword, limit=3)
                        if results:
                            for idx, auc in enumerate(results):
                                st.markdown(f"**{idx+1}. {auc['prop_name']} ({auc['case_number']})**")
                                try:
                                    p_eval = int(float(str(auc.get('price_eval', '0')).replace(',', '').replace('None', '0')))
                                except:
                                    p_eval = 0
                                try:
                                    p_min = int(float(str(auc.get('price_min', '0')).replace(',', '').replace('None', '0')))
                                except:
                                    p_min = 0
                                st.markdown(f"- ⚖️ 법원 감정가: {format_price(p_eval)}")
                                st.markdown(f"- 📉 현재 최저가: {format_price(p_min)} ({auc['status']})")
                            st.session_state["chat_history"].append({"role": "assistant", "content": f"총 {len(results)}건의 추천 매물을 스캔 완료했습니다. 위 결과를 확인해주세요!"})
                        else:
                            st.warning("해당 지역에 진행 중인 적합한 경매 매물이 없습니다.")
                            st.session_state["chat_history"].append({"role": "assistant", "content": "스캔 결과 해당 지역에 매물이 발견되지 않았습니다."})
                            
                    elif intent == "search_redev" and keyword:
                        st.info(f"🔍 '{keyword}' 기반 재개발/재건축 구역 분석을 시작합니다...")
                        r_info = sa_engine.fetch_redevelopment_info(keyword)
                        if r_info:
                            st.success(f"📍 {r_info.get('process_status')} 단계 진행 중")
                            st.markdown(f"- **핵심 추천 이유:** {r_info.get('recommendation_reason')}")
                            st.session_state["chat_history"].append({"role": "assistant", "content": f"스캔 결과: {r_info.get('process_status')} 단계로 분석됩니다."})
                        else:
                            st.warning("해당 지역의 유효한 재개발 정보를 찾을 수 없습니다.")
                else:
                    st.error("AI 엔진을 불러올 수 없습니다.")
"""

with codecs.open('C:\\Users\\뀽제\\OneDrive\\바탕 화면\\BU\\app.py', 'w', encoding='utf-8') as f:
    f.writelines(good_lines)
    f.write(appended_code)
