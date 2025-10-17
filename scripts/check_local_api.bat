@echo off
REM Скрипт для проверки настройки локального Telegram Bot API (Windows)

echo.
echo ========================================================
echo     Проверка настройки локального Bot API
echo ========================================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python с https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Проверка наличия requests
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [!] Устанавливаю библиотеку requests...
    pip install requests python-dotenv
)

REM Запуск скрипта проверки
python "%~dp0check_local_api.py"

echo.
pause

