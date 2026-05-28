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
    
    for region in TARGET_REGIONS:
        print(f"👉 '{region}' 일대 실시간 매물 탐색 중...")
        # Simulating fetch
        try:
            raw_blogs = engine.fetch_naver_search(f"{region} 경매 신건", endpoint="blog", display=3)
            
            for b in raw_blogs:
                title = b.get('title', '').replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                desc = b.get('description', '').replace('<b>', '').replace('</b>', '')
                link = b.get('link', '')
                
                msg = f"🚨 <b>[새로운 경매 물건 포착]</b>\n\n"
                msg += f"📍 <b>지역:</b> {region}\n"
                msg += f"🏢 <b>내용:</b> {title}\n"
                msg += f"🔗 <a href='{link}'>상세보기 링크</a>\n\n"
                msg += f"💡 대시보드에서 상세 내역을 확인하세요."
                
                send_telegram_alert(msg)
                
        except Exception as e:
            print(f"[{region}] 스캔 오류: {e}")
            
        time.sleep(2) # 봇 차단 방지 딜레이
        
    print(f"✅ 일일 스캔 완료.")

if __name__ == "__main__":
    run_background_scanner()
