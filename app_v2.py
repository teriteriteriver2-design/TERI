import billing_db
import streamlit as st
import concurrent.futures
import pandas as pd
import sqlite3
import os
import urllib.request
import json
import urllib.parse
import re
import random
import datetime
from dotenv import load_dotenv
import streamlit.components.v1 as components
import report_generator

def format_korean_money(amount_manwon):
    if amount_manwon == 0:
        return "0만원"
    is_negative = amount_manwon < 0
    abs_amt = abs(amount_manwon)
    uk = abs_amt // 10000
    man = abs_amt % 10000
    
    parts = []
    if uk > 0:
        parts.append(f"{uk:,}억")
    if man > 0:
        parts.append(f"{man:,}만")
    
    result = " ".join(parts) + "원"
    if is_negative:
        result = "-" + result
    return result


# ========================================================
# 1. 초기 설정 (초프리미엄 프롭테크 가이드 테마 & V21 DB 캐시)
# ========================================================
load_dotenv()
st.set_page_config(page_title="돈벌자 - Real Estate AI V21", layout="wide", initial_sidebar_state="expanded")

# --- DB & Log Setup ---
DB_FILE = "donbulja_realestate.db"
LOG_FILE = "agent_activity.log"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS saved_props
                 (case_number TEXT PRIMARY KEY, prop_name TEXT, min_price TEXT, eval_price TEXT, save_date TEXT)''')
    conn.commit()
    conn.close()

def log_agent(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] 에이전트: {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)

init_db()

# ========================================================
# 1.5. 완벽한 커스텀 사이드바 토글 (플로팅 햄버거 메뉴)
# ========================================================
import streamlit.components.v1 as components
components.html("""
<script>
  const parentDoc = window.parent.document;
  
  // [핵심] 이 스크립트가 실행되는 iframe 자체의 부모 박스(빈 동그라미 잔상)를 찾아내서 강제 삭제!
  if (window.frameElement) {
      let wrapper = window.frameElement.closest('div[data-testid="stVerticalBlock"] > div');
      if (wrapper) {
          wrapper.style.display = 'none';
      }
  }
  
  // 만약 이미 버튼이 생성되었다면 중복 생성 방지
  if (!parentDoc.getElementById("custom-galaxy-menu-btn")) {
      const btn = parentDoc.createElement("div");
      btn.id = "custom-galaxy-menu-btn";
      
      // 최고급 유리알 햄버거 아이콘 (SVG)
      btn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>`;
      
      // 화면 왼쪽 위 절대 위치 고정 (모바일/PC 완벽 호환 CSS)
      btn.style.cssText = `
          position: fixed; 
          top: 15px; 
          left: 15px; 
          z-index: 9999999; 
          width: 50px; 
          height: 50px; 
          background: rgba(255, 255, 255, 0.1); 
          backdrop-filter: blur(12px); 
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.2); 
          border-radius: 50%; 
          display: flex; 
          justify-content: center; 
          align-items: center; 
          cursor: pointer; 
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4); 
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      `;
      
      // 호버 액션
      btn.onmouseenter = () => {
          btn.style.background = "rgba(255, 255, 255, 0.25)";
          btn.style.transform = "scale(1.1)";
          btn.style.boxShadow = "0 6px 25px rgba(0, 0, 0, 0.5)";
      };
      btn.onmouseleave = () => {
          btn.style.background = "rgba(255, 255, 255, 0.1)";
          btn.style.transform = "scale(1)";
          btn.style.boxShadow = "0 4px 20px rgba(0, 0, 0, 0.4)";
      };
      
      // 클릭 시 투명 인간 해킹 기법 (네이티브 버튼 대리 클릭)
      btn.onclick = function() {
          // 1. 축소된 상태일 때 여는 버튼 찾기 (Deploy 버튼 오작동 방지)
          let openBtn = parentDoc.querySelector('[data-testid="collapsedControl"]') || 
                        parentDoc.querySelector('[data-testid="stSidebarCollapsedControl"]');
          
          if (openBtn) {
              openBtn.click();
          } else {
              // 2. 확장된 상태일 때 닫는 버튼 찾기 (사이드바 내부의 X 버튼)
              let closeBtn = parentDoc.querySelector('[data-testid="stSidebar"] button');
              if (closeBtn) closeBtn.click();
          }
      };
      
      // 앱의 최상위 body에 버튼을 강력하게 접착!
      parentDoc.body.appendChild(btn);
  }
</script>
""", height=0, width=0)

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* Apply Pretendard ONLY to text elements to 100% guarantee we never break Streamlit's native buttons/icons */
    p, h1, h2, h3, h4, li, label, .stMarkdown, .stText, .stAlert, .stSelectbox, .stRadio, .stButton > button { font-family: 'Pretendard', sans-serif !important; }
    
    .stApp { 
        background: #f8fafc !important; 
    }
    
    /* Force Streamlit inner containers to be transparent so the gradient shines through */
    div[data-testid="stAppViewContainer"] { background: transparent !important; }
    .block-container { max-width: 1500px; padding-top: 3rem; padding-bottom: 3rem; }
    
    /* 남색 박스 완전 제거 */
    header[data-testid="stHeader"], .stAppHeader { 
        display: none !important;
    }
    
    /* 네이티브 화살표의 텅 빈 동그라미 잔상(포커스 링) 영구 삭제 */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] { 
        opacity: 0 !important;
        pointer-events: none !important;
        position: absolute !important;
        left: -9999px !important;
    }
    
    /* 쓸데없는 툴바(우측 메뉴)만 숨김 */
    [data-testid="stToolbar"] { 
        display: none !important; 
    }
    
    /* CSS 블록 등 보이지 않는 요소가 빈 박스(Frosted Glass)로 나타나는 현상 제거 */
    div[data-testid="stVerticalBlock"] > div:has(style),
    div[data-testid="stVerticalBlock"] > div:has(iframe[height="0"]) {
        display: none !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    /* BENTO GRID: White cards with subtle shadows */
    [data-testid="stMetric"], [data-testid="stTabs"], [data-testid="stExpander"], .stPlotlyChart {
        background: #ffffff;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        padding: 24px;
        border: 1px solid rgba(0, 0, 0, 0.03);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    [data-testid="stMetric"]:hover, [data-testid="stTabs"]:hover, [data-testid="stExpander"]:hover, .stPlotlyChart:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
    }
    
    /* Remove padding from Tabs so headers look clean inside the card */
    [data-testid="stTabs"] [data-testid="stVerticalBlock"] { gap: 1rem; }
    
    button[data-baseweb="tab"] { background-color: transparent !important; color: #64748b !important; }
    div[data-baseweb="tab-list"] { gap: 15px; margin-bottom: 20px; }
    div[data-baseweb="tab-highlight"] { background-color: #6366f1 !important; height: 3px; border-radius: 5px; }
    
    .stButton > button {
        border-radius: 50px !important;
        background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
        color: #ffffff !important; font-weight: 800 !important; font-size: 16px !important;
        border: none !important; 
        padding: 10px 24px !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover { 
        transform: scale(1.03) translateY(-2px); 
        background: linear-gradient(135deg, #4f46e5, #4338ca) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5) !important;
    }
    
    .premium-title { font-size: 38px; font-weight: 900; color: #1e293b; margin-bottom: 5px; letter-spacing: -1px; }
    .premium-subtitle { font-size: 15px; color: #64748b; font-weight: 500; margin-bottom: 30px; letter-spacing: -0.5px; }
    .card-title { font-size: 18px; font-weight: 800; color: #334155; margin-bottom: 8px; letter-spacing: -0.5px; }
    .profit-highlight { font-size: 26px; font-weight: 900; color: #6366f1; letter-spacing: -1px; }
    .status-badge { background: rgba(220, 38, 38, 0.1); color: #ef4444; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 800; border: 1px solid rgba(220, 38, 38, 0.2); }
    .status-green { background: rgba(5, 150, 105, 0.1); color: #059669; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 800; border: 1px solid rgba(5, 150, 105, 0.2); }
    .status-yellow { background: rgba(217, 119, 6, 0.1); color: #d97706; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 800; border: 1px solid rgba(217, 119, 6, 0.2); }
    .tag-blue { background: rgba(99, 102, 241, 0.1); color: #4f46e5; padding: 4px 10px; border-radius: 8px; font-size: 13px; font-weight: bold; border: 1px solid rgba(99, 102, 241, 0.2); }
    .registry-box { font-family: monospace; font-size: 13px; background: #f1f5f9; border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; white-space: pre-wrap; color: #334155; }
    .alert-box { background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 10px; border-radius: 8px; font-weight: 700; color: #dc2626; margin-bottom: 10px; }


    
    
    /* --- Ultimate File Uploader Fix --- */
    /* Hide EVERY text and icon element inside the dropzone natively, leaving ONLY the invisible file input untouched */
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] span,
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] small,
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] p,
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] svg,
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] i,
    [data-testid*="FileUploader"] [data-testid*="Dropzone"] div {
        display: none !important;
    }
    
    /* Rebuild with bulletproof Emoji icon and Text */
    [data-testid*="FileUploader"] [data-testid*="Dropzone"]::before {
        content: "📁";
        font-size: 45px !important;
        display: block !important;
        text-align: center !important;
        margin-bottom: 10px !important;
    }
    [data-testid*="FileUploader"] [data-testid*="Dropzone"]::after {
        content: "여기를 클릭하거나 이미지를 드래그하여 업로드하세요\A최대 200MB 지원";
        white-space: pre-wrap !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #475569 !important;
        text-align: center !important;
        display: block !important;
        line-height: 1.5 !important;
    }

    
    /* --- Ultimate Expander Icon Replacement --- */
    /* Target EVERYTHING that could possibly render the arrow_down text */
    summary[data-testid*="Expander"] svg,
    summary[data-testid*="Expander"] i,
    summary[data-testid*="Expander"] span[translate="no"],
    summary[data-testid*="Expander"] span[class*="material"],
    summary[data-testid*="Expander"] span[class*="icon"],
    summary[data-testid*="Expander"] span[class*="Icon"] {
        display: none !important;
        opacity: 0 !important;
        font-size: 0 !important;
    }
    
    /* Inject bulletproof emoji chevron */
    summary[data-testid*="Expander"] > div::after {
        content: "🔽";
        float: right;
        font-size: 16px !important;
        color: #38BDF8 !important;
        margin-left: 10px;
        line-height: inherit;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# 유틸리티 함수: 금액 포맷팅 (80000 -> 8억 원) 변환 설정
# --------------------------------------------------------
def format_price(p):
    try:
        # 문자열에서 모든 숫자 외 문자 제거 후 변환
        p_str = str(p)
        clean_p = re.sub(r'[^0-9]', '', p_str)
        if not clean_p:
            return "가격정보 없음"
        p_val = int(clean_p)

        # 만약 값이 '억' 위에 있다면 만원으로 계산
        if p_val > 100000000: # 1억 이상 단위일 경우
            p_val = p_val // 10000

        if p_val >= 10000:
            uk = p_val // 10000
            man = p_val % 10000
            if man == 0:
                return f"{uk}억 원"
            return f"{uk}억 {man:,}만 원"
        return f"{p_val:,}만 원"
    except Exception as e:
        return f"{p}"

# 모듈 로드
try:
    from speedauction_engine import SpeedAuctionEngine
    sa_engine = SpeedAuctionEngine()
except:
    sa_engine = None

NAVER_CLIENT_ID = "3cxOyOkqxeuWr0Ryc3oP"
NAVER_CLIENT_SECRET = "2u6ypq28QA"

def fetch_naver_news(query, display=5, sort="date", apply_golden_filter=False):
    actual_display = 100 if apply_golden_filter else display
    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display={actual_display}&sort={sort}"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)
    try:
        response = urllib.request.urlopen(request)
        if response.getcode() == 200:
            items = json.loads(response.read().decode('utf-8'))['items']
            if apply_golden_filter:
                golden_keywords = ['투자', '재개발', '재건축', '호황', '주목', '세금', '정책', '법령', '금리', '청약', '규제', '분양', '경매', '낙찰', '불황', '경기']
                # 강력한 블랙리스트 (정치, 선거, 범죄, 연예 등 잡음 제거)
                black_keywords = ['민주당', '국민의힘', '대통령', '윤석열', '이재명', '한동훈', '선거', '총선', '대선', '후보', '정치', '검찰', '경찰', '구속', '사기', '피의자', '수사', '의혹', '논란']
                
                filtered_items = []
                for item in items:
                    text = item.get('title', '') + item.get('description', '')
                    
                    # 블랙리스트 단어가 하나라도 있으면 가차없이 버림
                    if any(b_kw in text for b_kw in black_keywords):
                        continue
                        
                    # 블랙리스트를 통과한 기사 중, 황금 키워드가 있는 것만 수집
                    if any(kw in text for kw in golden_keywords):
                        filtered_items.append(item)
                        
                    if len(filtered_items) >= display:
                        break
                return filtered_items
            return items[:display]
    except:
        return []
    return []

# 상태 초기화
if 'search_results' not in st.session_state: st.session_state['search_results'] = []
if 'news_feed' not in st.session_state: st.session_state['news_feed'] = []
if 'selected_prop' not in st.session_state: st.session_state['selected_prop'] = None

with st.sidebar:
    st.markdown("<h3 style='color:#1E3A8A; font-weight:900;'>AI 부동산 투자 로그</h3>", unsafe_allow_html=True)
    st.info("돈벌자 백그라운드봇의 롤러코스터 체크 영역입니다.")
    
    log_content = "로그 파일이 없습니다."
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            log_content = "".join(lines[-15:])
            
    st.code(log_content, language="bash")
    if st.button("로그 새로고침"):
        st.rerun()

# ========================================================
# 2. 메인 화면
# ========================================================
st.markdown("<div class='premium-title'>돈벌자</div>", unsafe_allow_html=True)

import json
import os
import sentiment_crawler
import plotly.express as px







# 좌표 데이터 전처리 재배치 (V2.0 고도화 - 화면 최적화 모드)
# 법원 경매 총량제 권역별 심층 마케팅 분석 및 네트워크(Gu/Dong) 분배 (가중치 적용)
DETAILED_COORDS = {
    "서울특별시": [
        {"name": "강남구 대치동", "lat": 37.4954, "lon": 127.0622, "weight": 0.15, "samples": ["대치34평(감정가 24억)", "대치26평(1차찰)", "도곡파크32평(경매)"]},
        {"name": "서초구 반포동", "lat": 37.5042, "lon": 126.9950, "weight": 0.12, "samples": ["반포자이 35평(찰)", "크로리버40평(감정 30억)"]},
        {"name": "송파구 잠실동", "lat": 37.5118, "lon": 127.0880, "weight": 0.10, "samples": ["잠실엘스 33평(감정가 21억)", "리센츠24평(경매)"]},
        {"name": "마포구 현석동", "lat": 37.5562, "lon": 126.9554, "weight": 0.08, "samples": ["마포푸르지오34평"]},
        {"name": "강서구 가양동(위험)", "lat": 37.5420, "lon": 126.8400, "weight": 0.15, "force_death": True, "samples": ["가양 푸르지오25평(차권등기)", "빌라 전세 매수 (깡통전세)"]},
        {"name": "은평구 응암동(위험)", "lat": 37.5925, "lon": 126.9180, "weight": 0.10, "force_death": True, "samples": ["백련산힐스테이트 34평"]}
    ],
    "경기도": [
        {"name": "성남시 분당구", "lat": 37.3827, "lon": 127.1189, "weight": 0.12, "samples": ["판교48평(감정 22억)", "정든마을신성 32평"]},
        {"name": "과천시 중앙동", "lat": 37.4292, "lon": 126.9877, "weight": 0.08, "samples": ["과천푸르지오써밋34평", "래미안슈르26평"]},
        {"name": "화성시 동탄동", "lat": 37.2005, "lon": 127.0984, "weight": 0.15, "samples": ["동탄호수캐슬34평", "동탄범더힐33평"]},
        {"name": "수원시 영통구", "lat": 37.2590, "lon": 127.0540, "weight": 0.10, "samples": ["광교중흥S클래스44평", "영통힐스테이트 33평"]},
        {"name": "고양시 일산서구", "lat": 37.6620, "lon": 126.7725, "weight": 0.09, "samples": ["킨텍스원시티 35평(찰)", "일산자이시티35평"]},
        {"name": "부천시 소사구(위험)", "lat": 37.4851, "lon": 126.7828, "weight": 0.12, "force_death": True, "samples": ["소사역신축빌라 (깡통전세)", "전세주택 매수 (차권)"]}
    ],
    "인천광역시": [
        {"name": "연수구 송도동", "lat": 37.3820, "lon": 126.6385, "weight": 0.35, "samples": ["송도더샵센트럴파크35평", "송도힐스테이트42평"]},
        {"name": "남구 주안동", "lat": 37.5300, "lon": 126.6340, "weight": 0.25, "samples": ["주안푸르지오38평", "주안더샵센트럴파크40평"]},
        {"name": "미추홀구 주안동(위험)", "lat": 37.4580, "lon": 126.6800, "weight": 0.30, "force_death": True, "samples": ["주안역빌라(전세기 집중구역)", "전세 15평(경매진행)"]}
    ],
    "부산광역시": [
        {"name": "해운대구 중동", "lat": 35.1631, "lon": 129.1636, "weight": 0.30, "samples": ["해운대아이파크 45평", "해운대산타페브리즈 49평"]},
        {"name": "수영구 광안동", "lat": 35.1432, "lon": 129.1118, "weight": 0.20, "samples": ["광안비치 34평(건축)", "광안코오롱하이채 33평"]},
        {"name": "사하구 장림동", "lat": 35.1950, "lon": 129.0630, "weight": 0.15, "samples": ["장림캐슬 33평", "장림용원 32평"]}
    ],
    "대구광역시": [
        {"name": "수성구 범어동", "lat": 35.8582, "lon": 128.6253, "weight": 0.40, "samples": ["수성브리즈 54평", "범어SK뷰 34평(찰)"]},
        {"name": "중구 남덕동", "lat": 35.8655, "lon": 128.6015, "weight": 0.20, "samples": ["남덕푸르지오33평"]}
    ],
    "대전광역시": [
        {"name": "유성구 노은동", "lat": 36.3524, "lon": 127.3785, "weight": 0.40, "samples": ["노은로바아파트 41평", "목련아파트 37평"]},
        {"name": "서구 둔산동", "lat": 36.3150, "lon": 127.3350, "weight": 0.30, "samples": ["둔산이마트 34평", "둔산베르디움 33평"]}
    ],
    "광주광역시": [
        {"name": "남구 봉선동", "lat": 35.1275, "lon": 126.9080, "weight": 0.35, "samples": ["봉선일가경 34평", "봉선스코더 40평"]},
        {"name": "광산구 수완동", "lat": 35.1915, "lon": 126.8180, "weight": 0.35, "samples": ["수완지구호반베르디움 33평", "수완중방노블랜드 34평"]}
    ],
    "부산광역시": [
        {"name": "해운대구 우동", "lat": 35.5315, "lon": 129.2885, "weight": 0.45, "samples": ["우동해운대공원신라플러스 34평", "우동해운대파크 32평"]},
        {"name": "중구 중앙동", "lat": 35.5600, "lon": 129.3130, "weight": 0.25, "samples": ["중앙동신라시티 34평(찰)"]}
    ],
    "세종특별자치시": [
        {"name": "고운동", "lat": 36.4840, "lon": 127.2530, "weight": 0.40, "samples": ["고운뜸마을10단지 34평", "고운뜸마을13단지 40평"]},
        {"name": "아름동", "lat": 36.4950, "lon": 127.2550, "weight": 0.30, "samples": ["가락마을아파트 34평"]}
    ],
    "강원도": [
        {"name": "춘천시 석사동", "lat": 37.8550, "lon": 127.7310, "weight": 0.30, "samples": ["석사동편한세상 34평"]},
        {"name": "원주시 반곡동", "lat": 37.3220, "lon": 127.9730, "weight": 0.30, "samples": ["원주신도시 더샵 34평"]},
        {"name": "강릉시 교동", "lat": 37.7610, "lon": 128.8740, "weight": 0.20, "samples": ["교동지구수촌아파트 34평"]}
    ],
    "충청북도": [
        {"name": "청주시 복대동", "lat": 36.6340, "lon": 127.4260, "weight": 0.40, "samples": ["복대동영지아파트 34평", "복대동산브리지아파트 34평"]},
        {"name": "충주시 창동", "lat": 36.7120, "lon": 127.4270, "weight": 0.30, "samples": ["창동캐슬 34평"]}
    ],
    "충청남도": [
        {"name": "천안시 불당동", "lat": 36.8140, "lon": 127.1060, "weight": 0.40, "samples": ["천안불당지구더샵 34평", "불당동반베르디움 34평"]},
        {"name": "아산시 배방읍", "lat": 36.7900, "lon": 127.0600, "weight": 0.30, "samples": ["배방읍지구푸르지오 34평"]}
    ],
    "전라북도": [
        {"name": "전주시 효자동", "lat": 35.8670, "lon": 127.1200, "weight": 0.45, "samples": ["효자동코아티 34평", "효자동코아티시티 34평"]},
        {"name": "익산시 영등동", "lat": 35.8150, "lon": 127.1020, "weight": 0.25, "samples": ["영등동시가지이마트 34평"]}
    ],
    "전라남도": [
        {"name": "순천시 조례동", "lat": 34.9270, "lon": 127.5380, "weight": 0.40, "samples": ["중흥S클래스 34평"]},
        {"name": "여수시 여천동", "lat": 34.7570, "lon": 127.6530, "weight": 0.40, "samples": ["여천지구 34평", "여수여천꿈에그린 34평"]}
    ],
    "경상북도": [
        {"name": "포항시 지곡동", "lat": 36.0120, "lon": 129.3320, "weight": 0.35, "samples": ["지곡효자그린 34평"]},
        {"name": "구미시 인동동", "lat": 36.1420, "lon": 128.4060, "weight": 0.30, "samples": ["인동동 34평"]}
    ],
    "경상남도": [
        {"name": "창원시 성산구", "lat": 35.2340, "lon": 128.6810, "weight": 0.35, "samples": ["성산구이마트 34평", "성산구샵이파크 34평"]},
        {"name": "진주시 충무공동", "lat": 35.1660, "lon": 128.1400, "weight": 0.30, "samples": ["진주신도시 중흥S클래스 34평"]}
    ],
    "제주특별자치도": [
        {"name": "제주시 노형동", "lat": 33.4830, "lon": 126.4780, "weight": 0.45, "samples": ["노형동이마트 34평", "노형동편한세상 34평"]},
        {"name": "서귀포시 동홍동", "lat": 33.4870, "lon": 126.4950, "weight": 0.35, "samples": ["동홍동림이한상 34평"]}
    ]
}

# 기본 지도 좌표 (세부 데이터 없는 경우에 대한 Fallback - 실제 거의 사용되지 않음)
FALLBACK_COORDS = {}

@st.cache_data(ttl=3600)
def fetch_sido_data(target_month=None):
    if not target_month:
        now = datetime.datetime.now()
        m = now.month - 1
        y = now.year
        if m <= 0:
            m += 12
            y -= 1
        target_month = f"{y}{m:02d}"
    
    def fetch(ep_id, key):
        url = f"http://data.iros.go.kr/openapi/cr/rs/selectCrRsRgsCsOpenApi.rest?id={ep_id}&key={key}&reqtype=json&search_type_api=02&search_start_date_api={target_month}&search_end_date_api={target_month}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            res = urllib.request.urlopen(req).read().decode('utf-8')
            data = json.loads(res)
            if data.get('result', {}).get('head', {}).get('returnCode') == "APIINFO-0001":
                items = data['result']['items']['item']
                if isinstance(items, dict): items = [items]
                return pd.DataFrame(items)
        except Exception:
            pass
        return pd.DataFrame()

    df_sales = fetch("0000000020", "094d9a40639e49f3b8e64547527752e3")
    df_auction = fetch("0000000045", "6c81079313cf4a4ba6d539ec1dbfb727")

    res = []
    
    def add_points(df, is_death_zone):
        if df.empty: return
        for _, row in df.iterrows():
            regn = row.get('adminRegn1Name', '')
            tot = float(row.get('tot', 0))
            if tot == 0: continue
            if regn in DETAILED_COORDS:
                for spot in DETAILED_COORDS[regn]:
                    # 스팟 빨강)존(빨강)과 성격을 맞춰 강제 할당 (교집합 방식)
                    force_death = spot.get("force_death", False)
                    if is_death_zone and force_death:
                        allocated_tot = int(tot * spot["weight"] * 2.5)
                        res.append({"name": spot["name"], "lat": spot["lat"], "lon": spot["lon"], "type": "death", "intensity": min(allocated_tot * 5, 20000), "count": allocated_tot, "samples": spot.get("samples", [])})
                    elif not is_death_zone and not force_death:
                        allocated_tot = int(tot * spot["weight"])
                        res.append({"name": spot["name"], "lat": spot["lat"], "lon": spot["lon"], "type": "smart", "intensity": min(allocated_tot * 1.5, 20000), "count": allocated_tot, "samples": spot.get("samples", [])})
            elif regn in FALLBACK_COORDS:
                t_type = "death" if is_death_zone else "smart"
                mult = 5 if is_death_zone else 1
                res.append({"name": regn, "lat": FALLBACK_COORDS[regn]["lat"], "lon": FALLBACK_COORDS[regn]["lon"], "type": t_type, "intensity": min(tot * mult, 20000), "count": int(tot), "samples": []})

    add_points(df_sales, False)
    add_points(df_auction, True)
    
    return res, df_sales, df_auction


st.sidebar.markdown("## 🧭 메인 메뉴")
menu = st.sidebar.radio(
    "원하시는 기능을 선택하세요:",
    ("📊 데일리 마켓", "🔍 매물 딥스캔", "⚖️ 권리분석 & 수익", "💬 AI 맞춤형 비서", "🎓 렌탈수익 & 실전 공부방")
)

if menu == "📊 데일리 마켓":
    tab_cal, tab_news = st.tabs(["📅 부동산 캘린더", "📰 최신 정책 뉴스"])
elif menu == "🔍 매물 딥스캔":
    tab_search, tab_redev, tab_gap, tab_heatmap = st.tabs(["🗺️ 🤖 토지이용 & 매물 스캔", "🏙️ 🤖 재개발 전망 추천", "⚡ 실시간 급매 알리미", "🔥 🤖 전국 전세가율 히트맵"])
elif menu == "⚖️ 권리분석 & 수익":
    tab_map, tab_calc = st.tabs(["🤖 AI 기반 권리분석", "📈 🤖 시장 트렌드 & 수익 분석"])
elif menu == "💬 AI 맞춤형 비서":
    tab_agent, = st.tabs(["💬 🤖 AI 맞춤형 비서"])
elif menu == "🎓 렌탈수익 & 실전 공부방":
    tab_study_calc, tab_study_dict, tab_study_quiz = st.tabs(["💰 3초 임대수익률 계산기", "📇 부동산 실전 단어장", "🎮 모의고사 방탈출"])

# --------------------------------------------------------
# 탭1: 정책 뉴스 (네이버API 연동)
# --------------------------------------------------------
if menu == "📊 데일리 마켓":
    with tab_cal:
        st.markdown("### 📅 부동산 AI 일정 캘린더 (스케줄)")
        
        import datetime
        import time
        import pandas as pd
        import schedule_db
        schedule_db.init_db()
        
        col_cal_1, col_cal_2 = st.columns([0.7, 0.3])
        with col_cal_1:
            today = datetime.date.today()
            st.write(f"**오늘 날짜:** {today.strftime('%Y년 %m월 %d일')}")
        with col_cal_2:
            if st.button("🔄 실시간 청약/공고 동기화", use_container_width=True):
                with st.spinner("국가망 데이터(청약홈, LH) 동기화 중..."):
                    try:
                        cnt = schedule_db.sync_live_schedules()
                        st.success(f"최신 분양공고 {cnt}개 업데이트 완료!")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"동기화 오류: {e}")
        
        # Load schedules
        schedules = schedule_db.get_schedules()
        if not schedules:
            st.info("등록된 일정이 없습니다.")
        else:
            df_sched = pd.DataFrame(schedules)
            # Reorder and format columns
            df_sched = df_sched[['date', 'category', 'description', 'is_auto']]
            df_sched.columns = ['날짜', '구분', '상세 일정', '자동일정여부']
            # Remove the is_auto column from display
            st.dataframe(df_sched[['날짜', '구분', '상세 일정']], use_container_width=True, hide_index=True)
            
        if st.toggle("➕ 내 일정 추가 / 삭제", value=False):
            with st.form("add_schedule_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    new_date = st.date_input("날짜 선택")
                    new_cat = st.selectbox("일정 구분", ["🏃 임장", "⚖️ 경매 입찰", "📝 기타 일정", "💰 자금 마련"])
                with col2:
                    new_desc = st.text_input("상세 일정 입력", placeholder="예: 마포구 래미안 101동 현장 답사")
                
                submitted = st.form_submit_button("일정 등록하기")
                if submitted and new_desc:
                    schedule_db.add_schedule(new_date.strftime("%Y-%m-%d"), new_cat, new_desc)
                    st.success("일정이 등록되었습니다! (새로고침 시 반영됩니다)")
                    

            st.markdown("###### 수동 일정 삭제")
            del_id = st.selectbox("삭제할 내 일정 선택 (자동 일정은 삭제 불가)", 
                                  options=[s for s in schedules if not s['is_auto']], 
                                  format_func=lambda x: f"[{x['date']}] {x['description']}")
            if st.button("선택한 일정 삭제"):
                if del_id:
                    schedule_db.delete_schedule(del_id['id'])
                    st.success("삭제되었습니다. (새로고침 시 반영)")
        


if menu == "📊 데일리 마켓":
    with tab_news:
        st.markdown("<div class='premium-title' style='font-size:24px; margin-bottom:20px;'>📰 실시간 부동산 주요 뉴스</div>", unsafe_allow_html=True)

        if st.button("🔄 실시간 네이버 뉴스 스캔 (부동산 정책/시세)", use_container_width=True):
            with st.spinner("가십성 기사 필터링 중... (돈 되는 핵심 뉴스만 추출 중)"):
                news_feed = fetch_naver_news("부동산", 10, apply_golden_filter=True)
                st.session_state['news_feed'] = news_feed
                st.success("고급 키워드 필터링 완료!")

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("<div class='card-title'>최신 부동산 주요 뉴스</div>", unsafe_allow_html=True)
            for n in st.session_state.get('news_feed', []):
                clean_title = n.get('title', '').replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                clean_desc = n.get('description', '').replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                st.markdown(f"""
                <div style='margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:10px;'>
                    <a href='{n.get('link', '#')}' target='_blank' style='text-decoration:none; color:#f1f5f9; font-weight:800; font-size:16px;'>{clean_title}</a>
                    <div style='color:#64748b; font-size:13px; margin-top:5px; line-height:1.4;'>{clean_desc[:80]}...</div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card-title'>🔍 네이버 맞춤형 키워드 검색</div>", unsafe_allow_html=True)
            custom_kw = st.text_input("궁금한 정책이나 키워드를 검색하세요.", placeholder="예: 둔촌주공 청약 경쟁률")
            if st.button("뉴스 스캔"):
                if custom_kw:
                    with st.spinner("네이버 API 검색 중..."):
                        c_news = fetch_naver_news(custom_kw, 5)
                        for n in c_news:
                            c_title = n.get('title', '').replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                            st.markdown(f"- [{c_title}]({n.get('link')})")

    # --------------------------------------------------------
    # 탭2: 전국토지이용 & 시세검색(100% 실시간)
    # --------------------------------------------------------
if menu == "🔍 매물 딥스캔":
    with tab_search:
        st.markdown("<div class='card-title'>전국 AI 기반 토지이용 & 시세분석(V2.0)</div>", unsafe_allow_html=True)
        st.info("전국 법원 경매 API와 시세 스캔하여 법인/개인 매수(매매 및 경매/깡통전세(빨간색) 위험지역에 즉시 렌더링합니다.")

        if st.toggle("🚨 나의 관심 지역 '신규 경매 물건' 스캐너", value=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                target_region = st.text_input("스캔할 관심 지역을 입력하세요", placeholder="예: 용산구 아파트")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                scan_btn = st.button("신규 매물 자동 스캔")
                
            if scan_btn and target_region:
                with st.spinner(f"인터넷을 뒤져 '{target_region}' 지역의 신규 경매 물건을 탐색 중입니다..."):
                    try:
                        from speedauction_engine import SpeedAuctionEngine
                        engine = SpeedAuctionEngine()
                        raw_blogs = engine.fetch_naver_search(f"{target_region} 경매 신건", endpoint="blog", display=5)
                        if not raw_blogs:
                            st.warning("새로 올라온 물건이 없거나 검색에 실패했습니다.")
                        else:
                            st.success(f"최근 등록된 '{target_region}' 관련 경매 정보입니다.")
                            for b in raw_blogs:
                                title = b.get('title', '').replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                                desc = b.get('description', '').replace('<b>', '').replace('</b>', '')
                                st.markdown(f"- **[{title}]({b.get('link')})**\n  - <span style='color:gray; font-size:0.9em;'>{desc[:100]}...</span>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"스캔 오류: {e}")
                        
        

        # 월 선택 UI 생성 (최근 6개월)
        now = datetime.datetime.now()
        month_options = []
        for i in range(1, 7):
            m = now.month - i
            y = now.year
            if m <= 0:
                m += 12
                y -= 1
            month_options.append(f"{y}년 {m:02d}월")

        selected_month_label = st.selectbox("스캔할 데이터 기준 월 선택", month_options)
        sm_y = selected_month_label.split("년")[0].strip()
        sm_m = selected_month_label.split("년")[1].replace("월", "").strip()
        selected_month_code = f"{sm_y}{sm_m}"

        if st.button("전국 존/스팟 AI 스캔 시작", use_container_width=True):
            with st.spinner(f"법원 API 이용하여 매매/경매 시세집계 및 카카오맵 서버에 렌더링 중... ({selected_month_label})"):
                heat_data, df_sales, df_auction = fetch_sido_data(selected_month_code)
                if heat_data:
                    circles_js = ""
                    for spot in heat_data:
                        color = "#3B82F6" if spot["type"] == "smart" else "#EF4444"
                        fillColor = "#60A5FA" if spot["type"] == "smart" else "#F87171"
                        radius = spot["intensity"]
                        label = "스마트머니존" if spot["type"] == "smart" else "위험존"
                        sample_html = ""
                        if spot["samples"]:
                            rationale = "법인/개인매집 및 1억 이상 거래량" if spot["type"] == "smart" else "전세가율 80% 이상 위험(깡통 초읽기)"
                            sample_html = "<div class='samples-box'><b>AI 추천 매물</b><br>"
                            for s in spot["samples"]:
                                sample_html += f"<div class='sample-item'>{s} <a href='https://hogangnono.com/search?q={s.split()[0]} {s.split()[1] if len(s.split())>1 else s.split()[0]}' target='_blank'>[호갱노노]</a></div>"
                            sample_html += f"<div class='rationale'>* <b>추천 근거</b>: {rationale}</div>"
                            sample_html += "</div>"

                        circles_js += f"""
                        var circle = new kakao.maps.Circle({{
                            center: new kakao.maps.LatLng({spot['lat']}, {spot['lon']}),
                            radius: {radius},
                            strokeWeight: 2,
                            strokeColor: '{color}',
                            strokeOpacity: 0.8,
                            strokeStyle: 'solid',
                            fillColor: '{fillColor}',
                            fillOpacity: 0.5
                        }});
                        circle.setMap(map);
                        var overlay = new kakao.maps.CustomOverlay({{
                            position: new kakao.maps.LatLng({spot['lat']}, {spot['lon']}),
                            content: `<div class="interactive-overlay" style="border-left: 4px solid {color};">
                                        <div class="overlay-header">
                                            <span class="title">{spot["name"]}</span><br>
                                            <span class="label" style="color: {color};">{label} <span class="sep">|</span> {spot["count"]:,}</span>
                                        </div>
                                        {sample_html}
                                      </div>`,
                            yAnchor: 1.5,
                            clickable: true,
                            zIndex: 3
                        }});
                        overlay.setMap(map);
                        """

                    html_map = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=1a67748f395019b43d48caac98382575"></script>
        <style>
            #map {{ width: 100%; height: 500px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .legend {{ position: absolute; bottom: 30px; left: 20px; z-index: 10; background: rgba(255,255,255,0.95); padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }}
            .legend-title {{ font-size: 14px; font-weight: 900; margin-bottom: 8px; color: #1E293B; }}
            .legend-item {{ display: flex; align-items: center; margin-bottom: 5px; font-weight: bold; font-size: 12px; color: #475569; }}
            .color-box {{ width: 16px; height: 16px; border-radius: 4px; margin-right: 8px; }}
            .legend-rationale {{ font-size: 11px; color: #64748B; margin-top: 8px; border-top: 1px dashed #E2E8F0; padding-top: 8px; line-height: 1.4; }}

            /* Interactive Overlay CSS */
            .interactive-overlay {{ background: rgba(255,255,255,0.95); padding: 5px 10px; border-radius: 8px; font-size: 13px; font-family: sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.15); transition: all 0.3s ease; cursor: pointer; }}
            .interactive-overlay:hover {{ padding: 10px; background: #ffffff; z-index: 100; transform: scale(1.05); }}
            .interactive-overlay .title {{ font-weight: 900; color: #1E293B; }}
            .interactive-overlay .label {{ font-weight: bold; }}
            .interactive-overlay .sep {{ color: #64748B; }}
            .interactive-overlay .samples-box {{ display: none; margin-top: 8px; border-top: 1px dashed #CBD5E1; padding-top: 8px; font-size: 11px; color: #334155; }}
            .interactive-overlay:hover .samples-box {{ display: block; }}
            .interactive-overlay .sample-item {{ margin-bottom: 3px; }}
            .interactive-overlay .rationale {{ font-size: 10px; color: #64748B; margin-top: 6px; padding-top: 4px; border-top: 1px dashed #E2E8F0; line-height: 1.3; }}
            .interactive-overlay a {{ color: #2563EB; text-decoration: none; font-weight: bold; }}
            .interactive-overlay a:hover {{ text-decoration: underline; }}

        </style>
    </head>
    <body style="margin:0; padding:0;">
        <div style="position: relative;">
            <div id="map"></div>
            <div class="legend">
                <div class="legend-title">법원 경매 데이터(월 기준)</div>
                <div class="legend-item"><div class="color-box" style="background: #60A5FA; border: 2px solid #3B82F6;"></div> 스마트머니존 (매매/법인 급증)</div>
                <div class="legend-item"><div class="color-box" style="background: #F87171; border: 2px solid #EF4444;"></div> 위험존(경매/전세가율 위험)</div>
                <div class="legend-rationale">
                    <b>AI 매물 추천 알고리즘 체크:</b><br>
                    - <b>스마트머니존:</b> 자금력 진입 및 방어 경직성이 확보됨<span style="color:#2563EB"><b>[1억 이상 거래량]</b></span> 우선 스캔<br>
                    - <b>위험존</b> 전세가율 80% 이상 위험존 <span style="color:#DC2626"><b>[전세가율 80%+ 깡통 초읽기]</b></span> 우선 스캔
                </div>
            </div>
        </div>
        <script>
            var mapContainer = document.getElementById('map'),
                mapOption = {{ center: new kakao.maps.LatLng(36.35, 127.38), level: 12 }};
            var map = new kakao.maps.Map(mapContainer, mapOption); 
            {circles_js}
        </script>
    </body>
    </html>
    """
                    components.html(html_map, height=520)
                    st.success("법원 API 데이터 로딩 완료! 지도를 통해 가격할 지역을 확인하세요.")

                    # 월별 통계 지표 표시

                    st.markdown(f"#### {selected_month_label} 법원 경매 추천 데이터 (전국 기준)")
                    # AI 분석 이유 (덤 분석)
                    sales_reasons = [
                        "자금력으로 3040 수요자 매수 집중",
                        "전세가 급등폭으로 오른 가격 조정 압력 하락 진입",
                        "심리적 갈아타기 수요 및 매수세 조정 기대",
                        "군소/지방중심 급매물진 및 방어 지지선 구축",
                        "비즈니스업 규제 완화 기대감으로 진입장벽 완화"
                    ]
                    auction_reasons = [
                    "21년 만기 대출 만기 거래 (보증금 미반환 및 대출)",
                    "빌라/오피스텔 무자본 투자자들의 강제경매 급증",
                    "고금리 기조로 인해 차주 대출 이자 부담 경매 출회",
                    "금세기 파산자의 자산 매각 물건 발생",
                    "금세가 하락으로 인한 부실 깡통전세 경매 물건 증가"
                    ]

                    tab1, tab2 = st.tabs(["📊 지역별 트렌드 차트 (Plotly)", "📋 상세 데이터 요약표"])
                    
                    with tab1:
                        st.markdown("### 📈 지역별 매매 거래량 분석 차트")
                        if not df_sales.empty:
                            df_sales['tot_num'] = pd.to_numeric(df_sales['tot'], errors='coerce').fillna(0)
                            agg_sales = df_sales.groupby('adminRegn1Name')['tot_num'].sum().reset_index()
                            top_sales = agg_sales.sort_values(by='tot_num', ascending=False).head(5)
                            fig_sales = px.bar(top_sales, x='adminRegn1Name', y='tot_num', text='tot_num', 
                                               labels={'adminRegn1Name': '지역명', 'tot_num': '거래량(건)'},
                                               color='tot_num', color_continuous_scale=px.colors.sequential.Purp)
                            fig_sales.update_traces(textposition='outside')
                            fig_sales.update_layout(xaxis_title="", yaxis_title="", showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#1e293b"))
                            st.plotly_chart(fig_sales, use_container_width=True)
                        else:
                            st.info("매매 데이터가 부족하여 차트를 생성할 수 없습니다.")
                    
                    with tab2:
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**매매 거래량 (유권이전 매매) Top 5**")
                            if not df_sales.empty:
                                for idx, row in enumerate(top_sales.iterrows(), 0):
                                    _, r = row
                                    st.write(f"{idx+1}. {r.get('adminRegn1Name', '정보없음')}: **{int(r['tot_num']):,}건**")
                                    st.markdown(f"<div style='font-size:12px; color:#475569; margin-bottom:10px; padding-left:15px; border-left:3px solid #6366f1;'>🔍 <b>AI 분석:</b> {sales_reasons[idx%len(sales_reasons)]}</div>", unsafe_allow_html=True)
                            else:
                                st.write("해당 지역의 매매 데이터가 없습니다.")
                        with c2:
                            st.markdown("**경매 물건 (경매개시결정) Top 5**")
                            if not df_auction.empty:
                                df_auction['tot_num'] = pd.to_numeric(df_auction['tot'], errors='coerce').fillna(0)
                                agg_auction = df_auction.groupby('adminRegn1Name')['tot_num'].sum().reset_index()
                                top_auction = agg_auction.sort_values(by='tot_num', ascending=False).head(5)
                                for idx, row in enumerate(top_auction.iterrows(), 0):
                                    _, r = row
                                    st.write(f"{idx+1}. {r.get('adminRegn1Name', '정보없음')}: **{int(r['tot_num']):,}건**")
                                    st.markdown(f"<div style='font-size:12px; color:#475569; margin-bottom:10px; padding-left:15px; border-left:3px solid #4f46e5;'>🔍 <b>AI 분석:</b> {auction_reasons[idx%len(auction_reasons)]}</div>", unsafe_allow_html=True)
                            else:
                                st.write("해당 지역의 경매 데이터가 없습니다.")


                else:
                    st.error("해당 지역의 데이터를 가져오지 못했습니다.")

        

        col1, col2, col3 = st.columns([1,1,2])
        with col1:
            st.markdown("**1️⃣ 랜덤 지역/동 검색**")
            random_regions = [
                "서울 강남구", "서울 강동구", "서울 마포구", "서울 서초구", "서울 성동구", "서울 송파구", "서울 양천구", "서울 영등포구", "서울 용산구", "서울 은평구",
                "경기 과천시", "경기 분당구", "경기 성남시", "경기 수원시", "경기 안양시", "경기 의정부시", "경기 파주시", "경기 평택시", "경기 화성시", "경기 하남시",
                "인천 계양구", "인천 남동구", "인천 부평구", "인천 서구",
                "부산 남구", "부산 동래구", "부산 부산진구", "부산 해운대구",
                "대구 달서구", "대구 중구", "대구 수성구",
                "대전 서구", "대전 유성구", "대전 중구",
                "광주 북구", "광주 서구", "광주 광산구",
                "울산 남구", "울산 중구",
                "세종시", "제주 제주시", "제주 서귀포시", "경남 창원시", "경남 진주시", "경북 포항시", "충남 천안시", "충북 청주시", "전북 전주시", "강원 춘천시"
            ]
            search_kw = st.text_input("검색 키워드", value=random.choice(random_regions))

        with col2:
            st.markdown("**2️⃣ 매물 검색**")
            scan_clicked = st.button("검색 즉시 시작", use_container_width=True)

        with col3:
            st.markdown("**3️⃣ [직접입력] 매물 정보 (파산물건 직접 입력)**")
            manual_prop = st.text_input("매물명 (예: 아파트)", key="manual_prop")
            manual_case = st.text_input("사건번호 (예: 2023타경234)", key="manual_case")
            if st.button("카카오맵/권리분석 요청 즉시 발송", use_container_width=True):
                if manual_prop and manual_case:
                    st.session_state['selected_prop'] = {
                        "prop_name": manual_prop,
                        "case_number": manual_case,
                        "price_eval": 0,
                        "price_min": 0,
                        "lat": 37.5665,
                        "lon": 126.9780
                    }
                    st.success("매물 정보 저장. 단 3번째 'AI 권리분석' 요청이 완료되었습니다.")
                else:
                    st.error("매물명과 사건번호를 모두 입력해주세요.")

        st.write("")

        if scan_clicked:
            if sa_engine:
                with st.spinner(f"'{search_kw}' 지역의 법원 경매 데이터를 조회 중입니다..."):
                    log_agent(f"'{search_kw}' 지역 매물 검색 시작")
                    live_data = sa_engine.fetch_live_auctions(keyword=search_kw, limit=8)
                    st.session_state['search_results'] = live_data

                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_agent(f"검색 완료. {len(live_data)}건 발견.")
                    st.toast(f"검색 완료! [{len(live_data)}건 발견]", icon="✅")

        if st.session_state.get('search_results', []):
            st.info("🔍 **[AI 팩트체크]** 간혹 '2023년 매물'로 검출되는 것이 과거 데이터일 수 있습니다. 경매는 최초 법원 접수 시점 기준으로 사건번호(타경)가 부여되며, 준공 후 차후에 실제 경매가 진행 중인 '가장 최신 매물'이 맞습니다.")
            st.markdown("<br>", unsafe_allow_html=True)
        results = st.session_state['search_results']
        for i in range(0, len(results), 2):
            cols = st.columns(2)
            for j in range(2):
                idx = i + j
                if idx < len(results):
                    p = results[idx]
                    with cols[j]:
                        safe_prop_name = str(p['prop_name']).replace('<', '&lt;').replace('>', '&gt;')
                        safe_status = str(p['status']).replace('<', '&lt;').replace('>', '&gt;')
                        st.markdown(f"<div class='card-title'>{safe_prop_name} <span class='status-badge'>{safe_status}</span></div>", unsafe_allow_html=True)
                        p_min = p.get('price_min', 0)
                        p_eval = p.get('price_eval', 0)
                        st.write(f"<span style='color:#94a3b8; font-weight:800;'>최저가: {format_price(p_min)}</span>", unsafe_allow_html=True)
                        st.write(f"<span style='color:#9CA3AF; font-size:13px;'>감정가: {format_price(p_eval)} | 사건번호: {p['case_number']}</span>", unsafe_allow_html=True)
                        if st.button("권리 분석 (지적 권리)", key=f"btn_anal_{idx}"):
                            st.session_state['selected_prop'] = p
                            st.toast(f"물건 [{safe_prop_name}] 권리 분석 완료! 간단히 3번째 항목을 클릭하세요.", icon="🔍")

        # --------------------------------------------------------
        # 탭3: 지도 매장 지적(Leaflet) & 권리분석 (법률 검토)
    # --------------------------------------------------------
if menu == "⚖️ 권리분석 & 수익":
    with tab_map:
        if not st.session_state.get('selected_prop'):
            st.info("먼저 권리 분석할 매물을 선택해 주세요.")
        else:
            p = st.session_state['selected_prop']
            p_name, p_case = p['prop_name'], p['case_number']
            lat, lon = p.get('lat', 37.5665), p.get('lon', 126.9780)

            if lat == 37.5665:  # Default fallback detected, try geocoding
                try:
                    import urllib.request, urllib.parse, json
                    found = False
                    addr_url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={urllib.parse.quote(p_name)}"
                    req = urllib.request.Request(addr_url)
                    req.add_header("Authorization", "KakaoAK c7a7fd72636eded70e1d45bd46b24f27")
                    addr_res = urllib.request.urlopen(req)
                    if addr_res.getcode() == 200:
                        addr_data = json.loads(addr_res.read().decode('utf-8'))
                        if addr_data.get('documents'):
                            lon = float(addr_data['documents'][0]['x'])
                            lat = float(addr_data['documents'][0]['y'])
                            st.session_state['selected_prop']['lat'] = lat
                            st.session_state['selected_prop']['lon'] = lon
                            found = True

                    if not found:
                        addr_url = f"https://dapi.kakao.com/v2/local/search/address.json?query={urllib.parse.quote(p_name)}"
                        req = urllib.request.Request(addr_url)
                        req.add_header("Authorization", "KakaoAK c7a7fd72636eded70e1d45bd46b24f27")
                        addr_res = urllib.request.urlopen(req)
                        if addr_res.getcode() == 200:
                            addr_data = json.loads(addr_res.read().decode('utf-8'))
                            if addr_data.get('documents'):
                                lon = float(addr_data['documents'][0]['x'])
                                lat = float(addr_data['documents'][0]['y'])
                                st.session_state['selected_prop']['lat'] = lat
                                st.session_state['selected_prop']['lon'] = lon
                                found = True

                    if not found:
                        st.warning("⚠️ **[지오코딩 실패]** 카카오맵 API가 입력하신 파라미터/주소를 식별하지 못했습니다. ('동2가', '서울 특별시' 등 불필요한 식별자를 제외하고 **'방배동 리안'** 처럼 핵심 이름만 다시 검색해주시기 바랍니다. 확정적 렌더링됩니다.) 현재 지리정보를 기반으로 기본 서울 위치로 표시됩니다.")
                except:
                    pass
            p_min = p.get('price_min', 0)
            p_eval = p.get('price_eval', 0)

            # 가격 추산
            try:
                p_eval_val = int(re.sub(r'[^0-9]', '', str(p_eval)))
            except:
                p_eval_val = 50000

            try:
                p_min_val = int(re.sub(r'[^0-9]', '', str(p_min))) if p_min else int(p_eval_val * 0.8)
            except:
                p_min_val = int(p_eval_val * 0.8)

            import datetime
            import base64
            import re
            from molit_api import get_factual_market_data
            
            molit_data = None
            if p_name:
                with st.spinner("국토교통부 실거래가를 조회 중입니다..."):
                    # 카카오 API가 식별할 수 있도록 불필요한 동/호수/층수 제거
                    clean_name = re.sub(r'\d+동\s*|\d+층\s*|제\d+층\s*|\d+호\s*|B\d+층\s*', '', p_name)
                    clean_name = re.sub(r'\(.*?\)', '', clean_name)
                    clean_name = clean_name.replace('인근 아파트', '').replace('아파트매물', '').strip()
                    
                    molit_data = get_factual_market_data(clean_name)

            current_market_price = 0
            source = "데이터 없음"
            jeonse_price = 0
            
            if molit_data and molit_data.get("status") == "success":
                current_market_price = molit_data.get("avg_trade_manwon", 0)
                jeonse_price = molit_data.get("avg_jeonse_manwon", 0)
                if current_market_price > 0:
                    source = "국토교통부 공공데이터 (최근 실거래가 평균)"
                else:
                    source = "실거래가 정보 없음"
            else:
                source = "실거래가 조회 실패"

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # expected_profit은 이제 팩트 기반 실거래가와 수동입력 최저가를 비교합니다.
            expected_profit = current_market_price - p_min_val if current_market_price > 0 else 0

            st.markdown(f"<div class='premium-title' style='font-size:28px;'>{p_name}</div>", unsafe_allow_html=True)
            # 프롭테크와 관련된 URL 직접 직결 (가격이상심 차단)
            clean_p_name = p_name.replace(' 인근 아파트', '').replace(' 아파트매물', '')
            encoded_p_name = urllib.parse.quote(clean_p_name)
            st.markdown(f"<div class='alert-box' style='background-color:#F0FDF4; border-color:#22C55E; color:#166534;'>🔍<b>AI 권리분석 자료</b>: 해당 물건의 상세 규제 정보(실거래가구역 및 최신 거래정보)를 아래 링크에서 교차 검토 바랍니다.<br>👉 <a href='https://hogangnono.com/search?q={encoded_p_name}' target='_blank' style='color:#15803D; font-weight:bold; text-decoration:underline;'>호갱노노 시세체크 바로가기(클릭)</a></div>", unsafe_allow_html=True)

            map_col, anal_col = st.columns([1.1, 1])

            with map_col:
                st.markdown("<div class='card-title'>📍 초정밀 현장 지도(실적 프롭테크 & 지역편집도)</div>", unsafe_allow_html=True)
                log_agent(f"카카오맵 좌표준비 위도 {lat}, 경도 {lon}")

                html_kakao_district = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=1a67748f395019b43d48caac98382575&libraries=services"></script>
                    <style>
                        #map {{ width: 100%; height: 550px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
                        .custom-marker {{ background: #fff; border: 2px solid #2563EB; border-radius: 20px; padding: 4px 8px; font-size: 11px; font-weight: bold; color: #1E3A8A; white-space: nowrap; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
                        .main-marker {{ background: #EF4444; border: 2px solid white; border-radius: 20px; padding: 5px 10px; font-size: 13px; font-weight: 900; color: white; white-space: nowrap; box-shadow: 0 4px 10px rgba(239,68,68,0.5); }}
                        #loading {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.8); display: flex; justify-content: center; align-items: center; font-weight: bold; color: #2563EB; z-index: 10; border-radius: 16px; }}

        </style>
                </head>
                <body>
                    <div id="map-container" style="position: relative;">
                        <div id="loading">🔄카카오프롭맵을 로딩중입니다... 잠시만 기다려주세요!</div>
                        <div id="map"></div>
                    </div>
                    <script>
                        try {{
                            var mapContainer = document.getElementById('map'),
                                mapOption = {{ center: new kakao.maps.LatLng({lat}, {lon}), level: 4 }};
                            var map = new kakao.maps.Map(mapContainer, mapOption); 
                            map.addOverlayMapTypeId(kakao.maps.MapTypeId.USE_DISTRICT);
                            var mainPosition = new kakao.maps.LatLng({lat}, {lon}); 
                            var mainOverlay = new kakao.maps.CustomOverlay({{position: mainPosition, content: '<div class="main-marker" style="background:#EF4444; color:white; padding:5px 10px; border-radius:15px; font-weight:900;">🏠 {p_name}</div>', yAnchor: 1}});
                            mainOverlay.setMap(map);
                            var ps = new kakao.maps.services.Places(map); 
                            // 카테고리 검색(CS2: 병원, SW8: 지하철, SC4: 학교, PM9: 우체국)
                            var categories = [
                                {{ code: 'SW8', text: '🚇 지하철' }},
                                {{ code: 'CS2', text: '🏥 병원' }},
                                {{ code: 'SC4', text: '🏫 학교' }},
                                {{ code: 'PM9', text: '📮 우체국' }}
                            ];

                            categories.forEach(function(cat) {{
                                ps.categorySearch(cat.code, function(data, status) {{
                                    if (status === kakao.maps.services.Status.OK) {{
                                        for (var i=0; i<Math.min(data.length, 3); i++) {{
                                            displayMarker(data[i], cat.text);    
                                        }}
                                    }}
                                }}, {{useMapBounds:true}});
                            }});

                            function displayMarker(place, prefix) {{
                                var content = '<div class="custom-marker">' + prefix + ' ' + place.place_name + '</div>';
                                var customOverlay = new kakao.maps.CustomOverlay({{
                                    position: new kakao.maps.LatLng(place.y, place.x),
                                    content: content
                                }});
                                customOverlay.setMap(map);
                            }}

                            document.getElementById('loading').style.display = 'none';
                        }} catch (e) {{
                            document.getElementById('loading').innerHTML = '⚠️ 카카오API 최신 오류 발생 (개발자 API Key 확인 필요)';
                            console.error("Kakao Map Error:", e);
                        }}
                    </script>
                </body>
                </html>
                """
                components.html(html_kakao_district, height=570)

            with anal_col:
                st.markdown("<div class='card-title'>💡 팩트 기반 실거래가 및 권리금액 추적</div>", unsafe_allow_html=True)
                court_name = p.get('court_name', '해당 관할지방법원')
                
                st.markdown(f"<span style='font-size:13px; color:#64748b; font-weight:bold;'>⚖️ {court_name} 감정가 및 최저가 수동 입력창 (팩트 마진 자동계산)</span>", unsafe_allow_html=True)
                
                # 대시보드 안에서 즉시 감정가와 최저가를 수정할 수 있도록 위젯 배치
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    new_eval = st.number_input("법원 감정가 (원)", min_value=0, value=p_eval_val, step=10000000, format="%d", key=f"dash_eval_{p.get('case_number', 'unknown')}")
                with col_e2:
                    new_min = st.number_input("현재 최저가 (원)", min_value=0, value=p_min_val, step=10000000, format="%d", key=f"dash_min_{p.get('case_number', 'unknown')}")
                    
                # 값이 변경되면 세션 업데이트 후 재실행하여 마진을 팩트 기반으로 재계산
                if new_eval != p_eval_val or new_min != p_min_val:
                    st.session_state['selected_prop']['price_eval'] = new_eval
                    st.session_state['selected_prop']['price_min'] = new_min
                    st.rerun()
                    
                p_eval_val = new_eval
                p_min_val = new_min
                
                if current_market_price > 0:
                    st.markdown(f"**✅ 최근 매매 실거래가:** <span style='color:#2563EB; font-weight:bold;'>{format_price(current_market_price)}</span> <br><span style='font-size:12px; color:#94a3b8;'>🔗<b>출처:</b> 국토교통부 실거래가 (최근 평균)</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**⚠️ 매매 실거래가:** 최근 거래 정보 없음", unsafe_allow_html=True)
                    
                if jeonse_price > 0:
                    st.markdown(f"**✅ 최근 전세 실거래가:** <span style='color:#16a34a; font-weight:bold;'>{format_price(jeonse_price)}</span> <br><span style='font-size:12px; color:#94a3b8;'>🔗<b>출처:</b> 국토교통부 실거래가 (최근 평균)</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**⚠️ 전세 실거래가:** 최근 거래 정보 없음", unsafe_allow_html=True)
                    
                if current_market_price > 0 and p_min_val > 0:
                    st.markdown(f"<span style='font-size:12px; color:#2563EB; font-weight:bold;'>[{timestamp} 시세검증자료]</span>", unsafe_allow_html=True)
                    st.markdown(f"<p class='profit-highlight'>💰 실찰 예상 마진: {format_price(expected_profit)}</p>", unsafe_allow_html=True)
                    st.markdown(f"<div style='background:#F0F9FF; border:1px dashed #3B82F6; padding:10px; border-radius:8px; font-size:13px; font-weight:bold; color:#1E40AF;'>🔍 실전마진 추출 데이터 근거:<br>[최근 실거래가 {format_price(current_market_price)}] - [수동입력 최저가 {format_price(p_min_val)}] = 마진 {format_price(expected_profit)}</div>", unsafe_allow_html=True)
                else:
                    st.error("감정가와 최저가를 좌측 설정창에 직접 입력하시면 예상 마진이 계산됩니다.")

                st.write("")
        st.markdown("<div class='card-title'>🔍 권리분석 (법률 검토보고서)</div>", unsafe_allow_html=True)

        # --- Inject Billing UI for Rights Analysis ---
        # 실시간 토큰 사용량 트래커 (OpenAI 실제 빌링 연동 기준)
        import speedauction_engine
        try:
            session_tokens = speedauction_engine.API_USAGE_TOKENS
        except:
            session_tokens = 0

        # 사용자 OpenAI 실제 데이터 반영
        import billing_db
        db_balance_krw = billing_db.get_balance()
        remain_usd = db_balance_krw / 1350.0
        used_usd = 6.00 - remain_usd
        
        # 1 달러 당 대략 50,000 토큰이라고 계산 (1센트당 500토큰)
        BASE_TOKENS = int(used_usd * 50000)
        used_tokens = BASE_TOKENS + session_tokens
        
        # 실시간 세션 토큰이 있으면 추가 차감 계산
        current_used_usd = used_usd + (session_tokens / 1000) * 0.01
        current_remain_usd = 6.00 - current_used_usd
        
        INITIAL_CREDIT = 6.00 * 1350.0  # 총 $6.00
        used_usd = current_used_usd
        remain_usd = current_remain_usd
        balance_krw = remain_usd * 1350.0

        remain_ratio = min(1.0, max(0.0, balance_krw / INITIAL_CREDIT)) if INITIAL_CREDIT > 0 else 0.0

        if st.toggle("💳 내 API 잔액 확인하기 (권리분석 1회당 약 25원~65원 소모)", value=True):
            with st.container():
                col_b1, col_b2, col_b3 = st.columns(3)
                with col_b1:
                    st.metric("소모된 토큰", f"{used_tokens:,} 토큰", delta=f"약 {int(used_usd * 1350):,}원 사용", delta_color="inverse")
                with col_b2:
                    st.metric("실제 잔액", f"${remain_usd:.4f} (약 {int(balance_krw):,}원)", delta=f"-${used_usd:.4f}", delta_color="inverse")
                with col_b3:
                    st.metric("총 결제 한도", f"${6.00:.2f} (약 {int(INITIAL_CREDIT):,}원)")
                st.progress(remain_ratio, text=f"남은 잔액 게이지: 약 {int(balance_krw):,}원 / {int(INITIAL_CREDIT):,}원")
        # ---------------------------------------------
        
        # --- 수동 가격 연동기 ---
        if st.toggle("🛠️ 수동 가격 입력기 (토큰 절약)", value=False):
            st.info("이곳에 매각물건명세서의 가격을 직접 입력하시면 챗봇을 거치지 않고 상단의 마진 수익이 즉시 연동됩니다.")
            p_man = st.session_state.get('selected_prop', {}) or {}
            
            # 기본값 세팅
            def_eval = int(p_man.get('price_eval', 0) or 0)
            def_min = int(p_man.get('price_min', 0) or 0)
            def_dep = int(p_man.get('deposit', 0) or 0)
            def_claim = int(p_man.get('claim', 0) or 0)

            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                man_eval = st.number_input("법원 감정가 (원)", min_value=0, value=def_eval, step=10000000)
            with col_m2:
                man_min = st.number_input("현재 최저가 (원)", min_value=0, value=def_min, step=10000000)
            with col_m3:
                man_dep = st.number_input("보증금 (원)", min_value=0, value=def_dep, step=1000000)
            with col_m4:
                man_claim = st.number_input("청구금액 (원)", min_value=0, value=def_claim, step=10000000)
            
            if st.button("입력한 가격으로 상단 수익률 즉시 업데이트"):
                if 'selected_prop' not in st.session_state or st.session_state['selected_prop'] is None:
                    st.session_state['selected_prop'] = {}
                
                st.session_state['selected_prop']['price_eval'] = man_eval
                st.session_state['selected_prop']['price_min'] = man_min
                st.session_state['selected_prop']['deposit'] = man_dep
                st.session_state['selected_prop']['claim'] = man_claim
                st.rerun()
        st.markdown("<hr>", unsafe_allow_html=True)
        # ---------------------------------------------
        st.info("AI 이미지 분석을 위해 캡처한 이미지나 문서를 붙여넣으면, GPT-4 Vision AI가 즉시 권리분석을 수행합니다.")

        uploaded_files = st.file_uploader("이미지 파일 업로드 (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        pasted_text = st.text_area("문서 텍스트 붙여넣기 (또는 권리분석 수동 입력)", height=100)

        if st.button("직접 업로드한 파일로 AI 권리분석 수행"):
            with st.spinner("Vision AI가 업로드된 문서를 읽고 있습니다... (약 10~15초 소요)"):
                b64_images = []
                if uploaded_files:
                    for uf in uploaded_files:
                        bytes_data = uf.read()
                        b64 = base64.b64encode(bytes_data).decode('utf-8')
                        b64_images.append(b64)

                st.session_state['rights_data'] = sa_engine.analyze_registry_byod(text_input=pasted_text, image_b64_list=b64_images)

        rights_data = st.session_state.get('rights_data')

        if rights_data:
            raw_registry = rights_data.get('raw_registry', '데이터 없음')
            malso = rights_data.get('malso_standard', '확인 불가')
            summary = rights_data.get('summary', '분석 실패')
            safe_status = rights_data.get('safe_status', '위험')

            # HTML로 이미지와 텍스트를 출력
            st.markdown(f"""
            <div class='registry-box'>
    {raw_registry}
            </div>
            """, unsafe_allow_html=True)

            if "독해 실패" in raw_registry or malso == "확인 불가":
                st.error("권리분석 독해 실패: 공공 데이터나 문서에서 유효한 권리 내역(말소기준 권리)을 찾지 못했습니다. 확인하신 기부 갑구/구 구문을 포함했는지 확인해 주세요.")
            else:
                diff = st.session_state.get('selected_prop', {}).get('diff', '없음')
                diff_badge = "status-green" if diff == '없음' else "status-yellow"
                st.markdown(f"<br><span class='{diff_badge}' style='font-size:14px;'>명도 이슈: {diff} | 권리 상태: {safe_status}</span>", unsafe_allow_html=True)

                st.markdown(f"""
                {summary}
                """)
                
                # --- PDF 보고서 생성 ---
                try:
                    pdf_bytes = report_generator.generate_pdf_report(
                        prop_data=st.session_state.get('selected_prop', {}),
                        analysis_result=f"[말소기준 권리: {malso}]\n{summary}\n안전여부: {safe_status}"
                    )
                    st.write("")
                    st.download_button(
                        label="📄 원클릭 임장 보고서 (PDF) 다운로드",
                        data=pdf_bytes,
                        file_name=f"임장보고서_{p.get('prop_name', '매물')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"보고서 생성 중 오류가 발생했습니다: {e}")
        else:
            st.info("이미지 또는 텍스트를 입력하고 '직접 업로드한 파일로 AI 권리분석 수행' 버튼을 눌러주세요.")

    # --------------------------------------------------------
    # STEP 4: 초정밀 투자 분석 & 수익 계산기 (상세 세팅)
    # --------------------------------------------------------
if menu == "⚖️ 권리분석 & 수익":
    with tab_calc:
        if 'selected_prop' in st.session_state and st.session_state['selected_prop']:
            p_case = st.session_state['selected_prop'].get('case_number', 'unknown')
            p_name = st.session_state['selected_prop'].get('prop_name', 'unknown')

            try:
                p_min_val = int(st.session_state['selected_prop'].get('price_min', 0) or 0)
            except (ValueError, TypeError):
                p_min_val = 0

            try:
                p_eval_val = int(st.session_state['selected_prop'].get('price_eval', 0) or 0)
            except (ValueError, TypeError):
                p_eval_val = 0

            lat = st.session_state['selected_prop'].get('lat', 37.5665)
            lon = st.session_state['selected_prop'].get('lon', 126.9780)
        else:
            p_case = "unknown"
            p_name = "unknown"
            p_min_val = 64000
            p_eval_val = 80000
            lat = 37.5665
            lon = 126.9780

        col_sim, col_note = st.columns([1, 1.2])

        with col_sim:
            st.markdown("<div class='card-title'>💰 초정밀 수익률 계산기</div>", unsafe_allow_html=True)
            st.info("세금, 부대비용 등을 모두 고려한 실 투자 수익률을 산출합니다.")

            bid_price = st.number_input("예상 입찰가 (만원)", value=p_min_val if p_min_val > 0 else 50000, step=1000, key=f"bid_{p_case}")

            st.markdown("<br><b style='color:#1E40AF;'>[1] 대출 및 레버리지 설정</b>", unsafe_allow_html=True)
            col_L1, col_L2 = st.columns(2)
            with col_L1:
                loan_amt = st.number_input("대출금 (만원)", value=int(bid_price*0.8), step=1000, key=f"loan_{p_case}")
            with col_L2:
                loan_rate = st.number_input("금융 대출금리 (%)", value=4.5, step=0.1, key=f"rate_{p_case}")

            st.markdown("<br><b style='color:#1E40AF;'>[2] 취득세 및 부대비용</b>", unsafe_allow_html=True)
            tax_rate_type = st.selectbox("취득세 부과 기준", ["무주택/1주택자 (1.1~3.5%)", "조정지역 2주택 (8.4%)", "조정지역 3주택 이상 (12.4%)"])
            if "1주택" in tax_rate_type:
                tax_rate = 0.011 if bid_price < 60000 else 0.022
            elif "8.4%" in tax_rate_type:
                tax_rate = 0.084
            else:
                tax_rate = 0.124

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                repair_cost = st.number_input("수리/명도 비용 (만원)", value=2000, step=100)
            with col_c2:
                legal_cost = st.number_input("법무/중개 등 (만원)", value=300, step=50)

            st.markdown("<br><b style='color:#1E40AF;'>[3] 임대 수익 설정</b>", unsafe_allow_html=True)
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                rent_deposit = st.number_input("받을 보증금 (만원)", value=5000, step=500, key=f"dep_{p_case}")
            with col_r2:
                rent_monthly = st.number_input("받을 월세 (만원)", value=120, step=5, key=f"mon_{p_case}")

            tax_amt = bid_price * tax_rate
            total_additional_cost = tax_amt + repair_cost + legal_cost

            monthly_interest = (loan_amt * 10000 * (loan_rate / 100)) / 12
            net_monthly_cashflow = (rent_monthly * 10000) - monthly_interest

            actual_investment = (bid_price - loan_amt - rent_deposit) + total_additional_cost 

            if actual_investment <= 0:
                yield_str = "무한대 (무피 투자 달성!)"
            else:
                annual_net_profit = net_monthly_cashflow * 12
                yield_pct = (annual_net_profit / (actual_investment * 10000)) * 100
                yield_str = f"{round(yield_pct, 2)}%"

            st.markdown(f"""
            <div style='background:#F8FAFC; border:1px solid #E2E8F0; padding:20px; border-radius:12px; font-size:15px; margin-top:15px; color:#1E293B; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);'>
            <b style='color:#334155;'>실 투자금 (Equity):</b> {int(actual_investment):,} 만원<br>
            <span style='font-size:13px; color:#64748B;'>(입찰가 - 대출 - 보증금 + 취득세 + 수리/부대비용)</span><br><br>
            <b style='color:#334155;'>매월 순수익 (Cash Flow):</b> <span style='color:#2563EB; font-size:22px; font-weight:900;'>{int(net_monthly_cashflow):,}원</span><br>
            <span style='font-size:13px; color:#64748B;'>(월세 {int(rent_monthly):,}만원 - 이자상환 {int(monthly_interest):,}원)</span><br><br>
            <b style='color:#334155;'>연 수익률 (ROI):</b> <span style='color:#EF4444; font-size:18px; font-weight:800;'>{yield_str}</span>
            </div>
            """, unsafe_allow_html=True)

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
                    <div style='border-left: 4px solid #10B981; margin-bottom:15px; background: #F8FAFC; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
                        <div style='font-style: normal; color: #1E293B; font-size: 14px; font-weight:500; line-height:1.6;'>{q}</div>
                        <div style='margin-top: 12px;'>
                            <a href='{s}' target='_blank' style='display:inline-block; background:#E2E8F0; color:#475569; padding:5px 12px; border-radius:6px; font-size:12px; font-weight:600; text-decoration:none;'>가장 가까운 매장 카카오맵 상세 보기</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("관련 인프라 정보를 찾지 못했습니다.")

            st.markdown("<div class='card-title' style='margin-top: 20px;'>커뮤니티 의견 발췌 (AI 분석/설명 자료 활용)</div>", unsafe_allow_html=True)

            reviews = []
            if 'selected_prop' in st.session_state and st.session_state['selected_prop'] is not None and sa_engine:
                with st.spinner("커뮤니티 거주기록 수집 중.."):
                    reviews = sa_engine.fetch_community_reviews(st.session_state['selected_prop']['prop_name'])

            if reviews:
                for r in reviews:
                    quote = r.get("exact_quote", "")
                    src = r.get("source", "")
                    st.markdown(f"""
                    <div style='border-left: 4px solid #3B82F6; margin-bottom:15px; background: #F8FAFC; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
                        <div style='font-style: italic; color: #1E293B; font-size: 15px; font-weight:500; line-height:1.6;'>"{quote}"</div>
                        <div style='margin-top: 12px;'>
                            <a href='{src}' target='_blank' style='display:inline-block; background:#E2E8F0; color:#475569; padding:5px 12px; border-radius:6px; font-size:12px; font-weight:600; text-decoration:none;'>원본 글 직접 확인하기 (체크)</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<div class='card-title'>📈 미래 가치 및 스트레스 테스트</div>", unsafe_allow_html=True)
        st.info("향후 5년 간의 시세 변동 예측 및 리스크를 시뮬레이션합니다.")

        col_v1, col_v2 = st.columns(2)

        with col_v1:
            # Valuation Modeling
            growth_rate = st.slider("연평균 예상 매매가 상승률 (%)", min_value=-5.0, max_value=15.0, value=3.0, step=0.5)

            import pandas as pd
            import numpy as np

            base_price = bid_price if bid_price > 0 else 50000
            years = [0, 1, 2, 3, 4, 5]

            # 보수적, 중도적, 낙관적 시나리오
            prices_base = [base_price * ((1 + (growth_rate)/100) ** y) for y in years]
            prices_optimistic = [base_price * ((1 + (growth_rate + 3)/100) ** y) for y in years]
            prices_pessimistic = [base_price * ((1 + (growth_rate - 3)/100) ** y) for y in years]

            df_future = pd.DataFrame({
                "연도": [f"{2024+y}년" for y in years],
                "예상 시세 (중립)": prices_base,
                "예상 시세 (호재반영)": prices_optimistic,
                "예상 시세 (보수적)": prices_pessimistic
            }).set_index("연도")

            st.line_chart(df_future, height=250)

        with col_v2:
            st.markdown("#### 🚨 스트레스 테스트 (금리 인상 리스크)")
            stress_rate = loan_rate + 2.0
            stress_interest = (loan_amt * 10000 * (stress_rate / 100)) / 12
            stress_cashflow = (rent_monthly * 10000) - stress_interest

            if stress_cashflow > 0:
                status_html = f"<span style='color:green; font-weight:bold;'>안전 마진 확보 (+{int(stress_cashflow):,}원)</span>"
            else:
                status_html = f"<span style='color:red; font-weight:bold;'>위험 (역마진 발생: {int(stress_cashflow):,}원)</span>"

            st.markdown(f"""
            <div style='background:rgba(239, 68, 68, 0.1); border:1px solid rgba(239, 68, 68, 0.3); padding:15px; border-radius:8px; font-size:14px; margin-top:10px;'>
            만약 금리가 <b>{stress_rate}%</b> (+2.0%p) 로 급등한다면?<br><br>
            월 이자는 <b>{int(stress_interest):,}원</b>으로 증가하며,<br>
            월 현금흐름 상태는 {status_html} 입니다.
            </div>
            """, unsafe_allow_html=True)


    # --------------------------------------------------------
if menu == "🔍 매물 딥스캔":
    with tab_redev:
        st.markdown("<div class='card-title'>전국 3대 권역 (서울/경기/지방) 재개발/재건축 토지이용계획</div>", unsafe_allow_html=True)
        st.info("**[AI 체크]** 버튼 클릭 시 해당 권역에서 많이 진행 중인 재개발/재건축 계획을 최신 데이터와 커뮤니티 리뷰 기반으로 실시간 교차 검증하여 보여줍니다.")

        st.markdown("""
        <div style='background-color:#F8FAFC; padding:15px; border-radius:10px; margin-bottom:20px; border:1px solid #E2E8F0;'>
            <div style='font-weight:bold; color:#1E2937; margin-bottom:10px; font-size:15px;'>재개발업무 진행 계획</div>
            <div style='display:flex; justify-content:space-between; align-items:center; font-size:13px; color:#94a3b8; font-weight:600;'>
                <div style='text-align:center;'>기본계획수립</div> <div>→</div>
                <div style='text-align:center;'>재개발구역지정</div> <div>→</div>
                <div style='text-align:center;'>추진위원회 승인</div> <div>→</div>
                <div style='text-align:center; color:#2563EB;'>조합설립인가</div> <div>→</div>
                <div style='text-align:center; color:#D97706;'>사업시행인가</div> <div>→</div>
                <div style='text-align:center; color:#DC2626;'>관리처분인가</div> <div>→</div>
                <div style='text-align:center;'>이주 및 철거</div> <div>→</div>
                <div style='text-align:center;'>일반분양</div> <div>→</div>
                <div style='text-align:center;'>준공 및 입주</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("전국 3대 권역 무작위 시뮬레이션 개시"):
            # 고인프라 이슈를 반영한 분석 시작 (Random Pool)
            import speedauction_engine
            with st.spinner("데이터 소스를 스캔하여 최신 재개발 구역을 추출 및 체크 중입니다... (약 20초 소요)"):
                zones = sa_engine.fetch_latest_redevelopment_zones() if sa_engine else ["서울 강남 3구역", "경기 광명 철산 11구역", "부산 해운대 우동 3구역"]

                # React DOM 에러(removeChild) 방지를 위해 컬럼 데이터를 일괄 수집
                zone_data_list = []
                for zone in zones:
                    log_agent(f"재개발 스캔 중: {zone}")
                    parsed_data = None
                    if sa_engine:
                        parsed_data = sa_engine.fetch_redevelopment_info(zone)

                    if not parsed_data: parsed_data = {}
                    zone_data_list.append((zone, parsed_data))

            # 데이터 수집이 모두 끝난 후 UI 업데이트
            cols = st.columns(3)
            for i, (zone, parsed_data) in enumerate(zone_data_list):
                with cols[i]:
                    p_status = parsed_data.get('process_status') or "데이터 스캔 중단"
                    e_date = parsed_data.get('expected_date') or "진행 상황 확인 필요"
                    e_policy = parsed_data.get('evidence_policy') or "해당 구역에 대한 최근 거래 및 정책 공공데이터를 불러오지 못했습니다."
                    e_quote = parsed_data.get('evidence_quote') or "관련 데이터가 충분하지 않아 거래 데이터를 필터링해 차단하였습니다."
                    r_reason = parsed_data.get('recommendation_reason') or "직접 현장 방문 후 추가 분석이 필요한 구역입니다."
                    news_link = parsed_data.get('news_url', '')
                    quote_link = parsed_data.get('quote_url', '')

                    st.markdown(f"<div class='premium-title' style='font-size:18px; color:#2563EB;'>📍 {zone}</div>", unsafe_allow_html=True)

                    now_str = datetime.datetime.now().strftime("%m-%d %H:%M:%S")
                    st.caption(f"🕒 **데이터 스캔 API 완료** ({now_str} 기준)")

                    st.markdown(f"<span class='status-badge' style='background:#FEF3C7; color:#92400E;'>{p_status}</span> | <span style='font-size:13px; font-weight:bold;'>예정일: {e_date}</span>", unsafe_allow_html=True)

                    st.markdown("<div class='card-title' style='font-size:14px; margin-top:15px;'>관련 법령/정책 근거</div>", unsafe_allow_html=True)

                    policy_html = f"<div style='font-size:13px; color:#94a3b8; background:rgba(30,41,59,0.6); padding:8px; border-radius:6px; margin-bottom:5px;'>{e_policy}</div>"
                    if news_link and news_link.startswith('http'):
                        policy_html += f"<div style='font-size:12px; font-weight:bold;'><a href='{news_link}' target='_blank' style='color:#2563EB; text-decoration:none;'>🔗 정책/뉴스 전문 확인하기</a></div>"
                    st.markdown(policy_html, unsafe_allow_html=True)

                    st.markdown("<div class='card-title' style='font-size:14px; margin-top:15px;'>커뮤니티 의견 인용문</div>", unsafe_allow_html=True)
                    quote_html = f"<div style='border-left: 3px solid #EF4444; padding-left:10px; font-style:italic; font-size:13px; color:#f1f5f9;'>\"{e_quote}\"</div>"
                    if quote_link and quote_link.startswith('http'):
                        quote_html += f"<div style='font-size:12px; font-weight:bold; margin-top:5px;'><a href='{quote_link}' target='_blank' style='color:#EF4444; text-decoration:none;'>🔗 커뮤니티 의견 직접 확인하기</a></div>"
                    st.markdown(quote_html, unsafe_allow_html=True)
                    st.markdown("<div class='card-title' style='font-size:14px; margin-top:15px;'>추천 이유</div>", unsafe_allow_html=True)
                    st.info(r_reason)


            # --------------------------------------------------------
    with tab_gap:
        st.markdown("<div class='card-title'>⚡ 실시간 급매 알리미 (키워드 감시)</div>", unsafe_allow_html=True)
        if st.button('🔍 실시간 급매물 스캔 가동 (무료/토큰 0원)', use_container_width=True):
            with st.spinner('대기 중인 실시간 매물 알림을 대시보드로 이동 중입니다...'):
                import subprocess
                try:
                    subprocess.run(['python', 'gap_sniper.py', '--manual'], check=True)
                    st.rerun()
                except Exception as e:
                    st.error(f'오류 발생: {e}')
        
        market_file = "market_data.json"
        market_data_list = []
        if os.path.exists(market_file):
            try:
                with open(market_file, "r", encoding="utf-8") as f:
                    market_data_list = json.load(f)
            except:
                pass
                
        if not market_data_list:
            st.warning("아직 포착된 급매물 알림이 없습니다. 스나이퍼 봇이 동작을 완료하면 데이터가 업데이트됩니다.")
        else:
            # 메트릭 표시
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("최근 감시 매물 수", f"{len(market_data_list)} 건")
            col_m2.metric("마지막 업데이트", market_data_list[0].get("date", "알 수 없음"))
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 리스트 렌더링 (Bento Grid)
            for i in range(0, len(market_data_list[:20]), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(market_data_list[:20]):
                        item = market_data_list[i + j]
                        title = item.get("title", "제목 없음")
                        body = item.get("body", "내용이 없습니다.")
                        if len(body) > 100: body = body[:100] + "..."
                        href = item.get("href", "#")
                        query = item.get("query", "키워드")
                        date = item.get("date", "")
                        
                        # Light Mode Bento Card
                        cols[j].markdown(f"""
                        <div style='background: #ffffff; border-radius: 16px; padding: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04); border: 1px solid rgba(0, 0, 0, 0.03); margin-bottom: 20px; transition: transform 0.3s, box-shadow 0.3s; display: flex; flex-direction: column; justify-content: space-between;'>
                            <div>
                                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;'>
                                    <span style='background: #fce7f3; color: #db2777; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 800; border: 1px solid #fbcfe8;'>📌 {query}</span>
                                    <span style='color: #64748b; font-size: 11px; font-weight: bold;'>{date}</span>
                                </div>
                                <h3 style='margin:0 0 15px 0; color:#1e293b; font-size:15px; font-weight:bold; line-height:1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis;'>{title}</h3>
                            </div>
                            <div style='margin-top:auto;'>
                                <a href='{href}' target='_blank' style='display:block; text-align:center; text-decoration:none; background:#f8fafc; color:#475569; padding:10px 0; border-radius:10px; font-size:13px; font-weight:bold; transition:all 0.2s; border:1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>바로가기 ➔</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    with tab_heatmap:
        st.markdown("<div class='card-title'>🔥 전국 전세가율 히트맵 (갭투자 최적지 스캔)</div>", unsafe_allow_html=True)
        
        if st.button("🔄 실시간 AI 시장 스캔 (새로고침)", use_container_width=True):
            if 'heatmap_real_data' in st.session_state:
                del st.session_state['heatmap_real_data']
        
        # 실시간 데이터 가져오기 (spinner 적용)
        heatmap_data_list = []
        import speedauction_engine
        import importlib
        importlib.reload(speedauction_engine)
                    
        if 'heatmap_real_data' not in st.session_state:
            with st.spinner("실시간 부동산 뉴스를 스캔하여 전세가율 급등 지역을 맵핑 중입니다... (약 3초 소요)"):
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
                    
                    var content = '<div style="padding:8px; background: rgba(30,41,59,0.5); color:#f8fafc; font-size:12px; border-radius:8px; font-weight:bold; box-shadow:0 2px 5px rgba(0,0,0,0.2);">' + d.title + ' (전세율 <span style="color:'+color+';">' + d.ratio + '%</span>)</div>';
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
        
        st.markdown("<div class='card-title'>🔍 팩트체크: 스캔된 전세가율 급등 지역</div>", unsafe_allow_html=True)
        if len(heatmap_data_list) > 0:
            for i in range(0, len(heatmap_data_list), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(heatmap_data_list):
                        data = heatmap_data_list[i + j]
                        ratio = data.get("ratio", 0)
                        
                        # 전세가율에 따른 동적 컬러매핑
                        if ratio >= 90:
                            color = "#EF4444"
                            bg_color = "rgba(239, 68, 68, 0.15)"
                        elif ratio >= 80:
                            color = "#F59E0B"
                            bg_color = "rgba(245, 158, 11, 0.15)"
                        else:
                            color = "#3B82F6"
                            bg_color = "rgba(59, 130, 246, 0.15)"
                            
                        cols[j].markdown(f'''
                        <div style='background: #ffffff; border-radius: 16px; padding: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04); border: 1px solid rgba(0, 0, 0, 0.03); margin-bottom: 20px; transition: transform 0.3s, box-shadow 0.3s; display: flex; flex-direction: column; justify-content: space-between;'>
                            <div>
                                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;'>
                                    <span style='background: {bg_color}; color: {color}; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 900; border: 1px solid {color}40;'>🔥 전세율 {ratio}%</span>
                                    <span style='color: #64748b; font-size: 11px; font-weight: bold;'>순위 #{i+j+1}</span>
                                </div>
                                <h3 style='margin:0 0 10px 0; color:#1e293b; font-size:15px; font-weight:bold; line-height:1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis;'>{data.get("title")}</h3>
                                <div style='color:#475569; font-size:13px; line-height:1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; margin-bottom: 15px;'>
                                    <b>💡 분석 근거:</b> {data.get("reason")}
                                </div>
                            </div>
                            <div style='margin-top:auto;'>
                                <a href='{data.get("link", "#")}' target='_blank' style='display:block; text-align:center; text-decoration:none; background:#f8fafc; color:#475569; padding:10px 0; border-radius:10px; font-size:13px; font-weight:bold; transition:all 0.2s; border:1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>팩트체크 원본 확인 ➔</a>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
        else:
            st.warning("현재 스캔된 고전세가율 지역이 없습니다.")


if menu == "💬 AI 맞춤형 비서":
    with tab_agent:
        st.markdown("<div class='premium-title' style='font-size:24px; margin-bottom:10px;'>🤖 AI 프롭테크 개인 비서 (V3.0 Beta)</div>", unsafe_allow_html=True)

        # 실시간 토큰 사용량 트래커 (OpenAI 실제 빌링 연동 기준)
        import speedauction_engine
        try:
            session_tokens = speedauction_engine.API_USAGE_TOKENS
        except:
            session_tokens = 0

        # 사용자 OpenAI 실제 데이터 반영
        import billing_db
        db_balance_krw = billing_db.get_balance()
        remain_usd = db_balance_krw / 1350.0
        used_usd = 6.00 - remain_usd
        
        # 1 달러 당 대략 50,000 토큰이라고 계산 (1센트당 500토큰)
        BASE_TOKENS = int(used_usd * 50000)
        used_tokens = BASE_TOKENS + session_tokens
        
        # 실시간 세션 토큰이 있으면 추가 차감 계산
        current_used_usd = used_usd + (session_tokens / 1000) * 0.01
        current_remain_usd = 6.00 - current_used_usd
        
        INITIAL_CREDIT = 6.00 * 1350.0  # 총 $6.00
        used_usd = current_used_usd
        remain_usd = current_remain_usd
        balance_krw = remain_usd * 1350.0
        
        remain_ratio = min(1.0, max(0.0, balance_krw / INITIAL_CREDIT)) if INITIAL_CREDIT > 0 else 0.0

        st.markdown("### 📊 실시간 API 빌링 대시보드")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.metric("소모된 토큰 (GPT-4o)", f"{used_tokens:,} 토큰", delta=f"약 {int(used_usd * 1350):,}원 사용", delta_color="inverse")
        with col_b2:
            st.metric("실제 잔액 (USD)", f"${remain_usd:.4f} (약 {int(balance_krw):,}원)", delta=f"-${used_usd:.4f}", delta_color="inverse")
        with col_b3:
            st.metric("총 결제 한도", f"${6.00:.2f} (약 {int(INITIAL_CREDIT):,}원)")

        st.progress(remain_ratio, text=f"남은 잔액 게이지: 약 {int(balance_krw):,}원 / {int(INITIAL_CREDIT):,}원")


        st.markdown('''
        <div style="background-color: #1E293B; border-left: 4px solid #38BDF8; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
            <h4 style="color: #38BDF8; margin-top: 0; font-size: 15px;">[안내] AI 비서는 언제 토큰(비용)을 소모하나요?</h4>
            <ul style="color: #CBD5E1; font-size: 13px; line-height: 1.6; margin-bottom: 0; padding-left: 20px;">
                <li><b>1. 사용자의 의도 분석 (가장 적게 소모):</b> 채팅창에 입력한 문장을 분석하여 동작을 판단할 때 (평균 100~300 토큰 / 약 1원~4원)</li>
                <li><b>2. 매물 딥스캔 & 요약:</b> 특정 지역의 물건 리스트와 상세 정보를 가져오고 정리할 때 (평균 500~1,000 토큰 / 약 7원~14원)</li>
                <li><b>3. 재개발/재건축 구역 분석:</b> 재개발 진행 단계와 호재, 커뮤니티 의견을 분석하여 답변할 때 (평균 800~1,500 토큰 / 약 11원~20원)</li>
                <li><b>4. 권리분석 및 등기부 스캔 (가장 많이 소모):</b> 등기부등본 전체를 읽거나 인프라 요약을 종합 판단할 때 (평균 1,500~3,000 토큰 이상 / 약 20원~40원 이상)</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)


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


# --------------------------------------------------------
# 탭6: 렌탈수익 & 실전 공부방 (Zero-Token)
# --------------------------------------------------------
if menu == "🎓 렌탈수익 & 실전 공부방":
    import json
    
    # DB Load
    def load_study_db():
        try:
            with open("study_db.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"vocabulary": [], "quizzes": []}
            
    study_db = load_study_db()

    with tab_study_calc:
        st.markdown("### 💰 3초 임대수익률 (월세) 계산기")
        
        c1, c2 = st.columns(2)
        with c1:
            buy_price = st.number_input("아파트/오피스텔 매매가 (만원)", value=30000, step=100)
            deposit = st.number_input("받을 보증금 (만원)", value=3000, step=100)
            monthly_rent = st.number_input("받을 월세 (만원)", value=150, step=10)
        with c2:
            loan_amount = st.number_input("대출받을 금액 (만원)", value=15000, step=100)
            loan_rate = st.number_input("대출 금리 (%)", value=5.0, step=0.1)
            acq_tax_rate = st.selectbox("취득세율 선택", ["1.1% (무주택/1주택)", "8% (다주택 중과)", "12% (3주택 이상 중과)", "4.6% (상가/오피스텔)"])
            
        tax_pct = float(acq_tax_rate.split("%")[0])
        acq_tax = int(buy_price * (tax_pct / 100.0))
        agent_fee = int(buy_price * 0.004) # 대략 0.4%
        
        real_invest = buy_price - deposit - loan_amount + acq_tax + agent_fee
        
        annual_rent = monthly_rent * 12
        annual_interest = int(loan_amount * (loan_rate / 100.0))
        net_annual_income = annual_rent - annual_interest
        net_monthly_income = int(net_annual_income / 12)
        
        yield_rate = (net_annual_income / real_invest * 100) if real_invest > 0 else 0
        
        st.divider()
        st.markdown("#### 🧾 최종 계산 영수증")
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric("내 주머니에서 나갈 [실투자금]", f"{real_invest:,} 만원", f"취득세/복비 {acq_tax+agent_fee:,}만원 포함", delta_color="inverse")
        rc2.metric("은행 이자 빼고 [순월세수익]", f"{net_monthly_income:,} 만원/월", f"연 이자 {annual_interest:,}만원 차감")
        rc3.metric("최종 [연 수익률]", f"{yield_rate:.1f} %")

    with tab_study_dict:
        st.markdown("### 📇 부동산 실전 단어장 (오프라인 DB)")
        
        search_term = st.text_input("궁금한 부동산 용어를 검색하세요 (예: DSR, 말소기준권리)")
        if search_term:
            found = False
            for v in study_db["vocabulary"]:
                if search_term.lower() in v["word"].lower():
                    st.success(f"**{v['word']}**")
                    st.info(v["explanation"])
                    found = True
            if not found:
                st.warning("단어장에 없는 용어입니다. 더 쉬운 단어로 검색해 보세요!")
        else:
            st.markdown("**자주 찾는 핵심 용어 TOP 5**")
            for v in study_db["vocabulary"][:5]:
                st.success(f"📌 **{v['word']}**")
                st.info(v["explanation"])
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    with tab_study_quiz:
        st.markdown("### 🎮 무한 AI 실전 모의고사 (안전장치 가동 중)")
        
        # 1. 고정 퀴즈 렌더링 (비용 0원)
        st.markdown("#### 📘 핵심 기출문제 (기본)")
        for i, q in enumerate(study_db["quizzes"]):
            st.info(f"**Q{i+1}. {q['question']}**")
            ans = st.radio("정답 선택:", q["options"], key=f"fixed_quiz_{i}", index=None)
            if ans:
                if ans == q["answer"]:
                    st.success("🎉 정답입니다!")
                    st.markdown(f"**[해설]** {q['explanation']}")
                else:
                    st.error("❌ 오답입니다. 다시 생각해 보세요!")
            st.divider()
        
        st.divider()
        
        # 2. 무한 AI 모의고사 생성기 (안전장치 탑재)
        st.markdown("#### 🤖 AI 무한 실전 모의고사 (심화)")
        
        if "daily_quiz_count" not in st.session_state:
            st.session_state["daily_quiz_count"] = 0
        
        st.write(f"오늘 출제 가능한 AI 퀴즈: **{10 - st.session_state['daily_quiz_count']} / 10 회**")
        
        if st.session_state["daily_quiz_count"] >= 10:
            st.error("⚠️ 요금 폭탄 방어벽 가동 중: 오늘의 무료 AI 출제 할당량(1원)을 모두 소모했습니다. 내일 다시 도전하세요!")
        else:
            if st.button("🎲 [비용 0.1원] 새로운 실전 문제 즉석 출제하기", type="primary"):
                with st.spinner("AI가 최신 트렌드를 반영한 족집게 문제를 창작 중입니다... (약 3초 소요)"):
                    try:
                        from openai import OpenAI
                        client = OpenAI()
                        
                        prompt = """
                        당신은 한국의 최고 부동산/경매 1타 강사입니다. 
                        수익형 부동산, 갭투자, 경매 권리분석, 대출(DSR 등), 세금(양도세, 취득세) 중 하나를 무작위로 골라
                        아주 실전적이고 함정이 있는 객관식 퀴즈 1개를 JSON 형태로 만들어주세요.
                        출력 형식:
                        {
                            "question": "문제 내용 (매우 구체적이고 현실적인 실전 사례)",
                            "options": ["A: ...", "B: ..."],
                            "answer": "정답 텍스트 (A 또는 B)",
                            "explanation": "사이다 같은 명쾌한 해설 (중학생도 이해 가능하게)"
                        }
                        절대 다른 말은 하지 말고 JSON만 출력하세요.
                        """
                        
                        response = client.chat.completions.create(
                            model="gpt-4o-mini", # 강제 고정 (1차 방어)
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=400, # 글자 수 물리적 차단 (2차 방어)
                            response_format={"type": "json_object"}
                        )
                        
                        raw_json = response.choices[0].message.content
                        st.session_state["current_ai_quiz"] = json.loads(raw_json)
                        st.session_state["daily_quiz_count"] += 1
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"문제 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요. ({e})")
        
        if "current_ai_quiz" in st.session_state:
            st.markdown("<br>", unsafe_allow_html=True)
            aq = st.session_state["current_ai_quiz"]
            st.info("✨ **AI가 방금 출제한 따끈따끈한 실전 문제입니다!**")
            st.markdown(f"**Q. {aq['question']}**")
            ai_ans = st.radio("정답 선택:", aq["options"], key=f"ai_quiz_radio_{st.session_state['daily_quiz_count']}", index=None)
            
            if ai_ans:
                if ai_ans == aq["answer"]:
                    st.success("🎉 정답입니다! 하산하셔도 좋습니다.")
                    st.info(f"**[1타 강사 해설]** {aq['explanation']}")
                else:
                    st.error("❌ 이런! 실전 함정에 빠지셨습니다.")
                    st.info(f"**[1타 강사 해설]** {aq['explanation']}")