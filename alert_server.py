import time
import requests
import sqlite3
import datetime
import sys

from speedauction_engine import SpeedAuctionEngine
from inference_engine import dynamic_enrich_data

# [사용자 설정 영역]
TELEGRAM_BOT_TOKEN = "8747565958:AAEDZOSNXyiN2ue9fpWwzpfYtJOKIzh0Hyc"
TELEGRAM_CHAT_ID = "8689260957"
TARGET_REGIONS = ["강남구", "서초구", "송파구", "관악구", "수원시"]
SCAN_INTERVAL_SECONDS = 3600  # 1시간 주기로 스캔

DB_PATH = r"C:\Users\뀽제\.gemini\antigravity\scratch\teri_master.db"

def send_telegram_alert(message):
    if "여기에" in TELEGRAM_BOT_TOKEN:
        print(f"[텔레그램 대기중] 알림 전송 보류 (토큰 미입력): {message[:30]}...")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram 전송 에러: {e}")

def run_background_scanner():
    print(f"🚀 [GitHub Actions 스캐너 가동 시작]")
    engine = SpeedAuctionEngine()
    
    # In a real cloud environment, we'd load alerted_cases from DB. 
    # For now, we rely on the bot sending everything it finds.
    print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 정기 AI 웹 스캔 시작...")
    
    # 1. 시황 및 핫플레이스 브리핑 수집
    print("👉 부동산 시황 및 핫플레이스 뉴스 수집 중...")
    news_articles = []
    try:
        news_articles.extend(engine.fetch_naver_search("부동산 핫플레이스", endpoint="news", display=5))
        news_articles.extend(engine.fetch_naver_search("서울 재개발 동향", endpoint="news", display=5))
    except Exception as e:
        print("뉴스 수집 오류:", e)
        
    from inference_engine import summarize_daily_briefing
    print("👉 AI 시황 브리핑 생성 중...")
    ai_briefing = summarize_daily_briefing(news_articles)
    
    # 2. 추천 경매 매물 1건 수집
    print("👉 오늘의 추천 경매 매물 탐색 중...")
    auction_msg = ""
    try:
        raw_blogs = engine.fetch_naver_search("전국 아파트 경매 추천 물건", endpoint="blog", display=1)
        if raw_blogs:
            b = raw_blogs[0]
            title = b.get('title', '').replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
            link = b.get('link', '')
            auction_msg += f"🚨 <b>[오늘의 전국 AI 추천 경매 물건]</b>\n"
            auction_msg += f"📍 <b>지역:</b> 전국 (인기 매물)\n"
            auction_msg += f"🏢 <b>내용:</b> {title}\n"
            auction_msg += f"🔗 <b>상세보기 링크:</b>\n{link}\n"
    except Exception as e:
        print("경매 수집 오류:", e)
        
    # 3. 세트 메뉴 조립 및 텔레그램 전송
    final_msg = f"🌅 <b>[TERI 일일 부동산 시황 브리핑]</b>\n\n{ai_briefing}\n\n======================\n\n{auction_msg}"
    
    send_telegram_alert(final_msg)
    print("✅ 일일 스캔 및 브리핑 전송 완료.")
        
    print(f"✅ 일일 스캔 완료.")

if __name__ == "__main__":
    run_background_scanner()
