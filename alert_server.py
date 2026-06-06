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
TARGET_REGIONS = ["전국구", "수도권", "지방 핫플레이스"]
SCAN_INTERVAL_SECONDS = 3600  # 1시간 주기로 스캔

DB_PATH = r"C:\Users\뀽제\.gemini\antigravity\scratch\teri_master.db"

def send_telegram_alert(message):
    if "여기에" in TELEGRAM_BOT_TOKEN:
        print(f"[텔레그램 대기중] 알림 전송 보류 (토큰 미입력): {message[:30]}...")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Telegram 전송 실패 (상태 코드: {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Telegram 전송 에러 (네트워크/타임아웃): {e}")

def run_background_scanner():
    print(f"🚀 [GitHub Actions 스캐너 가동 시작]")
    engine = SpeedAuctionEngine()
    
    # In a real cloud environment, we'd load alerted_cases from DB. 
    # For now, we rely on the bot sending everything it finds.
    print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 정기 AI 웹 스캔 시작...")
    
    # 1. 시황 및 핫플레이스 브리핑 수집
    print("👉 부동산 시황, 대출, 금리 뉴스 수집 중...")
    news_articles = []
    try:
        news_articles.extend(engine.fetch_naver_search("부동산 핫플레이스", endpoint="news", display=3, sort="date"))
        news_articles.extend(engine.fetch_naver_search("전국 부동산 동향", endpoint="news", display=3, sort="date"))
        news_articles.extend(engine.fetch_naver_search("대출 규제 완화 강화", endpoint="news", display=3, sort="date"))
        news_articles.extend(engine.fetch_naver_search("한국은행 주택담보대출 금리", endpoint="news", display=3, sort="date"))
        # 글로벌 매크로 지표 (미국 연준 금리 및 글로벌 경제 시황) 추가
        news_articles.extend(engine.fetch_naver_search("미국 연준 금리 글로벌 경제", endpoint="news", display=3, sort="date"))
    except Exception as e:
        print("뉴스 수집 오류:", e)
        
    from inference_engine import summarize_daily_briefing
    print("👉 AI 시황 브리핑 생성 중...")
    ai_briefing = summarize_daily_briefing(news_articles)
    
    # 2. 핵심 참고 링크 (뉴스 원본 및 유튜브)
    print("👉 참고 소스 링크 수집 중...")
    source_msg = "🔗 <b>[오늘의 핵심 참고 자료]</b>\n\n"
    
    # 뉴스 원본 링크 상위 2개
    if news_articles:
        for i, article in enumerate(news_articles[:2]):
            title = article.get('title', '').replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
            link = article.get('href', '').replace('\\', '')
            source_msg += f"📰 <b>{title[:25]}...</b>\n{link}\n\n"
            
    # 유튜브 추천 영상
    try:
        from inference_engine import search_ddg
        yt_results = search_ddg("부동산 시황 분석 site:youtube.com", max_results=1)
        if yt_results:
            yt = yt_results[0]
            yt_title = yt.get('title', '').split(' - YouTube')[0].strip()
            yt_link = yt.get('href', '').replace('\\', '')
            source_msg += f"📺 <b>[유튜브 분석 추천] {yt_title[:25]}...</b>\n{yt_link}\n"
    except Exception as e:
        print("유튜브 수집 오류:", e)
        
    # 1.5 민심 분석 추가 (사용자 요청: 오픈 API 절약을 위해 7:37 브리핑에 통합)
    print("👉 부동산 민심 분석 수집 중...")
    sentiment_msg = ""
    try:
        import sentiment_crawler
        sentiment_result = sentiment_crawler.run_sentiment_analysis()
        if sentiment_result:
            sentiment_msg = f"📊 <b>오늘의 시장 심리:</b> {sentiment_result['level']} ({sentiment_result['score']}/100)\n"
            sentiment_msg += f"🤖 <b>민심 요약:</b> {sentiment_result['summary']}\n\n"
    except Exception as e:
        print("민심 분석 수집 오류:", e)
        
    # 3. 세트 메뉴 조립 및 텔레그램 전송
    final_msg = f"🌅 <b>[TERI 일일 부동산 시황 & 민심 브리핑]</b>\n\n{sentiment_msg}{ai_briefing}\n\n======================\n\n{source_msg}"
    
    send_telegram_alert(final_msg)
    print("✅ 일일 스캔 및 브리핑 전송 완료.")
        
    print(f"✅ 일일 스캔 완료.")

def daemon_mode():
    import datetime
    import time
    kst = datetime.timezone(datetime.timedelta(hours=9))
    print("🚀 [7:37 브리핑 봇] 백그라운드 대기 모드 시작...")
    
    last_run_id = None
    
    while True:
        now = datetime.datetime.now(kst)
        current_time = now.strftime("%H:%M")
        current_id = now.strftime("%Y-%m-%d_") + current_time
        
        # 아침 8시와 저녁 8시에 실행 (중복 방지용 ID 체크)
        if current_time in ["08:00", "20:00"] and last_run_id != current_id:
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ⏰ 지정된 시간({current_time})이 되어 브리핑을 시작합니다!")
            try:
                run_background_scanner()
            except Exception as e:
                print(f"브리핑 중 오류 발생: {e}")
            last_run_id = current_id
            
        time.sleep(30) # 30초마다 시간 체크

if __name__ == "__main__":
    import sys
    if "--now" in sys.argv:
        run_background_scanner()
    else:
        daemon_mode()

