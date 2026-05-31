import os
import re

app_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'

with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the Gauge
gauge_old = 'st.markdown(gauge_html, unsafe_allow_html=True)'
gauge_new = 'import streamlit.components.v1 as components\ncomponents.html("<body style=\\"margin:0; padding:10px; font-family:sans-serif;\\">" + gauge_html + "</body>", height=280)'
content = content.replace(gauge_old, gauge_new)

# 2. Fix the Heatmap
heatmap_old_start = '        # 임시 목업 데이터 (추후 DB 연동)'
heatmap_old_end = 'c3.metric("3. 은평구 응암동", "85.4%", "+0.8%p")'

# We find the block to replace
start_idx = content.find(heatmap_old_start)
end_idx = content.find(heatmap_old_end) + len(heatmap_old_end)

if start_idx != -1 and end_idx != -1:
    heatmap_new = """
        # 실제 데이터 연동 (OpenAI 기반 실시간 시장 분석)
        st.markdown("### 📊 권역별 전세가율 히트맵 (실시간 AI 분석 데이터)")
        
        # 실시간 데이터 가져오기 (spinner 적용)
        heatmap_data_list = []
        import speedauction_engine
        if 'heatmap_real_data' not in st.session_state:
            with st.spinner("🤖 GPT-4o가 실시간 부동산 시장 데이터를 분석하여 전세가율 80% 이상 지역을 스캔 중입니다... (약 10초 소요)"):
                sa = speedauction_engine.SpeedAuctionEngine()
                st.session_state['heatmap_real_data'] = sa.fetch_jeonse_heatmap_data()
        
        heatmap_data_list = st.session_state['heatmap_real_data']
        
        import json
        heatmap_json_str = json.dumps(heatmap_data_list, ensure_ascii=False)
        
        heatmap_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=1a67748f395019b43d48caac98382575"></script>
            <style>
                #map {{ width: 100%; height: 500px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }}
                .legend {{ position: absolute; bottom: 30px; left: 20px; z-index: 10; background: rgba(25, 30, 40, 0.95); padding: 15px; border-radius: 10px; border: 1px solid #334155; box-shadow: 0 4px 10px rgba(0,0,0,0.5); color: #F8FAFC;}}
                .legend-title {{ font-size: 14px; font-weight: 900; margin-bottom: 8px; color: #F1F5F9; }}
                .legend-item {{ display: flex; align-items: center; margin-bottom: 5px; font-weight: bold; font-size: 12px; color: #CBD5E1; }}
                .color-box {{ width: 16px; height: 16px; border-radius: 4px; margin-right: 8px; }}
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
                var mapContainer = document.getElementById('map');
                var heatmapData = {heatmap_json_str};
                
                // 첫번째 지역 기준으로 지도 중심 설정
                var centerLat = heatmapData.length > 0 ? heatmapData[0].lat : 37.5665;
                var centerLon = heatmapData.length > 0 ? heatmapData[0].lon : 126.9780;
                
                var mapOption = {{ center: new kakao.maps.LatLng(centerLat, centerLon), level: 9 }};
                var map = new kakao.maps.Map(mapContainer, mapOption);
                
                // Dark Map Theme (Mockup approach)
                map.addOverlayMapTypeId(kakao.maps.MapTypeId.USE_DISTRICT);
                
                heatmapData.forEach(function(d) {{
                    var color = d.ratio >= 90 ? '#EF4444' : (d.ratio >= 80 ? '#F59E0B' : '#3B82F6');
                    var circle = new kakao.maps.Circle({{
                        center: new kakao.maps.LatLng(d.lat, d.lon),
                        radius: d.ratio * 30, // 시각적 과장
                        strokeWeight: 1,
                        strokeColor: color,
                        strokeOpacity: 0.8,
                        strokeStyle: 'solid',
                        fillColor: color,
                        fillOpacity: 0.6
                    }});
                    circle.setMap(map);
                    
                    var content = '<div style="padding:8px; background:white; color:black; font-size:12px; border-radius:8px; font-weight:bold; box-shadow:0 2px 5px rgba(0,0,0,0.2);">' + d.title + ' (전세율 <span style="color:'+color+';">' + d.ratio + '%</span>)</div>';
                    var customOverlay = new kakao.maps.CustomOverlay({{
                        position: new kakao.maps.LatLng(d.lat, d.lon),
                        content: content,
                        yAnchor: 1.5
                    }});
                    customOverlay.setMap(map);
                }});
            </script>
        </body>
        </html>
        '''
        
        import streamlit.components.v1 as components
        components.html(heatmap_html, height=520)
        
        st.markdown("### 🏆 AI 팩트체크: 현재 전세가율 급등 위험/기회 지역")
        if len(heatmap_data_list) > 0:
            for i, data in enumerate(heatmap_data_list):
                st.markdown(f'''
                <div style="background:#F8FAFC; border-left:4px solid #EF4444; padding:15px; border-radius:8px; margin-bottom:10px;">
                    <div style="font-size:16px; font-weight:900; color:#111827; margin-bottom:5px;">{i+1}. {data.get("title")} <span style="color:#DC2626; font-size:14px;">(전세가율 {data.get("ratio")}%)</span></div>
                    <div style="font-size:13px; color:#4B5563;"><b>💡 분석 근거:</b> {data.get("reason")}</div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.warning("현재 스캔된 고전세가율 지역이 없습니다.")
"""
    content = content[:start_idx] + heatmap_new + content[end_idx:]

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied to app_v2.py!")
