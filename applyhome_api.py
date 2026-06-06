import requests
import datetime

# 사용자 인증키 (공공데이터포털)
API_KEY = "e4b39c3ee01ce41ebb5b53e43e90698f0f03c9a749df1cbc1d3cac766c71b6da"

def fetch_applyhome_schedules():
    """한국부동산원 청약홈 분양정보 조회"""
    url = "https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail"
    params = {
        "serviceKey": API_KEY,
        "page": 1,
        "perPage": 30, # 최근 30개
    }
    schedules = []
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            items = data.get("data", [])
            for item in items:
                house_nm = item.get("HOUSE_NM", "")
                rcept_bgnde = item.get("RCEPT_BGNDE")
                
                if rcept_bgnde and len(rcept_bgnde) == 10:
                    schedules.append({
                        "date": rcept_bgnde,
                        "category": "🏢 청약홈",
                        "description": f"[접수시작] {house_nm}",
                        "is_auto": 1,
                        "is_macro": 0
                    })
                
                pr_date = item.get("PRZWNER_PRESNATN_DE")
                if pr_date and len(pr_date) == 10:
                    schedules.append({
                        "date": pr_date,
                        "category": "🎉 청약홈",
                        "description": f"[당첨발표] {house_nm}",
                        "is_auto": 1,
                        "is_macro": 0
                    })
    except Exception as e:
        print("청약홈 API 에러:", e)
    
    return schedules

def fetch_lh_schedules():
    """한국토지주택공사_분양임대공고문 조회"""
    url = "https://apis.data.go.kr/B552555/lhLeaseNoticeInfo1/lhLeaseNoticeInfo1"
    params = {
        "serviceKey": API_KEY,
        "PG_SZ": 30, # 30개
        "PAGE": 1
    }
    schedules = []
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            try:
                data = res.json()
                if len(data) > 1 and "dsList" in data[1]:
                    items = data[1]["dsList"]
                    for item in items:
                        pan_nm = item.get("PAN_NM", "")
                        nt_dt = item.get("PAN_NT_ST_DT", "")
                        
                        if nt_dt and len(nt_dt) >= 10:
                            nt_dt = nt_dt.replace(".", "-")[:10]
                            schedules.append({
                                "date": nt_dt,
                                "category": "🏗️ LH공고",
                                "description": f"[공고게시] {pan_nm}",
                                "is_auto": 1,
                                "is_macro": 0
                            })
            except:
                pass
    except Exception as e:
        print("LH API 에러:", e)
        
    return schedules

if __name__ == "__main__":
    print("--- 청약홈 ---")
    print(fetch_applyhome_schedules()[:3])
    print("--- LH ---")
    print(fetch_lh_schedules()[:3])
