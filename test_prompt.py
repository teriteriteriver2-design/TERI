import speedauction_engine as sa

prompt = """
You are a Korean real estate expert. Identify exactly 4 specific neighborhoods (Gu and Dong) in South Korea where the 'Jeonse' (Key money deposit) ratio compared to the sale price is exceptionally high (over 80%) based on actual recent data (e.g., Gangseo-gu, Hwaseong-si, etc.).
Return a JSON array of objects. Each object must have:
- "lat": latitude (float)
- "lon": longitude (float)
- "title": string (e.g. "강서구 화곡동")
- "ratio": integer between 80 and 99
- "reason": string (Short 1-2 sentence factual evidence explaining WHY the ratio is high here, e.g. "최근 전세사기 여파로 매매가가 하락하며 전세가율이 90%에 육박하고 있습니다.")
Output ONLY the valid JSON array without any markdown blocks.
"""

print(sa.call_openai_json(prompt, ""))
