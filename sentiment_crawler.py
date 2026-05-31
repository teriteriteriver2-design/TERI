import json
import time
import datetime
import os
from speedauction_engine import SpeedAuctionEngine, call_openai_json

SENTIMENT_FILE = "sentiment.json"

def run_sentiment_analysis():
    engine = SpeedAuctionEngine()
    
    # 1. 크롤링 키워드
    keywords = ["부동산 영끌", "부동산 패닉바잉", "갭투자", "부동산 폭락", "집값 하락", "청약 광풍", "집값 바닥"]
    
    recent_posts = []
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🧠 부동산 민심(FOMO/FUD) 데이터 수집 시작...")
    
    for kw in keywords:
        try:
            results = engine.fetch_naver_search(kw, endpoint="cafearticle", display=5, sort="date")
            for res in results:
                recent_posts.append(f"[{kw}] {res.get('title', '')} - {res.get('body', '')} [LINK: {res.get('href', '')}]")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error fetching {kw}: {e}")
            
    if not recent_posts:
        print("수집된 게시글이 없습니다.")
        return
        
    # 2. OpenAI 기반 감정 분석
    print("🤖 GPT-4o를 통한 부동산 시장 심리 분석 중...")
    
    prompt = """
    You are an expert real estate market sentiment analyzer. 
    Analyze the following recent community posts about real estate in South Korea.
    Determine the overall market sentiment score from 0 to 100:
    - 0-20: Extreme Fear / Panic Selling (부동산 폭락, 영끌 족 파산, 매수 심리 붕괴)
    - 21-40: Fear / Cautious (집값 하락세, 관망세 유지)
    - 41-60: Neutral (혼조세, 보합)
    - 61-80: Greed / FOMO creeping in (집값 바닥론, 갭투자 증가, 매수세 회복)
    - 81-100: Extreme Greed / Pure FOMO (영끌 광풍, 패닉 바잉, 무조건 우상향)
    
    Also provide a short 2-3 sentence summary (in Korean) of the current market mood, and extract 2 factual quotes from the provided context as evidence, and MUST include the [LINK: ...] associated with each quote.
    
    Output ONLY valid JSON:
    {
      "score": 75,
      "summary": "최근 갭투자와 집값 바닥론에 대한 언급이 늘어나며 매수 심리가 회복되고 있습니다.",
      "level": "Greed",
      "evidence": [
        {"quote": "실제 커뮤니티 발췌 문구 1", "link": "<extract EXACT link from context>"},
        {"quote": "실제 커뮤니티 발췌 문구 2", "link": "<extract EXACT link from context>"}

      ]
    }
    """
    
    context = "\n".join(recent_posts[:20]) # 최대 20개까지만 분석 (토큰 제한 방지)
    
    parsed = call_openai_json(prompt, context)
    
    if parsed and "score" in parsed:
        result = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": parsed.get("score", 50),
            "summary": parsed.get("summary", "분석 결과를 가져오지 못했습니다."),
            "level": parsed.get("level", "Neutral"),
            "evidence": parsed.get("evidence", [])
        }
        
        with open(SENTIMENT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 민심 분석 완료! 점수: {result['score']} ({result['level']})")
        print(f"요약: {result['summary']}")
    else:
        print("❌ 감정 분석 실패")

if __name__ == "__main__":
    run_sentiment_analysis()
