import os

file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """        st.info("이 데이터는 백그라운드 깃허브 로봇(스나이퍼 봇)이 24시간 네이버 호가와 전세가를 수집하여 갭투자 비용을 계산해둔 '실제 데이터'입니다.")

        market_file = "market_data.json\"""".replace('"', "")
# Wait, I won't use replace on strings. I'll use exact match.
old_code2 = "        st.info(\"이 데이터는 백그라운드 깃허브 로봇(스나이퍼 봇)이 24시간 네이버 호가와 전세가를 수집하여 갭투자 비용을 계산해둔 '실제 데이터'입니다.\")\n\n        market_file = \"market_data.json\""

new_code = """        st.info("이 데이터는 백그라운드 깃허브 로봇(스나이퍼 봇)이 24시간 네이버 호가와 전세가를 수집하여 갭투자 비용을 계산해둔 '실제 데이터'입니다.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 실시간 갭투자 AI 시뮬레이터 수동 가동 (약 1분 소요)", use_container_width=True):
            with st.spinner("AI가 최신 부동산 실거래가를 분석하며 갭을 계산 중입니다... (토큰 사용 중)"):
                import subprocess
                try:
                    subprocess.run(["python", "gap_sniper.py"], check=True)
                    st.success("✅ 시뮬레이터 분석이 완료되었습니다! 텔레그램을 확인하시거나 웹페이지를 새로고침(F5) 해주세요!")
                except Exception as e:
                    st.error(f"오류 발생: {e}")
        st.markdown("<br>", unsafe_allow_html=True)

        market_file = "market_data.json\"""".replace('\"', '"')

content = content.replace(old_code2, new_code)

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)
