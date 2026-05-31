import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import datetime

KAKAO_API_KEY = "c7a7fd72636eded70e1d45bd46b24f27"
MOLIT_API_KEY = "e4b39c3ee01ce41ebb5b53e43e90698f0f03c9a749df1cbc1d3cac766c71b6da"

def get_lawd_cd(keyword):
    try:
        enc_keyword = urllib.parse.quote(keyword)
        k_url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={enc_keyword}"
        req = urllib.request.Request(k_url, headers={"Authorization": f"KakaoAK {KAKAO_API_KEY}"})
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        
        if not data.get('documents'):
            return None, None
            
        first_doc = data['documents'][0]
        x, y = first_doc['x'], first_doc['y']
        exact_name = first_doc['place_name']
        
        coord_url = f"https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={x}&y={y}"
        req2 = urllib.request.Request(coord_url, headers={"Authorization": f"KakaoAK {KAKAO_API_KEY}"})
        res2 = json.loads(urllib.request.urlopen(req2).read().decode('utf-8'))
        
        for doc in res2['documents']:
            if doc['region_type'] == 'B': # 법정동
                return doc['code'][:5], exact_name
                
        return None, None
    except Exception as e:
        print(f"Kakao API Error: {e}")
        return None, None

def fetch_molit_transactions(lawd_cd, exact_name, api_type="trade"):
    try:
        # Check last 6 months (부동산은 거래 회전율이 낮아 6개월 치를 봐야 안전함)
        now = datetime.datetime.now()
        months_to_check = []
        for i in range(6):
            m = now.month - i
            y = now.year
            if m <= 0:
                m += 12
                y -= 1
            months_to_check.append(f"{y}{m:02d}")
        
        endpoint = "RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade" if api_type == "trade" else "RTMSDataSvcAptRent/getRTMSDataSvcAptRent"
        
        transactions = []
        for deal_ymd in months_to_check:
            # numOfRows=9999로 설정하여 누락 방지 (강남구처럼 거래량 많은 곳 대비)
            api_url = f"http://apis.data.go.kr/1613000/{endpoint}?serviceKey={MOLIT_API_KEY}&LAWD_CD={lawd_cd}&DEAL_YMD={deal_ymd}&numOfRows=9999"
            req = urllib.request.Request(api_url)
            res = urllib.request.urlopen(req)
            xml_data = res.read().decode('utf-8')
            root = ET.fromstring(xml_data)
            
            for item in root.findall(".//item"):
                apt_nm = item.find("aptNm").text if item.find("aptNm") is not None else ""
                
                import difflib
                
                # Check if name matches (fuzzy match using difflib)
                clean_apt = apt_nm.replace(" ", "").replace("아파트", "")
                clean_exact = exact_name.replace(" ", "").replace("아파트", "")
                
                # Substring match or Sequence similarity > 55%
                if clean_apt in clean_exact or clean_exact in clean_apt or difflib.SequenceMatcher(None, clean_apt, clean_exact).ratio() > 0.55:
                    amount_node = item.find("dealAmount" if api_type == "trade" else "deposit")
                    if amount_node is not None:
                        amount_str = amount_node.text.replace(",", "").strip()
                        try:
                            # amount is usually in ten-thousands (만 원)
                            amount_manwon = int(amount_str)
                            transactions.append(amount_manwon)
                        except:
                            pass
        return transactions
    except Exception as e:
        print(f"MOLIT API Error: {e}")
        return []

def get_factual_market_data(apartment_name):
    print(f"[MOLIT API] '{apartment_name}' 실거래가 추적 시작...")
    lawd_cd, exact_name = get_lawd_cd(apartment_name)
    
    if not lawd_cd:
        return {"status": "error", "message": "카카오맵에서 아파트 주소를 찾을 수 없습니다."}
        
    # Get Trade
    trades = fetch_molit_transactions(lawd_cd, exact_name, api_type="trade")
    # Get Rent (Jeonse)
    rents = fetch_molit_transactions(lawd_cd, exact_name, api_type="rent")
    
    avg_trade = sum(trades) // len(trades) if trades else 0
    avg_rent = sum(rents) // len(rents) if rents else 0
    
    return {
        "status": "success",
        "exact_name": exact_name,
        "avg_trade_manwon": avg_trade,
        "avg_jeonse_manwon": avg_rent,
        "trade_count_6m": len(trades),
        "jeonse_count_6m": len(rents)
    }

if __name__ == "__main__":
    print(get_factual_market_data("은마아파트"))
