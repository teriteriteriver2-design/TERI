import codecs

lines = codecs.open('app_v2.py', encoding='utf-8').read().splitlines()

# 1. Replace old tabs definition
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
    'elif menu == "🔍 매물 딥스캔":',
    '    tab_search, tab_redev = st.tabs(["🗺️ 토지이용 & 매물 스캔", "🏙️ 재개발 전망 추천"])',
    'elif menu == "⚖️ 권리분석 & 수익":',
    '    tab_map, tab_calc = st.tabs(["🤖 AI 기반 권리분석", "📈 시장 트렌드 & 수익 분석"])',
    'elif menu == "💬 AI 맞춤형 비서":',
    '    tab_agent, = st.tabs(["💬 AI 맞춤형 비서"])',
    ''
]

lines = lines[:start_idx] + sidebar_code + lines[end_idx+1:]

def find_line(startswith):
    for i, l in enumerate(lines):
        if l.startswith(startswith):
            return i
    return -1

# Find boundaries of each block
blocks = {
    'news': find_line('with tab_news:'),
    'search': find_line('with tab_search:'),
    'map': find_line('with tab_map:'),
    'calc': find_line('with tab_calc:'),
    'redev': find_line('with tab_redev:'),
    'agent': find_line('with tab_agent:')
}
# Order of appearance: news, search, map, calc, redev, agent
bounds = [
    ('news', blocks['news'], blocks['search']),
    ('search', blocks['search'], blocks['map']),
    ('map', blocks['map'], blocks['calc']),
    ('calc', blocks['calc'], blocks['redev']),
    ('redev', blocks['redev'], blocks['agent']),
    ('agent', blocks['agent'], len(lines))
]

menus = {
    'news': 'if menu == "📊 데일리 마켓":',
    'search': 'if menu == "🔍 매물 딥스캔":',
    'map': 'if menu == "⚖️ 권리분석 & 수익":',
    'calc': 'if menu == "⚖️ 권리분석 & 수익":',
    'redev': 'if menu == "🔍 매물 딥스캔":',
    'agent': 'if menu == "💬 AI 맞춤형 비서":'
}

new_lines = lines[:blocks['news']]

# Add the calendar code before news
new_lines.extend([
    'if menu == "📊 데일리 마켓":',
    '    with tab_cal:',
    '        st.markdown("### 📅 부동산 AI 일정 캘린더 (스케줄)")',
    '        st.info("여기에 법원 매각기일, 한국은행 금리 발표일 등 주요 일정이 추가될 예정입니다.")',
    '        if st.button("🤖 AI 분석 리포트 생성 (뉴스 & 호재 요약)"):',
    '            st.success("AI가 최신 동향을 요약했습니다! (추후 실제 데이터 연동)")',
    ''
])

for name, start, end in bounds:
    new_lines.append(menus[name])
    for i in range(start, end):
        if lines[i].strip() != '':
            new_lines.append('    ' + lines[i])
        else:
            new_lines.append('')

codecs.open('app_v2.py', 'w', encoding='utf-8').write('\n'.join(new_lines))
codecs.open('app.py', 'w', encoding='utf-8').write('\n'.join(new_lines))
codecs.open('app_restored.py', 'w', encoding='utf-8').write('\n'.join(new_lines))
print('Refactoring complete successfully.')
