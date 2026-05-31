import time
import os
import sys
import argparse
import datetime
import requests
import json
import report_generator
from speedauction_engine import SpeedAuctionEngine, call_openai_json
from molit_api import get_factual_market_data

HISTORY_FILE = "sniper_history.txt"
MARKET_DATA_FILE = "market_data.json"
PENDING_FILE = "pending_analysis.json"
SNIPER_BOT_TOKEN = "8949509854:AAEvqKT0qIkTg7bmFDhUX-UfEXY9y4KwRoY"
TELEGRAM_CHAT_ID = "8689260957"

def send_sniper_telegram_alert(message):
    url = f"https://api.telegram.org/bot{SNIPER_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram 전송 에러: {e}")

def send_sniper_telegram_pdf(message, pdf_bytes, filename):
    url = f"https://api.telegram.org/bot{SNIPER_BOT_TOKEN}/sendDocument"
    files = {"document": (filename, pdf_bytes, "application/pdf")}
    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data, files=files, timeout=10)
    except Exception as e:
        print(f"Telegram PDF 전송 에러: {e}")

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_history(href):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{href}\n")

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_apartment_and_price(title, body):
    system_prompt = """
    You are a real estate parser extracting facts from a Korean cafe post.
    Given the post title and body, extract:
    1. prop_name: Exact apartment name (e.g. '은마아파트', '잠실엘스'). Do NOT include size (평수). If not found, return empty string.
    2. asking_price_manwon: The exact asking price (매매 호가/급매가) listed in the text, converted to 만원 (integer). If 8억 5천 -> 85000. If no price is explicitly stated, return 0.
    3. exact_quote: The EXACT sentence from the text that proves the asking price. If no price, return '가격 정보 없음'.

    Output ONLY valid JSON: 
    {
        "prop_name": "extracted name",
        "asking_price_manwon": 0,
        "exact_quote": "증거 문장"
    }
    """
    parsed = call_openai_json(system_prompt, title + " " + body)
    if parsed:
        return parsed
    return {"prop_name": "", "asking_price_manwon": 0, "exact_quote": "추출 실패"}

def run_sniper(manual_mode=False):
    history = load_history()
    market_data_list = load_json(MARKET_DATA_FILE)
    pending_list = load_json(PENDING_FILE)
    
    if manual_mode:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 [수동 모드] 대기 중인 매물 AI 갭투자 분석 시작...")
        if not pending_list:
            print("대기 중인 매물이 없습니다!")
            return
            
        new_alerts = []
        for item in pending_list:
            title = item.get("title", "")
            body = item.get("body", "")
            href = item.get("href", "")
            query = item.get("query", "")
            
            print(f"분석 중: {title}")
            extracted = extract_apartment_and_price(title, body)
            prop_name = extracted.get("prop_name", "")
            asking_price = extracted.get("asking_price_manwon", 0)
            exact_quote = extracted.get("exact_quote", "정보 없음")
            
            molit_data = None
            if prop_name and len(prop_name) > 1:
                molit_data = get_factual_market_data(prop_name)
                
            msg = f"🚨 <b>[수동 AI 팩트 분석 - 갭투자 스나이퍼!]</b>\n"
            msg += f"📍 <b>검색어:</b> {query}\n"
            
            if prop_name and asking_price > 0:
                msg += f"🏢 <b>단지명:</b> {prop_name}\n"
                msg += f"💰 <b>카페 급매 호가:</b> {asking_price:,}만원\n"
                msg += f"🔎 <b>증거 문장:</b> <i>\"{exact_quote}\"</i>\n"
                
                if molit_data and molit_data.get("status") == "success" and molit_data.get("avg_jeonse_manwon", 0) > 0:
                    jeonse_price = molit_data['avg_jeonse_manwon']
                    gap = asking_price - jeonse_price
                    msg += f"🛡️ <b>[국토교통부 팩트] 최근 전세 실거래:</b> {jeonse_price:,}만원\n"
                    msg += f"🔥 <b>필요 갭(투자금):</b> {gap:,}만원\n"
                    
                    # Dashboard integration format
                    market_info = {
                        "prop_name": prop_name,
                        "sale_min": asking_price,
                        "jeonse_min": jeonse_price,
                        "gap": gap,
                        "exact_quote": exact_quote
                    }
                    market_data_list.insert(0, {
                        "title": title,
                        "href": href,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "market_info": market_info
                    })
                else:
                    msg += f"⚠️ <b>전세 데이터 확인 불가</b> (국토부 실거래가 검색 실패)\n"
                    
            else:
                msg += f"📰 <b>제목:</b> {title[:40]}...\n"
                msg += f"⚠️ 명확한 가격 정보나 아파트 이름을 찾을 수 없습니다.\n"
                
            msg += f"🔗 <b>원본 글 바로가기:</b>\n{href}\n"
            new_alerts.append((msg, title))
            
        # 유지: 최근 50개만 저장
        market_data_list = market_data_list[:50]
        save_json(MARKET_DATA_FILE, market_data_list)
        
        # 분석이 끝났으므로 대기열 비우기
        save_json(PENDING_FILE, [])
        
        for alert_msg, alert_title in new_alerts[:5]:
            try:
                prop_data = {"prop_name": alert_title, "sell_price": "정보없음", "jeonse_price": "정보없음", "address": "확인필요"}
                pdf_bytes = report_generator.generate_pdf_report(prop_data, "수동 AI 갭투자 분석 보고서입니다.")
                send_sniper_telegram_pdf(alert_msg, pdf_bytes, f"임장보고서_{alert_title[:10]}.pdf")
            except:
                send_sniper_telegram_alert(alert_msg)
            time.sleep(1)
            
        print("수동 AI 분석 및 전송 완료!")
        
    else:
        # 백그라운드 무지성 감시 모드
        engine = SpeedAuctionEngine()
        apt_keywords = ["급매", "우량", "재개발", "재건축", "꿀매물", "급상승", "인기", "핫플", "갭투자", "초급매", "초우량", "초핫딜", "역세권", "입지"]
        general_keywords = ["상권", "빌라", "주택", "전원주택 마당", "전원주택"]
        queries = [f"아파트 {k}" for k in apt_keywords] + [f"부동산 {k}" for k in apt_keywords + general_keywords]
        
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚡ [자동 모드] 무지성 스나이퍼 감시 시작... 토큰 사용 안함!")
        
        found_new = False
        for query in queries:
            for endpoint in ["cafearticle", "blog"]:
                try:
                    results = engine.fetch_naver_search(query, endpoint=endpoint, display=3, sort="date")
                    for res in results:
                        href = res.get("href", "").replace("\\", "")
                        title = res.get("title", "")
                        body = res.get("body", "")
                        
                        if href and href not in history:
                            if "중고차" in title or "노트북" in title:
                                continue
                                
                            pending_list.append({
                                "query": query,
                                "title": title,
                                "body": body,
                                "href": href
                            })
                            history.add(href)
                            save_history(href)
                            found_new = True
                            
                            # 방금 찾은 알람 내역만 모으기 (텔레그램 도배 방지)
                            if len(pending_list) <= 10: # 최대 10개까지만 알람 전송
                                msg = f"🚨 <b>[자동 감시 - 새 매물 발견!]</b>\n"
                                msg += f"📍 <b>검색어:</b> {query}\n"
                                msg += f"📰 <b>제목:</b> {title[:40]}...\n"
                                msg += f"🔗 <b>바로가기:</b>\n{href}\n"
                                msg += f"💡 <i>대시보드에서 [수동 가동 버튼]을 누르시면 AI가 분석해드립니다!</i>"
                                send_sniper_telegram_alert(msg)
                            elif len(pending_list) == 11:
                                send_sniper_telegram_alert("⚠️ <b>새로운 매물이 너무 많습니다! (10개 초과)</b>\n나머지는 텔레그램 도배 방지를 위해 알람을 생략했습니다. 대시보드에서 [수동 가동]을 눌러 확인하세요!")
                            
                except Exception as e:
                    print(f"Error: {e}")
                time.sleep(0.5)
                
        if found_new:
            save_json(PENDING_FILE, pending_list)
        else:
            print("새로운 매물이 없습니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual", action="store_true", help="수동 AI 분석 모드")
    args = parser.parse_args()
    
    try:
        run_sniper(manual_mode=args.manual)
    except Exception as e:
        print("Sniper Error:", e)
