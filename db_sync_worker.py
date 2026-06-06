import sqlite3
import time
from speedauction_engine import SpeedAuctionEngine

DB_PATH = r"C:\Users\뀽제\.gemini\antigravity\scratch\teri_master.db"

def sync_data(region="서울"):
    print(f"=== {region} 실시간 스피드옥션 데이터 동기화 시작 ===")
    engine = SpeedAuctionEngine()
    
    # 1. 라이브 매물 가져오기
    properties = engine.fetch_live_auctions(region)
    if not properties:
        print("❌ 스크래핑된 매물이 없습니다.")
        engine.close()
        return False
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 2. Properties UPSERT
    for p in properties:
        c.execute('''INSERT OR REPLACE INTO properties 
                     (case_number, prop_name, location, price_eval, price_min, status, auction_date, lat, lon) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  (p['case_number'], p['prop_name'], p['location'], p['price_eval'], p['price_min'], p['status'], p['auction_date'], p['lat'], p['lon']))
                  
        # 3. 각 매물별 권리분석 스크래핑
        tenants, registries = engine.fetch_rights_analysis(p['case_number'])
        
        # Tenants UPSERT
        for t in tenants:
            c.execute('''INSERT OR REPLACE INTO tenants 
                         (case_number, tenant_name, move_in_date, confirm_date, deposit, monthly_rent, oppose_status, payout_status)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (p['case_number'], t['tenant_name'], t['move_in_date'], t['confirm_date'], t['deposit'], t['monthly_rent'], t['oppose_status'], t['payout_status']))
                      
        # Registries UPSERT
        for r in registries:
            c.execute('''INSERT OR REPLACE INTO registries
                         (case_number, reg_type, reg_date, creditor, amount, is_malso, extinct_status)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (p['case_number'], r['reg_type'], r['reg_date'], r['creditor'], r['amount'], r['is_malso'], r['extinct_status']))
                      
    conn.commit()
    conn.close()
    engine.close()
    
    print(f"✅ 동기화 완료: 총 {len(properties)}건의 데이터가 teri_master.db에 반영되었습니다.")
    
    # 바탕화면으로 DB 동기화
    import shutil
    try:
        shutil.copy2(DB_PATH, r"C:\Users\뀽제\OneDrive\바탕 화면\teri_master.db")
        print("✅ 바탕화면 DB 덮어쓰기 완료.")
    except Exception as e:
        print(f"❌ 바탕화면 DB 복사 실패: {e}")
        
    return True

if __name__ == "__main__":
    import sys
    region = sys.argv[1] if len(sys.argv) > 1 else "서울"
    sync_data(region)
