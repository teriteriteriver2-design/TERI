import sqlite3

# 1. Update billing.sqlite with the real values
DB_PATH = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/billing.sqlite'
# User has $4.49 remaining. So $4.49 * 1350 = 6061.5
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('UPDATE users SET balance_krw = ? WHERE user_id = ?', (6061.5, 'test_user_01'))
conn.commit()
conn.close()

# 2. Patch app_v2.py to use dynamic billing_db
app_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'
import re

with open(app_file, 'r', encoding='utf-8') as f:
    app = f.read()

# Pattern to find the block
pattern = r"# 사용자 OpenAI 실제 데이터 반영\s+BASE_TOKENS = \d+\s+used_tokens = BASE_TOKENS \+ session_tokens\s+# 금액 계산[^\n]+\s+INITIAL_CREDIT = 6\.00 \* 1350\.0[^\n]+\s+used_usd = \d+\.\d+ \+ \(session_tokens \/ 1000\) \* 0\.01[^\n]+\s+remain_usd = 6\.00 - used_usd"

replacement = """# 사용자 OpenAI 실제 데이터 반영
        import billing_db
        db_balance_krw = billing_db.get_balance()
        remain_usd = db_balance_krw / 1350.0
        used_usd = 6.00 - remain_usd
        
        # 1 달러 당 대략 50,000 토큰이라고 계산 (1센트당 500토큰)
        BASE_TOKENS = int(used_usd * 50000)
        used_tokens = BASE_TOKENS + session_tokens
        
        # 실시간 세션 토큰이 있으면 추가 차감 계산
        current_used_usd = used_usd + (session_tokens / 1000) * 0.01
        current_remain_usd = 6.00 - current_used_usd
        
        INITIAL_CREDIT = 6.00 * 1350.0  # 총 $6.00
        used_usd = current_used_usd
        remain_usd = current_remain_usd"""

app = re.sub(pattern, replacement, app)

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(app)

print("Dynamic billing patched!")
