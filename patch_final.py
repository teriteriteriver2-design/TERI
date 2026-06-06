import os

# 1. Update speedauction_engine.py
sa_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/speedauction_engine.py'
with open(sa_file, 'r', encoding='utf-8') as f:
    sa_content = f.read()

sa_content = sa_content.replace('전세가율 80% OR 전세가율 급등 OR 갭투자', '전세가율 갭투자')

with open(sa_file, 'w', encoding='utf-8') as f:
    f.write(sa_content)


# 2. Update app_v2.py
app_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'
with open(app_file, 'r', encoding='utf-8') as f:
    app = f.read()

app = app.replace(
    'tab_cal, tab_news = st.tabs(["📅 AI 부동산 캘린더", "📰 최신 정책 뉴스"])',
    'tab_cal, tab_news = st.tabs(["📅 🤖 AI 부동산 캘린더", "📰 🤖 최신 정책 뉴스"])'
)

app = app.replace(
    'tab_search, tab_redev, tab_gap, tab_heatmap = st.tabs(["🗺️ 토지이용 & 매물 스캔", "🏙️ 재개발 전망 추천", "⚡ AI 갭투자 스나이퍼", "🔥 전국 전세가율 히트맵"])',
    'tab_search, tab_redev, tab_gap, tab_heatmap = st.tabs(["🗺️ 🤖 토지이용 & 매물 스캔", "🏙️ 🤖 재개발 전망 추천", "⚡ 🤖 AI 갭투자 스나이퍼", "🔥 🤖 전국 전세가율 히트맵"])'
)

app = app.replace(
    'tab_map, tab_calc = st.tabs(["🤖 AI 기반 권리분석", "📈 시장 트렌드 & 수익 분석"])',
    'tab_map, tab_calc = st.tabs(["🤖 AI 기반 권리분석", "📈 🤖 시장 트렌드 & 수익 분석"])'
)

app = app.replace(
    'tab_agent, = st.tabs(["💬 AI 맞춤형 비서"])',
    'tab_agent, = st.tabs(["💬 🤖 AI 맞춤형 비서"])'
)

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(app)

print("Patch applied for query and emojis")
