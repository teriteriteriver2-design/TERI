@echo off
title TERI Sniper Bot
echo ==============================================
echo [TERI Sniper Bot Running...]
echo Scanning every 10 minutes for properties.
echo Leave this window open to keep the bot active.
echo ==============================================
set PYTHONUTF8=1
cd /d "%~dp0"

:loop
echo.
echo [%time%] Starting Sniper Bot Scan...
py gap_sniper.py
echo ==============================================
echo Waiting for 10 minutes (600 seconds)...
timeout /t 600 /nobreak
goto loop
