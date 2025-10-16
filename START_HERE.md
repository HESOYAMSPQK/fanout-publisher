# 🚀 НАЧНИ ОТСЮДА - Fanout Publisher

## ✅ Что уже сделано

Полностью рабочий сервис для автоматической публикации видео на YouTube Shorts через Telegram-бота!

### 📦 Созданные компоненты:

✅ **FastAPI API** - REST API с endpoints:
- `POST /ingest` - приём видео на публикацию
- `GET /status/{id}` - проверка статуса
- `POST /retry_failed/{id}` - повтор неудавшихся
- `GET /health` - health check

✅ **Telegram Bot** - полнофункциональный бот:
- Приём видео (файлы до 2 ГБ через локальный Bot API)
- Запрос описания
- Отправка в API
- Уведомления о статусе публикации

✅ **YouTube адаптер** - рабочая интеграция:
- OAuth2 авторизация
- Resumable upload
- Retry с exponential backoff
- Обработка ошибок

✅ **Celery Workers** - асинхронная обработка:
- Скачивание из MinIO
- Публикация на платформы
- Обновление статусов
- Retry логика

✅ **Docker Compose** - полная инфраструктура:
- PostgreSQL (БД)
- Redis (очереди)
- MinIO (хранилище видео)
- Локальный Telegram Bot API
- API, Worker, Bot

✅ **Скрипты** - вспомогательные инструменты:
- Инициализация БД
- Получение YouTube refresh token
- Тестирование API
- Тестирование YouTube upload

✅ **Документация**:
- README.md - основная документация
- SETUP_GUIDE.md - пошаговая инструкция
- QUICK_START_COMMANDS.md - все команды
- PLATFORMS_ROADMAP.md - план других платформ

---

## ⚡ Быстрый старт (3 шага)

### 1️⃣ Настрой .env

```bash
# Linux/Mac
cp .env.example .env
nano .env

# Windows
copy .env.example .env
notepad .env
```

**Заполни обязательные переменные:**
- `SERVICE_TOKEN` - сгенерируй: `openssl rand -hex 32`
- `POSTGRES_PASSWORD` - придумай пароль
- `MINIO_SECRET_KEY` - придумай пароль
- `TELEGRAM_API_ID` + `TELEGRAM_API_HASH` - получи на https://my.telegram.org
- `TELEGRAM_BOT_TOKEN` - получи у @BotFather
- `TELEGRAM_ADMIN_ID` - твой User ID (@userinfobot)
- `YOUTUBE_CLIENT_ID` + `YOUTUBE_CLIENT_SECRET` - Google Cloud Console
- `YOUTUBE_REFRESH_TOKEN` - получишь на шаге 3

### 2️⃣ Запусти сервисы

```bash
# Автоматически (рекомендуется)
# Linux/Mac:
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh

# Windows:
scripts\quick_start.bat

# Или вручную:
docker compose up -d
docker compose exec api python scripts/init_db.py
```

### 3️⃣ Получи YouTube token

```bash
docker compose exec api python scripts/get_youtube_token.py
# Открой ссылку в браузере → разреши доступ → скопируй токен
# Добавь YOUTUBE_REFRESH_TOKEN в .env
docker compose restart worker bot
```

---

## 🎯 Проверка работы

### 1. Проверь API:
```bash
curl http://localhost:8000/health
```

### 2. Проверь бота:
- Найди бота в Telegram (username из @BotFather)
- Отправь `/start`
- Отправь видео

### 3. Смотри логи:
```bash
docker compose logs -f
```

---

## 📖 Детальная документация

| Файл | Описание |
|------|----------|
| **README.md** | Полная документация проекта |
| **SETUP_GUIDE.md** | Пошаговая инструкция настройки |
| **QUICK_START_COMMANDS.md** | Все команды для копирования |
| **PLATFORMS_ROADMAP.md** | План интеграции других платформ |

---

## 🏗️ Архитектура

```
User → Telegram Bot → MinIO (видео)
                   ↓
              FastAPI API
                   ↓
              Celery Worker → YouTube API
                   ↓
              PostgreSQL (статусы)
```

**Сервисы:**
- **API:** http://localhost:8000
- **MinIO Console:** http://localhost:9001 (minioadmin / твой пароль)
- **PostgreSQL:** localhost:5432 (fanout_user / твой пароль)

---

## 📁 Структура проекта

```
fanout-publisher/
├── app/                      # FastAPI приложение
│   ├── main.py              # Главный файл с роутами
│   ├── config.py            # Конфигурация
│   ├── database.py          # Модели БД
│   └── schemas.py           # Pydantic схемы
├── bot/                     # Telegram бот
│   ├── main.py             # Главный файл бота
│   └── config.py           # Конфигурация
├── workers/                # Celery workers
│   ├── celery_app.py      # Настройка Celery
│   └── tasks_publish.py   # Задачи публикации
├── platforms/              # Адаптеры платформ
│   └── youtube.py         # YouTube адаптер
├── scripts/               # Вспомогательные скрипты
│   ├── init_db.py        # Инициализация БД
│   ├── get_youtube_token.py  # Получение YouTube token
│   ├── probe_ingest.py       # Тестирование API
│   └── test_youtube_upload.py # Тест YouTube
├── tests/                # Тесты
│   └── test_api.py
├── docker-compose.yml    # Docker Compose конфигурация
├── Dockerfile           # Docker образ
├── requirements.txt     # Python зависимости
├── .env.example        # Пример переменных окружения
└── README.md           # Документация
```

---

## 🛠️ Полезные команды

### Логи:
```bash
docker compose logs -f              # Все
docker compose logs -f api          # API
docker compose logs -f worker       # Worker
docker compose logs -f bot          # Bot
```

### Управление:
```bash
docker compose ps                   # Статус
docker compose restart              # Перезапуск
docker compose stop                 # Остановка
docker compose start                # Старт
docker compose down                 # Удаление контейнеров
```

### База данных:
```bash
# Подключение
docker compose exec postgres psql -U fanout_user -d fanout_publisher

# Внутри psql:
SELECT * FROM publish_jobs ORDER BY created_at DESC LIMIT 10;
```

### Отладка:
```bash
docker compose exec api bash        # Shell в API
docker compose exec worker bash     # Shell в Worker
docker compose exec bot bash        # Shell в Bot
```

---

## 🚦 Следующие шаги

После успешного запуска YouTube:

1. **Протестируй полный цикл:**
   - Отправь видео в бот
   - Дождись публикации
   - Проверь на YouTube

2. **Подключи другие платформы:**
   - Instagram Reels
   - TikTok
   - VK
   - См. `PLATFORMS_ROADMAP.md`

3. **Улучши систему:**
   - Добавь веб-интерфейс
   - Настрой планировщик публикаций
   - Добавь аналитику

---

## ❓ Нужна помощь?

### Где что находится:

| Вопрос | Где искать |
|--------|-----------|
| Как получить YouTube credentials? | `SETUP_GUIDE.md` → Шаг 3 |
| Как получить Telegram credentials? | `SETUP_GUIDE.md` → Шаг 2 |
| Все команды для запуска | `QUICK_START_COMMANDS.md` |
| API не работает | `QUICK_START_COMMANDS.md` → Troubleshooting |
| Планы других платформ | `PLATFORMS_ROADMAP.md` |
| Детальная архитектура | `README.md` → Архитектура |

### Типичные проблемы:

**API не запускается:**
```bash
docker compose logs api
docker compose restart api
```

**Worker не обрабатывает:**
```bash
docker compose logs worker
docker compose restart worker
```

**Бот не отвечает:**
```bash
docker compose logs bot
docker compose restart bot
```

**YouTube upload fails:**
```bash
# Получи новый refresh token
docker compose exec api python scripts/get_youtube_token.py
# Обнови .env
docker compose restart worker
```

---

## 📊 Мониторинг

### Проверка статуса всех сервисов:
```bash
docker compose ps
```

Должны быть запущены (Up):
- ✅ postgres
- ✅ redis
- ✅ minio
- ✅ telegram-bot-api
- ✅ api
- ✅ worker
- ✅ bot

### Health checks:
```bash
curl http://localhost:8000/health              # API
docker compose exec redis redis-cli ping       # Redis
docker compose exec postgres pg_isready        # PostgreSQL
curl http://localhost:9000/minio/health/live   # MinIO
```

---

## 🎉 Готово к работе!

Теперь у тебя есть:
- ✅ Полностью рабочий сервис
- ✅ Telegram бот для загрузки видео
- ✅ Интеграция с YouTube Shorts
- ✅ Асинхронная обработка через Celery
- ✅ Хранение в MinIO
- ✅ Отслеживание статусов в PostgreSQL
- ✅ Полная документация
- ✅ Тесты и скрипты

**Начни с `SETUP_GUIDE.md` для детальной настройки!**

---

## 📞 Контакты и поддержка

- GitHub Issues - для багов и предложений
- README.md - полная документация
- SETUP_GUIDE.md - детальная инструкция

---

**Удачи с публикациями! 🚀🎥**

*Создано: 2025-10-15*


