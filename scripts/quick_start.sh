#!/bin/bash
# Скрипт быстрого старта Fanout Publisher

set -e

echo "=================================="
echo "Fanout Publisher - Quick Start"
echo "=================================="

# Проверка наличия .env
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Copying .env.example to .env..."
    cp .env.example .env
    echo ""
    echo "⚠️  ВАЖНО: Отредактируй .env файл и заполни:"
    echo "   - SERVICE_TOKEN (openssl rand -hex 32)"
    echo "   - POSTGRES_PASSWORD"
    echo "   - MINIO_SECRET_KEY"
    echo "   - TELEGRAM_API_ID (https://my.telegram.org)"
    echo "   - TELEGRAM_API_HASH (https://my.telegram.org)"
    echo "   - TELEGRAM_BOT_TOKEN (@BotFather)"
    echo "   - TELEGRAM_ADMIN_ID (твой User ID)"
    echo "   - YOUTUBE_CLIENT_ID (Google Cloud Console)"
    echo "   - YOUTUBE_CLIENT_SECRET (Google Cloud Console)"
    echo "   - YOUTUBE_REFRESH_TOKEN (запусти scripts/get_youtube_token.py)"
    echo ""
    echo "После заполнения .env запусти этот скрипт снова."
    exit 1
fi

echo "✅ .env file found"
echo ""

# Генерация SERVICE_TOKEN если не установлен
if grep -q "change_me_generate_random_token" .env; then
    echo "🔐 Generating SERVICE_TOKEN..."
    NEW_TOKEN=$(openssl rand -hex 32)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/change_me_generate_random_token/$NEW_TOKEN/g" .env
    else
        # Linux
        sed -i "s/change_me_generate_random_token/$NEW_TOKEN/g" .env
    fi
    echo "✅ SERVICE_TOKEN generated"
fi

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found! Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found! Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Запуск сервисов
echo "🚀 Starting services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready (30 seconds)..."
sleep 30

# Инициализация БД
echo ""
echo "🗄️  Initializing database..."
docker compose exec -T api python scripts/init_db.py || echo "⚠️  DB init failed, might be already initialized"

# Проверка health
echo ""
echo "🏥 Checking API health..."
curl -f http://localhost:8000/health || echo "⚠️  API health check failed"

echo ""
echo "=================================="
echo "✅ Fanout Publisher is running!"
echo "=================================="
echo ""
echo "📡 API: http://localhost:8000"
echo "📊 MinIO Console: http://localhost:9001 (minioadmin / minioadmin)"
echo "🗄️  PostgreSQL: localhost:5432 (fanout_user / <your_password>)"
echo ""
echo "📋 Next steps:"
echo "   1. Проверь логи: docker compose logs -f"
echo "   2. Получи YouTube refresh token:"
echo "      docker compose exec api python scripts/get_youtube_token.py"
echo "   3. Тестируй API:"
echo "      docker compose exec api python scripts/probe_ingest.py"
echo "   4. Найди своего бота в Telegram и отправь /start"
echo ""
echo "💡 Useful commands:"
echo "   make help           - Show all commands"
echo "   make logs           - Show all logs"
echo "   make logs-api       - Show API logs"
echo "   make logs-bot       - Show bot logs"
echo "   make test-api       - Test API"
echo "   make youtube-token  - Get YouTube token"
echo ""


