import codecs

bat_content = """@echo off
title TERI 실시간 급매 스나이퍼 봇
echo ==============================================
echo [TERI 급매 스나이퍼 가동 중...]
echo 10분마다 자동으로 네이버 카페와 블로그를 감시합니다.
echo 이 창을 켜두시면 봇이 계속 작동합니다. (최소화 해두셔도 됩니다)
echo ==============================================
set PYTHONUTF8=1
cd /d "%~dp0"

:loop
echo.
echo [%time%] 스나이퍼 봇 스캔을 시작합니다...
py gap_sniper.py
echo ==============================================
echo 10분(600초) 대기 중... 다음 스캔을 기다립니다.
timeout /t 600 /nobreak
goto loop
"""

# Save as CP949 WITHOUT chcp 65001, so it matches the native Korean CMD
with codecs.open('start_sniper.bat', 'w', 'cp949') as f:
    f.write(bat_content)

print("start_sniper.bat saved with CP949 encoding (chcp removed).")
