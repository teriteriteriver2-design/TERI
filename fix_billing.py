import os

app_file = 'C:/Users/뀽제/OneDrive/바탕 화면/BU/app_v2.py'
with open(app_file, 'r', encoding='utf-8') as f:
    app = f.read()

# 1. Update hardcoded billing details
billing_old = """
        # 사용자 OpenAI 실제 데이터 반영
        BASE_TOKENS = 48852
        used_tokens = BASE_TOKENS + session_tokens

        # 금액 계산 ($1.20 = 1620원 사용 / 잔액 $4.80 = 6480원)
        INITIAL_CREDIT = 6.00 * 1350.0  # 총 $6.00
        used_usd = 1.20 + (session_tokens / 1000) * 0.01  # 실시간 추가분 포함
        remain_usd = 6.00 - used_usd
"""
billing_new = """
        # 사용자 OpenAI 실제 데이터 반영
        BASE_TOKENS = 74400
        used_tokens = BASE_TOKENS + session_tokens

        # 금액 계산 ($1.49 = 2011원 사용 / 잔액 $4.51 = 6088원)
        INITIAL_CREDIT = 6.00 * 1350.0  # 총 $6.00
        used_usd = 1.49 + (session_tokens / 1000) * 0.01  # 실시간 추가분 포함
        remain_usd = 6.00 - used_usd
"""
app = app.replace(billing_old, billing_new)

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(app)

print("Billing patched")
