# 🚀 Fanout Publisher

Сервис для автоматической публикации коротких видео через Telegram-бота на различные платформы (YouTube Shorts, Instagram, TikTok и др.)

## 📋 Оглавление

- [Архитектура](#архитектура)
- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Настройка YouTube](#настройка-youtube)
- [Настройка Telegram Bot API](#настройка-telegram-bot-api)
- [Запуск и тестирование](#запуск-и-тестирование)
- [API Endpoints](#api-endpoints)
- [Roadmap: Другие платформы](#roadmap-другие-платформы)

---

## 🏗️ Архитектура

```
┌─────────────┐
│ Telegram    │
│ Bot         │─────┐
└─────────────┘     │
                    ▼
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│ Local TG    │   │   FastAPI    │   │   Celery     │
│ Bot API     │◄──│     API      │◄──│   Workers    │
└─────────────┘   └──────────────┘   └──────────────┘
                    │         │              │
                    ▼         ▼              ▼
              ┌──────────┐ ┌──────┐   ┌──────────┐
              │ MinIO/S3 │ │ Redis│   │PostgreSQL│
              └──────────┘ └──────┘   └──────────┘
                                            │
                                            ▼
                                      ┌──────────────┐
                                      │   YouTube    │
                                      │   Instagram  │
                                      │   TikTok...  │
                                      └──────────────┘
```

### Компоненты:

- **FastAPI** - REST API для приёма заявок
- **Telegram Bot** - Бот для взаимодействия с пользователями
- **Local Telegram Bot API** - Локальный сервер для работы с большими файлами (до 2 ГБ)
- **Celery Workers** - Асинхронная обработка публикаций
- **PostgreSQL** - База данных для хранения заявок
- **Redis** - Брокер сообщений для Celery
- **MinIO** - S3-совместимое хранилище для видеофайлов
- **Platform Adapters** - Адаптеры для публикации на различные платформы

---

## 📦 Требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- YouTube API credentials
- Telegram Bot Token
- Telegram API ID и API Hash

---

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
# Клонируем репозиторий
git clone <repository_url>
cd fanout-publisher

# Копируем .env.example в .env
cp .env.example .env

# Редактируем .env и заполняем необходимые значения
nano .env
```

### 2. Настройка переменных окружения

Обязательные переменные в `.env`:

```bash
# Сервисная безопасность
SERVICE_TOKEN=<сгенерируй: openssl rand -hex 32>

# PostgreSQL
POSTGRES_PASSWORD=<надежный_пароль>

# MinIO
MINIO_SECRET_KEY=<надежный_пароль>

# Telegram (см. раздел "Настройка Telegram Bot API")
TELEGRAM_API_ID=<получи на my.telegram.org>
TELEGRAM_API_HASH=<получи на my.telegram.org>
TELEGRAM_BOT_TOKEN=<получи у @BotFather>
TELEGRAM_ADMIN_ID=<твой Telegram user ID>

# YouTube (см. раздел "Настройка YouTube")
YOUTUBE_CLIENT_ID=<получи в Google Cloud Console>
YOUTUBE_CLIENT_SECRET=<получи в Google Cloud Console>
YOUTUBE_REFRESH_TOKEN=<получи через скрипт get_youtube_token.py>
```

### 3. Запуск сервисов

```bash
# Запускаем все сервисы
docker compose up -d

# Проверяем статус
docker compose ps

# Смотрим логи
docker compose logs -f
```

### 4. Инициализация базы данных

```bash
# Создаем таблицы в БД
docker compose exec api python scripts/init_db.py
```

### 5. Проверка работоспособности

```bash
# Проверяем health endpoint
curl http://localhost:8000/health

# Или используем готовый скрипт
docker compose exec api python scripts/probe_ingest.py
```

---

## 🎥 Настройка YouTube

### Шаг 1: Создание проекта в Google Cloud

1. Перейди на [Google Cloud Console](https://console.cloud.google.com/)
2. Создай новый проект или выбери существующий
3. Включи **YouTube Data API v3**:
   - APIs & Services → Enable APIs and Services
   - Найди "YouTube Data API v3"
   - Нажми "Enable"

### Шаг 2: Создание OAuth 2.0 credentials

1. APIs & Services → Credentials
2. Create Credentials → OAuth client ID
3. Application type: **Desktop app** (или Web application)
4. Название: `Fanout Publisher`
5. Authorized redirect URIs (если Web app):
   - `http://localhost:8080/`
6. Сохрани **Client ID** и **Client Secret**

### Шаг 3: Получение Refresh Token

```bash
# Запускаем скрипт для получения refresh token
docker compose exec api python scripts/get_youtube_token.py

# Или локально:
python scripts/get_youtube_token.py
```

Скрипт:
1. Откроет браузер для авторизации
2. Попросит разрешить доступ к YouTube
3. Выведет `YOUTUBE_REFRESH_TOKEN`
4. Скопируй токен в `.env`

### Шаг 4: Тестирование загрузки

```bash
# Создай тестовое видео (или используй существующее)
# Тестовая загрузка на YouTube
docker compose exec api python scripts/test_youtube_upload.py /path/to/video.mp4
```

---

## 📱 Настройка Telegram Bot API

### Шаг 1: Получение API ID и API Hash

1. Перейди на [https://my.telegram.org](https://my.telegram.org)
2. Войди с помощью своего номера телефона
3. API development tools
4. Создай новое приложение:
   - App title: `Fanout Publisher`
   - Short name: `fanout`
   - Platform: Other
5. Сохрани **api_id** и **api_hash**

### Шаг 2: Создание бота

1. Найди [@BotFather](https://t.me/BotFather) в Telegram
2. Отправь `/newbot`
3. Следуй инструкциям:
   - Название бота: `Fanout Publisher`
   - Username: `your_fanout_bot` (должен заканчиваться на `_bot`)
4. Сохрани **Bot Token**

### Шаг 3: Получение своего User ID

1. Найди [@userinfobot](https://t.me/userinfobot) в Telegram
2. Отправь `/start`
3. Скопируй свой **User ID**

### Шаг 4: Локальный Telegram Bot API

Локальный сервер уже настроен в `docker-compose.yml`. Он автоматически запускается с другими сервисами.

**Преимущества локального Bot API:**
- Работа с файлами до **2 ГБ** (вместо 20 МБ в облаке)
- Прямой доступ к файлам без повторной загрузки
- Нет лимитов на количество запросов

---

## 🔧 Запуск и тестирование

### Проверка всех сервисов

```bash
# Проверка статуса контейнеров
docker compose ps

# Логи всех сервисов
docker compose logs -f

# Логи конкретного сервиса
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f bot
```

### Тестирование API

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

#### 2. Тест POST /ingest

```bash
# Используй готовый скрипт
docker compose exec api python scripts/probe_ingest.py

# Или вручную
curl -X POST http://localhost:8000/ingest \
  -H "X-Service-Token: YOUR_SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "video_hash": "test123",
    "s3_key": "test/video.mp4",
    "file_size": 1000000,
    "duration": 30,
    "platform": "youtube",
    "title": "Test Video",
    "description": "Test Description",
    "tags": ["shorts", "test"]
  }'
```

#### 3. Проверка статуса

```bash
curl http://localhost:8000/status/<SUBMISSION_ID> \
  -H "X-Service-Token: YOUR_SERVICE_TOKEN"
```

### Тестирование бота

1. Найди своего бота в Telegram
2. Отправь `/start`
3. Отправь видео (файл или видеосообщение)
4. Введи название и описание
5. Подожди публикации

---

## 📡 API Endpoints

### GET /health

**Описание:** Health check

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-15T12:00:00",
  "service": "fanout-publisher-api"
}
```

---

### POST /ingest

**Описание:** Принять видео для публикации

**Заголовки:**
- `X-Service-Token: <token>` (обязательно)

**Тело запроса:**
```json
{
  "video_hash": "sha256_hash",
  "s3_key": "videos/user123/20251015_video.mp4",
  "file_size": 5000000,
  "duration": 30,
  "platform": "youtube",
  "title": "Мое крутое видео",
  "description": "Описание видео",
  "tags": ["shorts", "видео"],
  "telegram_user_id": "123456789",
  "telegram_message_id": "456"
}
```

**Ответ:**
```json
{
  "submission_id": "uuid-here",
  "status": "QUEUED"
}
```

---

### GET /status/{submission_id}

**Описание:** Получить статус публикации

**Заголовки:**
- `X-Service-Token: <token>` (обязательно)

**Ответ:**
```json
{
  "submission_id": "uuid-here",
  "status": "COMPLETED",
  "platform": "youtube",
  "platform_job_id": "youtube_video_id",
  "public_url": "https://youtube.com/watch?v=...",
  "error_message": null,
  "retry_count": 0,
  "created_at": "2025-10-15T12:00:00",
  "updated_at": "2025-10-15T12:05:00",
  "published_at": "2025-10-15T12:05:00"
}
```

**Статусы:**
- `PENDING` - В очереди
- `PROCESSING` - Обрабатывается
- `COMPLETED` - Опубликовано успешно
- `FAILED` - Ошибка публикации

---

### POST /retry_failed/{submission_id}

**Описание:** Повторить неудавшуюся публикацию

**Заголовки:**
- `X-Service-Token: <token>` (обязательно)

**Ответ:**
```json
{
  "submission_id": "uuid-here",
  "status": "QUEUED",
  "message": "Job re-queued for processing"
}
```

---

## 🗺️ Roadmap: Другие платформы

После успешной интеграции с YouTube Shorts, планируется подключение следующих платформ:

### ✅ YouTube Shorts
**Статус:** Реализовано  
**API:** YouTube Data API v3  
**Документация:** [YouTube API Docs](https://developers.google.com/youtube/v3)

---

### 📸 Instagram Reels

**Официальный способ:**
- **API:** Instagram Graph API (Meta)
- **Требования:**
  - Meta App (Facebook for Developers)
  - Instagram Business аккаунт
  - Access Token с правами `instagram_content_publish`
- **Лимиты:**
  - До 25 постов в сутки на аккаунт
  - Видео: до 60 секунд, до 100 МБ
  - Формат: 9:16 рекомендуется
- **Документация:** [Instagram API](https://developers.facebook.com/docs/instagram-api/)

**Альтернативы:**
- Instagrapi (неофициальная библиотека)
- ⚠️ Риск блокировки аккаунта

---

### 🎵 TikTok

**Официальный способ:**
- **API:** TikTok for Developers - Content Posting API
- **Требования:**
  - TikTok Developer Account
  - Утверждение приложения TikTok
  - OAuth 2.0 авторизация
- **Лимиты:**
  - До 5 постов в день (может меняться)
  - Видео: 3 секунды - 10 минут
  - До 287.6 МБ
- **Документация:** [TikTok API](https://developers.tiktok.com/)

**Альтернативы:**
- TikTokApi (неофициальная библиотека)
- ⚠️ Требует авторизацию через WebDriver

---

### 🔵 ВКонтакте (VK)

**Официальный способ:**
- **API:** VK API
- **Требования:**
  - VK приложение
  - Access Token с правами `video`
- **Лимиты:**
  - До 1500 запросов в сутки (зависит от прав)
  - Видео: до 5 ГБ, до 6 часов
- **Документация:** [VK API](https://dev.vk.com/method/video)

**Особенности:**
- Загрузка через `video.save` → получение `upload_url` → загрузка файла
- Поддержка Stories

---

### 🟠 Одноклассники (OK)

**Официальный способ:**
- **API:** OK REST API
- **Требования:**
  - OK приложение
  - Application Key и Access Token
- **Лимиты:**
  - Зависят от типа приложения
  - Видео: до 4 ГБ
- **Документация:** [OK API](https://apiok.ru/dev/methods/)

**Особенности:**
- Метод `video.add` для загрузки видео
- Необходима подпись запросов (MD5)

---

### 📰 Яндекс.Дзен

**Официальный способ:**
- **API:** Yandex Zen Platform API
- **Требования:**
  - Канал в Дзене
  - OAuth токен
  - Партнерская программа (для некоторых функций)
- **Лимиты:**
  - Зависят от статуса канала
  - Видео: до 10 ГБ, до 4 часов
- **Документация:** [Zen API](https://yandex.ru/dev/zen/doc/)

**Особенности:**
- Загрузка через `upload_url`
- Поддержка отложенной публикации

---

### 🐦 Twitter/X

**Официальный способ:**
- **API:** Twitter API v2
- **Требования:**
  - Twitter Developer Account
  - Elevated или Academic access для видео
  - OAuth 1.0a или OAuth 2.0
- **Лимиты:**
  - До 50 твитов в день (может меняться)
  - Видео: до 512 МБ, до 2 минуты 20 секунд
  - Формат: MP4 (H264 + AAC)
- **Документация:** [Twitter API](https://developer.twitter.com/en/docs)

**Особенности:**
- Chunked upload для видео
- INIT → APPEND → FINALIZE → Create Tweet

---

### 📺 Facebook

**Официальный способ:**
- **API:** Facebook Graph API
- **Требования:**
  - Facebook App
  - Page или User Access Token
  - Права `pages_manage_posts`, `pages_read_engagement`
- **Лимиты:**
  - До 75 постов в день на страницу
  - Видео: до 10 ГБ, до 240 минут
- **Документация:** [Facebook API](https://developers.facebook.com/docs/graph-api/)

---

### 📝 План интеграции платформ

**Milestone 1 (Реализовано):**
- ✅ YouTube Shorts

**Milestone 2 (Следующий):**
- Instagram Reels
- TikTok

**Milestone 3:**
- ВКонтакте
- Одноклассники

**Milestone 4:**
- Яндекс.Дзен
- Twitter/X
- Facebook

---

## 🛠️ Разработка

### Локальный запуск без Docker

```bash
# Создаем виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Запускаем PostgreSQL, Redis, MinIO через Docker
docker compose up -d postgres redis minio telegram-bot-api

# Инициализируем БД
python scripts/init_db.py

# Запускаем API
uvicorn app.main:app --reload

# В другом терминале - Celery worker
celery -A workers.celery_app worker --loglevel=info

# В третьем терминале - Telegram bot
python -m bot.main
```

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=app --cov=workers --cov=platforms

# Конкретный тест
pytest tests/test_api.py::test_health_check
```

---

## 📚 Структура проекта

```
fanout-publisher/
├── app/                    # FastAPI приложение
│   ├── main.py            # Главный файл с роутами
│   ├── config.py          # Конфигурация
│   ├── database.py        # Модели БД
│   └── schemas.py         # Pydantic схемы
├── bot/                   # Telegram бот
│   ├── main.py           # Главный файл бота
│   └── config.py         # Конфигурация бота
├── workers/              # Celery workers
│   ├── celery_app.py    # Конфигурация Celery
│   └── tasks_publish.py # Задачи публикации
├── platforms/            # Адаптеры платформ
│   └── youtube.py       # YouTube адаптер
├── scripts/             # Вспомогательные скрипты
│   ├── init_db.py       # Инициализация БД
│   ├── get_youtube_token.py  # Получение YouTube token
│   ├── probe_ingest.py       # Тестирование API
│   └── test_youtube_upload.py # Тест загрузки на YouTube
├── tests/               # Тесты
│   └── test_api.py
├── infra/              # Инфраструктура (будущее)
├── docker-compose.yml  # Docker Compose конфигурация
├── Dockerfile          # Dockerfile для приложения
├── requirements.txt    # Python зависимости
├── .env.example       # Пример переменных окружения
├── .gitignore
└── README.md
```

---

## 🔐 Безопасность

1. **SERVICE_TOKEN** - используется для аутентификации между ботом и API
2. Все секреты хранятся в `.env` (не коммитится в Git)
3. YouTube OAuth2 с refresh token (доступ можно отозвать в любой момент)
4. MinIO можно заменить на AWS S3 с IAM ролями

---

## 🐛 Troubleshooting

### Проблема: API не отвечает

```bash
# Проверь логи
docker compose logs api

# Проверь доступность БД
docker compose exec postgres psql -U fanout_user -d fanout_publisher -c "SELECT 1"

# Перезапусти API
docker compose restart api
```

### Проблема: Celery worker не обрабатывает задачи

```bash
# Проверь логи worker
docker compose logs worker

# Проверь очередь Redis
docker compose exec redis redis-cli KEYS "*"

# Перезапусти worker
docker compose restart worker
```

### Проблема: Telegram бот не получает файлы

```bash
# Проверь логи локального Bot API
docker compose logs telegram-bot-api

# Проверь что используется локальный API
docker compose exec bot env | grep TELEGRAM_LOCAL_API_URL

# Перезапусти бота
docker compose restart bot
```

### Проблема: Ошибка загрузки на YouTube

1. Проверь что YouTube API включен в Google Cloud Console
2. Проверь квоты API (10,000 units/day по умолчанию)
3. Проверь refresh token не истек
4. Попробуй получить новый refresh token

---

## 📄 Лицензия

MIT License

---

## 👨‍💻 Автор

Fanout Publisher Team

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## ⭐ Благодарности

- FastAPI
- python-telegram-bot
- Google YouTube API
- Celery
- MinIO


