@echo off
chcp 65001 >nul 2>&1
echo ========================================================================
echo 🔑 НАСТРОЙКА NGROK AUTHTOKEN
echo ========================================================================
echo.
echo 📋 ИНСТРУКЦИЯ:
echo.
echo 1. Откройте в браузере: https://dashboard.ngrok.com/get-started/your-authtoken
echo 2. Зарегистрируйтесь (можно через GitHub - это быстро!)
echo 3. Скопируйте ваш authtoken со страницы
echo 4. Вставьте его ниже
echo.
echo ========================================================================
echo.

set /p TOKEN="34CJQji4BFUZXlumtBBZWjWFTSy_7yyuQx6npBcPXZY88qLgc"

if "%TOKEN%"=="" (
    echo ❌ Token не может быть пустым!
    pause
    exit /b 1
)

echo.
echo ⏳ Настройка authtoken...
ngrok config add-authtoken %TOKEN%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Authtoken успешно настроен!
    echo.
    echo ========================================================================
    echo 🎉 ГОТОВО! Теперь можете запустить:
    echo    scripts\get_tiktok_token_ngrok.bat
    echo ========================================================================
) else (
    echo.
    echo ❌ Ошибка настройки authtoken
)

echo.
pause

