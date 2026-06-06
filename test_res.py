import speedauction_engine as sa

engine = sa.SpeedAuctionEngine()
news_context = "테스트 뉴스"
prompt = f'''You are a Korean real estate expert. Based on the following REAL-TIME NEWS DATA, identify exactly 4 specific neighborhoods (Gu and Dong) in South Korea where the 'Jeonse' (Key money deposit) ratio is exceptionally high (over 80%) or rapidly rising.

REAL-TIME NEWS:
{news_context}

Return a JSON array of objects. Each object must have:
- "lat": latitude (float, approximate center of the neighborhood)
- "lon": longitude (float, approximate center of the neighborhood)
- "title": string (e.g. "강서구 화곡동")
- "ratio": integer between 80 and 99 (infer from news, or estimate reasonably > 80)
- "reason": string (Short factual evidence from the news explaining WHY the ratio is high here)
- "link": string (The exact LINK from the news data that supports this. If not explicitly found, use the most relevant news link)
Output ONLY the valid JSON array without any markdown blocks.'''

res = sa.call_openai_json(prompt, "")
print('RAW RES:', res)
