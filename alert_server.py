import time
import requests
import sqlite3
import datetime
import sys

from speedauction_engine import SpeedAuctionEngine
from inference_engine import dynamic_enrich_data

# [사용자 설정 영역]
TELEGRAM_BOT_TOKEN = "여기에_봇_토큰을_넣어주세요"  # 예: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID = "여기에_채팅_아이디를_넣어주세요"
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
    print(f"🚀 [24/7 AI 백그라운드 스캐너 가동] 주기: {SCAN_INTERVAL_SECONDS}초")
    engine = SpeedAuctionEngine()
    
    # 이전에 알림을 보낸 사건번호 기록 (중복 알람 방지)
    alerted_cases = set()
    
    while True:
        print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 정기 AI 웹 스캔 시작...")
        
        for region in TARGET_REGIONS:
            print(f"👉 '{region}' 일대 실시간 매물 탐색 중...")
            auctions = engine.fetch_live_auctions(keyword=region, limit=3)
            
            for auc in auctions:
                case_num = auc['case_number']
                if case_num in alerted_cases:
                    continue
                
                # 새로운 매물 발견! -> 권리분석 및 심층 정보 추출
                print(f"신규 매물 발견: {case_num} ({auc['prop_name']}) - 심층 분석 시작")
                rich_data = dynamic_enrich_data(auc['prop_name'], auc)
                
                # 알림 조건 판별 (예: 안전한 물건인지 GPT가 판단한 결과)
                is_safe = False
                for r in rich_data.get('registries', []):
                    if "안전" in r.get('extinct_status', ''):
                        is_safe = True
                        break
                        
                if is_safe:
                    msg = f"🚨 <b>[새로운 우량 매물 포착]</b>\n\n"
                    msg += f"📍 <b>지역:</b> {region}\n"
                    msg += f"🏢 <b>매물명:</b> {auc['prop_name']}\n"
                    msg += f"⚖️ <b>사건번호:</b> {case_num}\n"
                    msg += f"💰 <b>감정가:</b> {auc['price_eval']}만원\n"
                    msg += f"🔥 <b>최저가:</b> {auc['price_min']}만원\n\n"
                    msg += f"💡 <b>GPT 권리분석:</b> 안전 추정 매물!\n"
                    msg += f"대시보드에서 상세 내역을 확인하세요."
                    
                    send_telegram_alert(msg)
                    alerted_cases.add(case_num)
                
            time.sleep(10) # 봇 차단 방지 딜레이
            
        print(f"✅ 스캔 완료. {SCAN_INTERVAL_SECONDS}초 후 다시 탐색합니다.")
        time.sleep(SCAN_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_background_scanner()
