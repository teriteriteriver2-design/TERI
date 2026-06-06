import time
import requests
import datetime
from speedauction_engine import SpeedAuctionEngine

# ==========================================
# [설정 영역]
# ==========================================
TOKEN = "8949509854:AAEvqKT0qIkTg7bmFDhUX-UfEXY9y4KwRoY" # 매물봇 (Property Bot)
CHAT_ID = "8689260957"
URL = f"https://api.telegram.org/bot{TOKEN}"

engine = SpeedAuctionEngine()

# API 과금 명령어를 위한 상태 저장소
# 예: {"8689260957": {"state": "waiting_confirmation", "action": "/민심"}}
user_states = {}

def send_telegram_msg(chat_id, text):
    try:
        requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"메시지 전송 실패: {e}")

def handle_free_search(chat_id, keyword, search_type):
    send_telegram_msg(chat_id, f"🔍 <b>'{keyword}'</b> {search_type} 정보를 실시간 무료 크롤링 중입니다... (약 5초 소요)")
    try:
        if search_type == "시세":
            # 시세는 블로그/카페 최신 글로
            results = engine.fetch_naver_search(f"{keyword} 시세 호가", endpoint="cafearticle", display=3, sort="date")
        elif search_type == "경매":
            results = engine.fetch_naver_search(f"{keyword} 경매 신건", endpoint="blog", display=3, sort="date")
        elif search_type == "뉴스":
            results = engine.fetch_naver_search(f"{keyword}", endpoint="news", display=3, sort="date")
        else:
            results = []
            
        if not results:
            send_telegram_msg(chat_id, "⚠️ 검색 결과가 없습니다.")
            return
            
        msg = f"✅ <b>[{keyword} {search_type} 검색 결과]</b> (무료)\n\n"
        for r in results:
            title = r.get("title", "").replace("<b>", "").replace("</b>", "").replace("&quot;", '"')
            link = r.get("href", "").replace("\\", "")
            desc = r.get("description", r.get("body", ""))[:60].replace("<b>", "").replace("</b>", "")
            msg += f"📰 <b>{title}</b>\n{desc}...\n🔗 {link}\n\n"
            
        send_telegram_msg(chat_id, msg)
    except Exception as e:
        send_telegram_msg(chat_id, f"❌ 검색 중 오류가 발생했습니다: {e}")

def execute_paid_action(chat_id, action):
    if action == "/민심":
        send_telegram_msg(chat_id, "🤖 [GPT-4o 가동] 인터넷 여론을 긁어모아 분석 중입니다... (약 15초 소요)")
        try:
            import sentiment_crawler
            res = sentiment_crawler.run_sentiment_analysis()
            if res:
                msg = f"📊 <b>실시간 시장 심리:</b> {res['level']} ({res['score']}/100)\n"
                msg += f"🤖 <b>AI 요약:</b> {res['summary']}\n"
                send_telegram_msg(chat_id, msg)
            else:
                send_telegram_msg(chat_id, "❌ 분석에 실패했습니다.")
        except Exception as e:
            send_telegram_msg(chat_id, f"❌ 오류 발생: {e}")

def process_message(chat_id, text):
    global user_states
    
    # 1. 상태(State) 확인 (과금 확인 대기 중인지)
    if chat_id in user_states:
        state_info = user_states[chat_id]
        if state_info["state"] == "waiting_confirmation":
            if text.strip() in ["네", "y", "yes", "응", "ㅇㅇ", "진행", "고", "go"]:
                send_telegram_msg(chat_id, "✅ 확인되었습니다. 작업을 시작합니다!")
                execute_action = state_info["action"]
                del user_states[chat_id] # 상태 초기화
                execute_paid_action(chat_id, execute_action)
            else:
                send_telegram_msg(chat_id, "🛑 작업이 취소되었습니다. (API 요금이 청구되지 않았습니다.)")
                del user_states[chat_id]
            return
            
    # 2. 새로운 명령어 처리
    text = text.strip()
    if text.startswith("/시세"):
        keyword = text.replace("/시세", "").strip()
        if not keyword:
            send_telegram_msg(chat_id, "사용법: /시세 [단지명/지역명]")
            return
        handle_free_search(chat_id, keyword, "시세")
        
    elif text.startswith("/경매"):
        keyword = text.replace("/경매", "").strip()
        if not keyword:
            send_telegram_msg(chat_id, "사용법: /경매 [지역명]")
            return
        handle_free_search(chat_id, keyword, "경매")
        
    elif text.startswith("/뉴스"):
        keyword = text.replace("/뉴스", "").strip()
        if not keyword:
            send_telegram_msg(chat_id, "사용법: /뉴스 [키워드]")
            return
        handle_free_search(chat_id, keyword, "뉴스")
        
    elif text == "/민심":
        # API 과금 경고 로직 (State Machine)
        user_states[chat_id] = {"state": "waiting_confirmation", "action": "/민심"}
        send_telegram_msg(chat_id, "⚠️ <b>[API 과금 경고]</b>\n이 명령어는 OpenAI GPT-4o를 사용하여 소량의 요금(약 10~30원)이 발생합니다.\n\n진짜로 진행하시겠습니까? (채팅창에 <b>네</b> 또는 <b>아니오</b> 를 입력해주세요)")
        
    elif text == "/업데이트":
        send_telegram_msg(chat_id, "🔄 <b>[시스템 원격 조종]</b>\n깃허브에서 최신 코드를 다운로드하고 모든 봇을 재부팅합니다...\n약 5~10초 뒤에 최신 버전이 적용됩니다!")
        
        import subprocess
        update_cmd = """
        (
        sleep 5
        git pull origin main
        chmod +x setup_24h_bots.sh
        nohup ./setup_24h_bots.sh > update_system.log 2>&1
        ) &
        """
        # 백그라운드 실행으로 스스로를 안전하게 죽이고 다시 태어나도록 세팅
        subprocess.Popen(update_cmd, shell=True)
        return
        
    elif text == "/start" or text == "/help":
        help_msg = """
🤖 <b>[TERI 24시간 양방향 비서 봇]</b>

사용 가능한 명령어:
✅ <b>/시세 [단지명]</b> : 실시간 호가/시세 검색 (무료)
✅ <b>/경매 [지역명]</b> : 신건/추천 물건 검색 (무료)
✅ <b>/뉴스 [키워드]</b> : 최신 부동산 뉴스 검색 (무료)
💰 <b>/민심</b> : AI 실시간 여론 분석 (GPT-4o 과금)
🔄 <b>/업데이트</b> : 깃허브 최신 코드 원격 패치 및 재시작

원하시는 명령어를 채팅창에 입력해 보세요!
        """
        send_telegram_msg(chat_id, help_msg)
    else:
        send_telegram_msg(chat_id, "🤔 알 수 없는 명령어입니다. '/help'를 입력해 보세요.")


def main():
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 텔레그램 양방향 수신 봇 가동 시작...")
    last_update_id = 0
    
    while True:
        try:
            req_url = f"{URL}/getUpdates?offset={last_update_id + 1}&timeout=30"
            resp = requests.get(req_url, timeout=35).json()
            
            if resp.get("ok"):
                for result in resp.get("result", []):
                    last_update_id = result["update_id"]
                    msg = result.get("message", {})
                    chat_id = str(msg.get("chat", {}).get("id", ""))
                    text = msg.get("text", "")
                    
                    if not text:
                        continue
                        
                    # 강력한 보안 검증 (사장님 외 원천 차단)
                    if chat_id != CHAT_ID:
                        send_telegram_msg(chat_id, "🛑 접근 권한이 없습니다. (Access Denied)")
                        print(f"⚠️ [보안] 허가되지 않은 사용자 접근 시도: {chat_id}")
                        continue
                        
                    print(f"📥 [수신] {text}")
                    process_message(chat_id, text)
                    
        except Exception as e:
            # 타임아웃 또는 인터넷 끊김 시 무시하고 재시도
            pass
            
        time.sleep(1)

if __name__ == "__main__":
    main()
