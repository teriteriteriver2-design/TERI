import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import json
import traceback
import sys
import os

# Add current dir to path to import speedauction_engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from speedauction_engine import call_openai_json

def fetch_market_prices(prop_name_with_size):
    """
    Fetches real estate market prices (매매 and 전세) from Naver Search using OpenAI for robust parsing.
    Example prop_name_with_size: "잠실 엘스 33평"
    Returns: {"sale_min": int(manwon), "sale_max": int, "jeonse_min": int, "jeonse_max": int, "gap": int}
    """
    enc_query = urllib.parse.quote(f"{prop_name_with_size} 아파트 시세")
    url = f"https://m.search.naver.com/search.naver?query={enc_query}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)'})
    
    result = {
        "prop_name": prop_name_with_size,
        "sale_min": 0,
        "sale_max": 0,
        "jeonse_min": 0,
        "jeonse_max": 0,
        "gap": 0,
        "source": "네이버 시세 (AI 자동추출)"
    }
    
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ')
        
        # We only need the top part of the search result where the price is
        context = text[:3000]
        
        system_prompt = """
        You are an expert real estate data extractor. 
        Read the provided Naver search result text and extract the '매매' (Sale) and '전세' (Jeonse) market prices.
        Convert the prices to '만 원' (10,000 won) integer units. 
        For example, '27억' = 270000. '9억 5,000' = 95000. '270,000' = 270000.
        If there is a range (e.g. 27억~30억), output the min and max. If it's a single price, min and max are the same.
        Output ONLY valid JSON format:
        {
            "sale_min": integer,
            "sale_max": integer,
            "jeonse_min": integer,
            "jeonse_max": integer
        }
        If you cannot find the prices, output 0 for them.
        """
        
        parsed = call_openai_json(system_prompt, context)
        
        if parsed:
            result['sale_min'] = parsed.get('sale_min', 0)
            result['sale_max'] = parsed.get('sale_max', 0)
            result['jeonse_min'] = parsed.get('jeonse_min', 0)
            result['jeonse_max'] = parsed.get('jeonse_max', 0)
            
            if result['sale_min'] > 0 and result['jeonse_min'] > 0:
                result['gap'] = result['sale_min'] - result['jeonse_min']
                
    except Exception as e:
        print(f"[fetch_market_prices] Error for {prop_name_with_size}: {e}")
        traceback.print_exc()
        
    return result

if __name__ == "__main__":
    print(json.dumps(fetch_market_prices("잠실 엘스 33평"), ensure_ascii=False, indent=2))
    print(json.dumps(fetch_market_prices("은마아파트 31평"), ensure_ascii=False, indent=2))
