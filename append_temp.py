    with tab_gap:
        st.markdown("<div class='card-title'>⚡ AI 자동 갭투자 시뮬레이터 (실시간 감시)</div>", unsafe_allow_html=True)
        st.info("이 데이터는 백그라운드 깃허브 로봇(스나이퍼 봇)이 24시간 네이버 호가와 전세가를 수집하여 갭투자 비용을 계산해둔 '실제 데이터'입니다.")
        
        market_file = "market_data.json"
        market_data_list = []
        if os.path.exists(market_file):
            try:
                with open(market_file, "r", encoding="utf-8") as f:
                    market_data_list = json.load(f)
            except:
                pass
                
        if not market_data_list:
            st.warning("아직 수집된 갭투자 데이터가 없습니다. 스나이퍼 봇이 백그라운드에서 동작을 완료하면 데이터가 업데이트됩니다.")
        else:
            st.success(f"총 {len(market_data_list)}건의 실시간 갭투자 분석 데이터가 로드되었습니다!")
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 메트릭 표시
            avg_gap = sum(item["market_info"]["gap"] for item in market_data_list if item.get("market_info") and item["market_info"].get("gap", 0) > 0) / max(1, len([1 for item in market_data_list if item.get("market_info") and item["market_info"].get("gap", 0) > 0]))
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("최근 감시 매물 수", f"{len(market_data_list)} 건")
            col_m2.metric("평균 필요 투자 갭", f"{int(avg_gap):,} 만원")
            col_m3.metric("마지막 업데이트", market_data_list[0]["date"])
            
            st.markdown("---")
            
            # 리스트 렌더링
            for idx, item in enumerate(market_data_list[:10]):
                m_info = item.get("market_info")
                if not m_info or m_info.get("sale_min", 0) == 0:
                    continue
                    
                prop_name = m_info["prop_name"]
                sale_min = m_info["sale_min"]
                jeonse_min = m_info["jeonse_min"]
                gap = m_info["gap"]
                
                st.markdown(f"""
                <div style='background:white; border-radius:12px; padding:20px; box-shadow:0 4px 6px rgba(0,0,0,0.05); margin-bottom:15px; border:1px solid #E5E7EB; border-left:5px solid #3B82F6;'>
                    <h3 style='margin:0; color:#1E3A8A; font-size:20px;'>🏢 {prop_name} <span style='font-size:12px; background:#DBEAFE; color:#1D4ED8; padding:3px 8px; border-radius:20px; font-weight:normal; vertical-align:middle; margin-left:10px;'>{item['date']}</span></h3>
                    <div style='color:#6B7280; font-size:13px; margin-bottom:15px; margin-top:5px;'>출처: {m_info.get('source', '네이버 시세')}</div>
                    
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div style='text-align:center; flex:1;'>
                            <div style='color:#4B5563; font-size:13px; font-weight:bold;'>매매 호가 (최저)</div>
                            <div style='color:#111827; font-size:18px; font-weight:900;'>{sale_min:,}만원</div>
                        </div>
                        <div style='color:#9CA3AF; font-size:20px;'>-</div>
                        <div style='text-align:center; flex:1;'>
                            <div style='color:#4B5563; font-size:13px; font-weight:bold;'>전세 시세 (최저)</div>
                            <div style='color:#059669; font-size:18px; font-weight:900;'>{jeonse_min:,}만원</div>
                        </div>
                        <div style='color:#9CA3AF; font-size:20px;'>=</div>
                        <div style='text-align:center; flex:1; background:#FEF2F2; padding:10px; border-radius:8px;'>
                            <div style='color:#B91C1C; font-size:14px; font-weight:bold;'>필요 갭 투자금 💸</div>
                            <div style='color:#DC2626; font-size:24px; font-weight:900;'>{gap:,}만원</div>
                        </div>
                    </div>
                    <div style='margin-top:15px; text-align:right;'>
                        <a href='{item["href"]}' target='_blank' style='text-decoration:none; background:#F3F4F6; color:#4B5563; padding:6px 12px; border-radius:6px; font-size:13px; font-weight:bold; transition:all 0.2s;'>🔗 원본글 보기</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab_heatmap:
        st.markdown("<div class='card-title'>🔥 전국 전세가율 히트맵 (갭투자 최적지 스캔)</div>", unsafe_allow_html=True)
        st.info("이 데이터는 전국 아파트 실거래가 및 네이버 호가를 취합하여 전세가율이 80% 이상인 '갭투자 위험/기회' 지역을 식별합니다.")
        
        # 임시 목업 데이터 (추후 DB 연동)
        st.markdown("### 📊 권역별 전세가율 히트맵 (샘플 데이터)")
        
        heatmap_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=1a67748f395019b43d48caac98382575"></script>
            <style>
                #map { width: 100%; height: 500px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
                .legend { position: absolute; bottom: 30px; left: 20px; z-index: 10; background: rgba(25, 30, 40, 0.95); padding: 15px; border-radius: 10px; border: 1px solid #334155; box-shadow: 0 4px 10px rgba(0,0,0,0.5); color: #F8FAFC;}
                .legend-title { font-size: 14px; font-weight: 900; margin-bottom: 8px; color: #F1F5F9; }
                .legend-item { display: flex; align-items: center; margin-bottom: 5px; font-weight: bold; font-size: 12px; color: #CBD5E1; }
                .color-box { width: 16px; height: 16px; border-radius: 4px; margin-right: 8px; }
            </style>
        </head>
        <body style="margin:0; padding:0; background: #0F172A;">
            <div style="position: relative;">
                <div id="map"></div>
                <div class="legend">
                    <div class="legend-title">전세가율 히트맵 범례</div>
                    <div class="legend-item"><div class="color-box" style="background: rgba(239, 68, 68, 0.8);"></div> 90% 이상 (극위험/초소액 갭)</div>
                    <div class="legend-item"><div class="color-box" style="background: rgba(245, 158, 11, 0.8);"></div> 80% ~ 90% (경고/소액 갭)</div>
                    <div class="legend-item"><div class="color-box" style="background: rgba(59, 130, 246, 0.8);"></div> 70% 이하 (안전)</div>
                </div>
            </div>
            <script>
                var mapContainer = document.getElementById('map'),
                    mapOption = { center: new kakao.maps.LatLng(37.5665, 126.9780), level: 8 };
                var map = new kakao.maps.Map(mapContainer, mapOption);
                
                // Dark Map Theme (Mockup approach)
                map.addOverlayMapTypeId(kakao.maps.MapTypeId.USE_DISTRICT);
                
                var heatmapData = [
                    {lat: 37.5420, lon: 126.8400, ratio: 92, title: '강서구 가양동'},
                    {lat: 37.5925, lon: 126.9180, ratio: 85, title: '은평구 응암동'},
                    {lat: 37.4851, lon: 126.7828, ratio: 95, title: '부천시 소사동'},
                    {lat: 37.5118, lon: 127.0880, ratio: 55, title: '송파구 잠실동'}
                ];
                
                heatmapData.forEach(function(d) {
                    var color = d.ratio >= 90 ? '#EF4444' : (d.ratio >= 80 ? '#F59E0B' : '#3B82F6');
                    var circle = new kakao.maps.Circle({
                        center: new kakao.maps.LatLng(d.lat, d.lon),
                        radius: d.ratio * 20, // 시각적 과장
                        strokeWeight: 1,
                        strokeColor: color,
                        strokeOpacity: 0.8,
                        strokeStyle: 'solid',
                        fillColor: color,
                        fillOpacity: 0.6
                    });
                    circle.setMap(map);
                    
                    var content = '<div style="padding:5px; background:white; color:black; font-size:12px; border-radius:5px; font-weight:bold;">' + d.title + ' (전세율 ' + d.ratio + '%)</div>';
                    var customOverlay = new kakao.maps.CustomOverlay({
                        position: new kakao.maps.LatLng(d.lat, d.lon),
                        content: content,
                        yAnchor: 1.5
                    });
                    customOverlay.setMap(map);
                });
            </script>
        </body>
        </html>
        """
        components.html(heatmap_html, height=520)
        
        st.markdown("### 🏆 최근 전세가율 급등 지역 Top 3")
        c1, c2, c3 = st.columns(3)
        c1.metric("1. 부천시 소사동", "95.2%", "+2.1%p")
        c2.metric("2. 강서구 가양동", "92.8%", "+1.5%p")
        c3.metric("3. 은평구 응암동", "85.4%", "+0.8%p")            # --------------------------------------------------------
    # 탭 6: 지능형 AI 부동산 비서 (Agentic UI)
