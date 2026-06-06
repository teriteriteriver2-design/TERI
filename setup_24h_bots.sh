#!/bin/bash

echo "================================================="
echo "🚀 24시간 백그라운드 봇 자동 실행기 설정 (Crontab)"
echo "================================================="

# 작업 디렉토리 설정
WORK_DIR="$HOME/TERI"

# 크론탭(crontab)에 등록할 명령어들
CRON_SNIPER="@reboot cd $WORK_DIR && nohup python3 gap_sniper.py > sniper.log 2>&1 &"
CRON_TELEGRAM="@reboot cd $WORK_DIR && nohup python3 telegram_interactive_bot.py > telegram_bot.log 2>&1 &"
CRON_ALERT="@reboot cd $WORK_DIR && nohup python3 alert_server.py > alert_bot.log 2>&1 &"

# 기존 크론탭 백업 및 임시 파일 생성
crontab -l > mycron 2>/dev/null || true

# 스나이퍼 봇 크론 등록 (중복 방지)
if ! grep -q "gap_sniper.py" mycron; then
    echo "$CRON_SNIPER" >> mycron
    echo "✅ 스나이퍼 봇(gap_sniper.py) 자동 재시작 등록 완료"
fi

# 텔레그램 봇 크론 등록 (중복 방지)
if ! grep -q "telegram_interactive_bot.py" mycron; then
    echo "$CRON_TELEGRAM" >> mycron
    echo "✅ 텔레그램 봇(telegram_interactive_bot.py) 자동 재시작 등록 완료"
fi

# 브리핑 봇 크론 등록 (중복 방지)
if ! grep -q "alert_server.py" mycron; then
    echo "$CRON_ALERT" >> mycron
    echo "✅ 브리핑 봇(alert_server.py) 자동 재시작 등록 완료"
fi

# 새로운 크론탭 적용
crontab mycron
rm mycron

echo "================================================="
echo "🎉 설정 완료! 이제 서버가 껐다 켜져도 봇들이 자동으로 부활합니다."
echo "지금 바로 봇들을 백그라운드에서 다시 실행합니다..."

# 지금 당장 봇들을 실행
pkill -f "gap_sniper.py"
pkill -f "telegram_interactive_bot.py"
pkill -f "alert_server.py"

cd $WORK_DIR
nohup python3 gap_sniper.py > sniper.log 2>&1 &
nohup python3 telegram_interactive_bot.py > telegram_bot.log 2>&1 &
nohup python3 alert_server.py > alert_bot.log 2>&1 &

echo "✅ 3개의 봇(스나이퍼, 텔레그램, 브리핑)이 정상적으로 백그라운드 가동을 시작했습니다!"
