import os
import urllib.request
from fpdf import FPDF
import datetime

FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
FONT_PATH = "NanumGothic.ttf"

def ensure_font():
    if not os.path.exists(FONT_PATH):
        print("Downloading Korean font for PDF generation...")
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)

def generate_pdf_report(prop_data, analysis_result=""):
    ensure_font()
    
    pdf = FPDF()
    pdf.add_page()
    
    # Add Korean font
    pdf.add_font("Nanum", "", FONT_PATH, uni=True)
    pdf.set_font("Nanum", size=24)
    
    # Header
    pdf.cell(200, 20, txt="부동산 임장 및 권리분석 보고서", ln=True, align="C")
    
    # Generation Time
    pdf.set_font("Nanum", size=10)
    pdf.set_text_color(100, 100, 100)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    pdf.cell(200, 10, txt=f"출력 일시: {now_str}", ln=True, align="R")
    
    pdf.line(10, 40, 200, 40)
    pdf.ln(10)
    
    # Property Info
    pdf.set_font("Nanum", size=16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt="1. 물건 개요", ln=True)
    
    pdf.set_font("Nanum", size=12)
    prop_name = prop_data.get('prop_name', '알 수 없음')
    case_num = prop_data.get('case_number', '알 수 없음')
    
    pdf.cell(50, 10, txt="물건명:", border=0)
    pdf.cell(140, 10, txt=str(prop_name), ln=True)
    
    pdf.cell(50, 10, txt="사건번호:", border=0)
    pdf.cell(140, 10, txt=str(case_num), ln=True)
    
    pdf.ln(10)
    
    # Price Info
    def format_price(value):
        try:
            if isinstance(value, str):
                import re
                val = re.sub(r'[^0-9]', '', value)
                if not val: return str(value)
                value = int(val)
            if value >= 10000:
                return f"{value // 10000}억 {value % 10000:,}만원" if value % 10000 != 0 else f"{value // 10000}억원"
            return f"{value:,}만원"
        except:
            return str(value)

    pdf.set_font("Nanum", size=16)
    pdf.cell(200, 10, txt="2. 가격 분석", ln=True)
    
    pdf.set_font("Nanum", size=12)
    p_eval = prop_data.get('price_eval', '정보 없음')
    p_min = prop_data.get('price_min', '정보 없음')
    
    pdf.cell(50, 10, txt="감정가:")
    pdf.cell(140, 10, txt=format_price(p_eval), ln=True)
    
    pdf.set_text_color(220, 53, 69) # Red for min price
    pdf.cell(50, 10, txt="최저 입찰가:")
    pdf.cell(140, 10, txt=format_price(p_min), ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(10)
    
    # Rights Analysis
    pdf.set_font("Nanum", size=16)
    pdf.cell(200, 10, txt="3. AI 권리분석 결과", ln=True)
    
    pdf.set_font("Nanum", size=11)
    if not analysis_result:
        analysis_result = "분석 결과가 제공되지 않았습니다."
    
    # Handle multi-line text cleanly
    pdf.multi_cell(0, 8, txt=analysis_result)
    
    pdf.ln(15)
    
    # Memo section
    pdf.set_font("Nanum", size=16)
    pdf.cell(200, 10, txt="4. 임장 메모 (현장 조사 체크리스트)", ln=True)
    pdf.set_font("Nanum", size=12)
    pdf.cell(200, 10, txt="[ ] 주변 환경 및 교통편 체크", ln=True)
    pdf.cell(200, 10, txt="[ ] 누수, 결로 등 건물 내부 하자 여부", ln=True)
    pdf.cell(200, 10, txt="[ ] 실제 거주자 점유 현황 및 관리비 미납액", ln=True)
    pdf.cell(200, 10, txt="[ ] 인근 부동산 방문 시세 교차검증", ln=True)
    
    # Box for notes
    pdf.rect(10, pdf.get_y() + 5, 190, 40)
    # Convert bytearray to bytes for Streamlit
    return bytes(pdf.output())
