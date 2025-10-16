@echo off
REM Скрипт быстрого старта Fanout Publisher для Windows

echo ==================================
echo Fanout Publisher - Quick Start
echo ==================================
echo.

REM Проверка наличия .env
if not exist .env (
    echo WARNING: .env file not found!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo ВАЖНО: Отредактируй .env файл и заполни:
    echo    - SERVICE_TOKEN (можно сгенерировать онлайн)
    echo    - POSTGRES_PASSWORD
    echo    - MINIO_SECRET_KEY
    echo    - TELEGRAM_API_ID (https://my.telegram.org)
    echo    - TELEGRAM_API_HASH (https://my.telegram.org)
    echo    - TELEGRAM_BOT_TOKEN (@BotFather)
    echo    - TELEGRAM_ADMIN_ID (твой User ID)
    echo    - YOUTUBE_CLIENT_ID (Google Cloud Console)
    echo    - YOUTUBE_CLIENT_SECRET (Google Cloud Console)
    echo    - YOUTUBE_REFRESH_TOKEN (запусти scripts/get_youtube_token.py)
    echo.
    echo После заполнения .env запусти этот скрипт снова.
    pause
    exit /b 1
)

echo ✓ .env file found
echo.

REM Проверка Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Docker not found! Please install Docker Desktop for Windows.
    pause
    exit /b 1
)

echo ✓ Docker found
echo.

REM Запуск сервисов
echo Starting services...
docker compose up -d

echo.
echo Waiting for services to be ready (30 seconds)...
timeout /t 30 /nobreak >nul

REM Инициализация БД
echo.
echo Initializing database...
docker compose exec -T api python scripts/init_db.py

REM Проверка health
echo.
echo Checking API health...
curl -f http://localhost:8000/health

echo.
echo ==================================
echo ✓ Fanout Publisher is running!
echo ==================================
echo.
echo API: http://localhost:8000
echo MinIO Console: http://localhost:9001 (minioadmin / minioadmin)
echo PostgreSQL: localhost:5432 (fanout_user / your_password)
echo.
echo Next steps:
echo    1. Проверь логи: docker compose logs -f
echo    2. Получи YouTube refresh token:
echo       docker compose exec api python scripts/get_youtube_token.py
echo    3. Тестируй API:
echo       docker compose exec api python scripts/probe_ingest.py
echo    4. Найди своего бота в Telegram и отправь /start
echo.
pause


