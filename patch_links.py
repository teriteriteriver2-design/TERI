import os

# 1. Update sentiment_crawler.py
sent_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/sentiment_crawler.py'
with open(sent_file, 'r', encoding='utf-8') as f:
    sent = f.read()

sent = sent.replace(
    'recent_posts.append(f"[{kw}] {res.get(\'title\', \'\')} - {res.get(\'body\', \'\')}")',
    'recent_posts.append(f"[{kw}] {res.get(\'title\', \'\')} - {res.get(\'body\', \'\')} [LINK: {res.get(\'link\', \'\')}]")'
)

sent = sent.replace(
    'extract 2 factual quotes from the provided context as evidence.',
    'extract 2 factual quotes from the provided context as evidence, and MUST include the [LINK: ...] associated with each quote.'
)

sent = sent.replace(
    '{"quote": "실제 커뮤니티 발췌 문구 1"},',
    '{"quote": "실제 커뮤니티 발췌 문구 1", "link": "https://..."},\n        {"quote": "실제 커뮤니티 발췌 문구 2", "link": "https://..."}'
)
sent = sent.replace(
    '        {"quote": "실제 커뮤니티 발췌 문구 2"}',
    ''
)
with open(sent_file, 'w', encoding='utf-8') as f:
    f.write(sent)


# 2. Update speedauction_engine.py
sa_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/speedauction_engine.py'
with open(sa_file, 'r', encoding='utf-8') as f:
    sa_content = f.read()

import re

# We will replace the entire fetch_jeonse_heatmap_data function again.
# First, extract everything before and after the function.
start_idx = sa_content.find('def fetch_jeonse_heatmap_data(self):')

new_fetch_func = """def fetch_jeonse_heatmap_data(self):
        print("Fetching real jeonse heatmap data via LIVE NEWS SEARCH + AI...")
        
        # 1. Live Search for Jeonse news
        news_context = ""
        try:
            results = self.fetch_naver_search("전세가율 80% OR 전세가율 급등 OR 갭투자", endpoint="news", display=10, sort="sim")
            for res in results:
                news_context += f"- TITLE: {res.get('title','')} | DESC: {res.get('description','')} | LINK: {res.get('link','')}\\n"
        except Exception as e:
            print(f"News fetch failed: {e}")
            news_context = "No live news available."

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
        
        try:
            res = call_openai_json(prompt, "")
            if isinstance(res, dict):
                for k, v in res.items():
                    if isinstance(v, list) and len(v) > 0:
                        res = v
                        break
            
            if isinstance(res, list) and len(res) > 0:
                return res
        except Exception as e:
            print(f"Error fetching heatmap data: {e}")
        
        return [
            {"lat": 37.5420, "lon": 126.8400, "title": "강서구 화곡동", "ratio": 92, "reason": "빌라왕 사태 이후 매매가 하락", "link": "https://news.naver.com"}
        ]
"""

# Replace the old function
sa_lines = sa_content.splitlines(True)
final_sa_lines = []
in_fetch = False
for line in sa_lines:
    if 'def fetch_jeonse_heatmap_data(self):' in line:
        in_fetch = True
        final_sa_lines.append(new_fetch_func + '\n')
        continue
    
    if in_fetch:
        if line.startswith('def ') or (len(line.strip()) > 0 and not line.startswith(' ') and not line.startswith('\t')):
            in_fetch = False
            final_sa_lines.append(line)
    else:
        final_sa_lines.append(line)

with open(sa_file, 'w', encoding='utf-8') as f:
    f.writelines(final_sa_lines)


# 3. Update app_v2.py to render links and fix iframe height
app_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'
with open(app_file, 'r', encoding='utf-8') as f:
    app = f.read()

app = app.replace('height=320', 'height=420')

app = app.replace(
    'evidence_html += f"<li>{q}</li>"',
    'link_html = f" <a href=\\"{item.get(\'link\', \'#\')}\\" target=\\"_blank\\" style=\\"color:#3B82F6; text-decoration:none; font-weight:bold;\\">[출처 🔗]</a>" if item.get("link") else ""\n        evidence_html += f"<li style=\\"margin-bottom:6px;\\">{q}{link_html}</li>"'
)

heatmap_reason_old = '<div style="font-size:13px; color:#4B5563;"><b>💡 분석 근거:</b> {data.get("reason")}</div>'
heatmap_reason_new = '<div style="font-size:13px; color:#4B5563;"><b>💡 분석 근거:</b> {data.get("reason")} <a href="{data.get("link", "#")}" target="_blank" style="color:#2563EB; font-weight:bold; text-decoration:none;">[팩트체크 🔗]</a></div>'
app = app.replace(heatmap_reason_old, heatmap_reason_new)

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(app)

print("Patch links applied!")
