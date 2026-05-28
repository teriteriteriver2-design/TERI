import urllib.request
import urllib.parse
import json

queries = ["리안", "대방동 리안", "서울특별시 동작구 대방동 리안"]

for q in queries:
    addr_url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={urllib.parse.quote(q)}"
    req = urllib.request.Request(addr_url)
    req.add_header("Authorization", "KakaoAK c7a7fd72636eded70e1d45bd46b24f27")
    try:
        addr_res = urllib.request.urlopen(req)
        if addr_res.getcode() == 200:
            addr_data = json.loads(addr_res.read().decode('utf-8'))
            if addr_data.get('documents'):
                print(f"Query '{q}': SUCCESS -> {addr_data['documents'][0]['address_name']}")
            else:
                print(f"Query '{q}': No documents found.")
        else:
            print(f"Query '{q}': HTTP {addr_res.getcode()}")
    except Exception as e:
        print(f"Query '{q}': Error {e}")
