@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0\.."
python scripts\get_tiktok_token_ngrok.py
echo.
echo.
pause

