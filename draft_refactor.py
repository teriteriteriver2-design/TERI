import codecs

lines = codecs.open('app_v2.py', encoding='utf-8').read().splitlines()

# 1. Find the old tabs definition (around 369-376)
start_idx = -1
end_idx = -1
for i, l in enumerate(lines):
    if 'tab_news, tab_search, tab_map, tab_calc, tab_redev, tab_agent = st.tabs([' in l:
        start_idx = i
    if start_idx != -1 and '])' in l and i > start_idx:
        end_idx = i
        break

sidebar_code = [
    'st.sidebar.markdown("---")',
    'st.sidebar.markdown("## 🧭 메인 메뉴")',
    'menu = st.sidebar.radio(',
    '    "원하시는 기능을 선택하세요:",',
    '    ("📊 데일리 마켓", "🔍 매물 딥스캔", "⚖️ 권리분석 & 수익", "💬 AI 맞춤형 비서")',
    ')',
    '',
    'if menu == "📊 데일리 마켓":',
    '    tab_cal, tab_news = st.tabs(["📅 AI 부동산 캘린더", "📰 최신 정책 뉴스"])',
    '    with tab_cal:',
    '        st.markdown("### 📅 부동산 AI 일정 캘린더 (스케줄)")',
    '        st.info("여기에 법원 매각기일, 한국은행 금리 발표일 등 주요 일정이 추가될 예정입니다.")',
    '        if st.button("🤖 AI 분석 리포트 생성 (뉴스 & 호재 요약)"):',
    '            st.success("AI가 최신 동향을 요약했습니다! (추후 실제 데이터 연동)")'
]

lines = lines[:start_idx] + sidebar_code + lines[end_idx+1:]

def find_line(startswith):
    for i, l in enumerate(lines):
        if l.startswith(startswith):
            return i
    return -1

idx_news = find_line('with tab_news:')

# We need to indent everything from idx_news to the end of the file by 4 spaces!
for i in range(idx_news, len(lines)):
    if not lines[i].startswith('elif menu =='):
        if lines[i].strip() != '':
            lines[i] = '    ' + lines[i]

def find_indented_line(text):
    for i, l in enumerate(lines):
        if l == '    ' + text:
            return i
    return -1

# Insert new menu headers at the correct locations
idx_search = find_indented_line('with tab_search:')
lines.insert(idx_search, 'elif menu == "🔍 매물 딥스캔":')
lines.insert(idx_search + 1, '    tab_search, tab_redev = st.tabs(["🗺️ 토지이용 & 매물 스캔", "🏙️ 재개발 전망 추천"])')

idx_map = find_indented_line('with tab_map:')
lines.insert(idx_map, 'elif menu == "⚖️ 권리분석 & 수익":')
lines.insert(idx_map + 1, '    tab_map, tab_calc = st.tabs(["🤖 AI 기반 권리분석", "📈 시장 트렌드 & 수익 분석"])')

# Also tab_calc needs to stay under the same elif as tab_map, so no need to add elif menu there. 
# It will just be tab_map, tab_calc = st.tabs... which is already handled above!

idx_redev = find_indented_line('with tab_redev:')
# Wait, redev belongs to "🔍 매물 딥스캔" but it's physically located AFTER tab_calc in the file!!!
# This is a major issue! In Streamlit, everything is procedural top-to-bottom.
# If `menu == "🔍 매물 딥스캔"`, the `elif` blocks run.
# But `with tab_redev:` is physically at line 1107, which is AFTER `with tab_map:` (line 672)!
# So if `menu == "🔍 매물 딥스캔"`, it hits the first `elif`, executes `with tab_search:`, and then SKIPS the second `elif menu == "⚖️ 권리분석 & 수익":` entirely, WHICH MEANS IT WILL SKIP `with tab_redev:` if we just indent it without another `if` block!!!
