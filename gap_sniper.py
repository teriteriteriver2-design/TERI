import time
import os
import datetime
from speedauction_engine import SpeedAuctionEngine
from alert_server import send_telegram_alert

HISTORY_FILE = "sniper_history.txt"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_history(href):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{href}\n")

def run_sniper():
    engine = SpeedAuctionEngine()
    history = load_history()
    
    # 사용자 요청 키워드 목록
    keywords = ["급매", "우량", "재개발", "재건축", "꿀매물", "급상승", "인기", "핫플", "갭투자"]
    queries = [f"아파트 {k}" for k in keywords] + [f"부동산 {k}" for k in keywords]
    
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚡ 스나이퍼 봇 감시 시작... (타겟: 전국 아파트/부동산)")
    
    new_alerts = []
    
    for query in queries:
        # 카페 및 블로그에서 최신순(date)으로 수집
        for endpoint in ["cafearticle", "blog"]:
            try:
                results = engine.fetch_naver_search(query, endpoint=endpoint, display=3, sort="date")
                for res in results:
                    href = res.get("href", "").replace("\\", "")
                    title = res.get("title", "")
                    body = res.get("body", "")
                    source = res.get("source_name", endpoint)
                    
                    if href and href not in history:
                        # 스팸 필터링 로직 (광고나 무관한 글 거르기)
                        if "중고차" in title or "노트북" in title:
                            continue
                            
                        # 새로운 알람 발견
                        msg = f"🚨 <b>[급매/갭투자 스나이퍼 포착!]</b>\n"
                        msg += f"📍 <b>검색어:</b> {query}\n"
                        msg += f"📰 <b>제목:</b> {title[:40]}...\n"
                        msg += f"📝 <b>요약:</b> {body[:60]}...\n"
                        msg += f"🔗 <b>바로가기:</b>\n{href}\n"
                        
                        new_alerts.append(msg)
                        history.add(href)
                        save_history(href)
            except Exception as e:
                print(f"Error fetching {query} on {endpoint}: {e}")
                
            time.sleep(0.5) # API Rate limit 보호
            
    # 새로운 알람이 있으면 텔레그램 전송
    if new_alerts:
        print(f"🔥 총 {len(new_alerts)}건의 새로운 급매물 포착! 텔레그램 전송 중...")
        # 너무 많으면 상위 5개만 전송하여 스팸 방지
        for alert_msg in new_alerts[:5]:
            send_telegram_alert(alert_msg)
            time.sleep(1) # 텔레그램 도배 방지
    else:
        print("👀 새로 올라온 급매물이 없습니다. 10분 뒤 다시 감시합니다.")

if __name__ == "__main__":
    # 처음 실행 시 바로 한 번 스캔하고, 이후 10분마다 스캔
    while True:
        try:
            run_sniper()
        except Exception as e:
            print("Sniper Error:", e)
        
        # 10분(600초) 대기
        time.sleep(600)
