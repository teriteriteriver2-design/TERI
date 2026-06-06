import os

file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'
with open(file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "이 데이터는 백그라운드 깃허브 로봇(스나이퍼 봇)이 24시간 네이버 호가와 전세가를 수집하여 갭투자 비용을 계산해둔 '실제 데이터'입니다." in line:
        new_lines.append("        st.markdown('<br>', unsafe_allow_html=True)\n")
        new_lines.append("        if st.button('🔍 실시간 갭투자 AI 시뮬레이터 수동 가동 (약 1분 소요)', use_container_width=True):\n")
        new_lines.append("            with st.spinner('AI가 최신 부동산 실거래가를 분석하며 갭을 계산 중입니다... (토큰 사용 중)'):\n")
        new_lines.append("                import subprocess\n")
        new_lines.append("                try:\n")
        new_lines.append("                    subprocess.run(['python', 'gap_sniper.py'], check=True)\n")
        new_lines.append("                    st.success('✅ 시뮬레이터 분석이 완료되었습니다! 텔레그램을 확인하시거나 웹페이지를 새로고침(F5) 해주세요!')\n")
        new_lines.append("                except Exception as e:\n")
        new_lines.append("                    st.error(f'오류 발생: {e}')\n")
        new_lines.append("        st.markdown('<br>', unsafe_allow_html=True)\n")

with open(file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
