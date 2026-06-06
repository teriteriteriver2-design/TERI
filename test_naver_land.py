import requests
import json

def get_naver_real_estate():
    # Example: Gangnam-gu (CortarNo: 1168000000)
    url = "https://m.land.naver.com/cluster/ajax/articleList"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://m.land.naver.com/"
    }
    # Parameters for query
    params = {
        "rletTpCd": "A01", # Apartment
        "tradTpCd": "A1", # Sale (매매)
        "z": "12",
        "lat": "37.4979",
        "lon": "127.0276",
        "btm": "37.47",
        "lft": "127.00",
        "top": "37.52",
        "rgt": "127.05",
        "cortarNo": "1168000000",
        "page": "1"
    }
    
    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        print(f"Success! Found items: {len(data.get('body', []))}")
        for item in data.get('body', [])[:3]:
            print(item.get('atclNm'), item.get('prcInfo'), item.get('tradTpNm'))
    except Exception as e:
        print("Failed:", e)

if __name__ == "__main__":
    get_naver_real_estate()
