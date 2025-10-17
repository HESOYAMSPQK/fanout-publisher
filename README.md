# 🚀 Fanout Publisher - Web Version

> Автоматическая загрузка видео на YouTube через удобный веб-интерфейс

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com)

## 📖 О проекте

**Fanout Publisher** — это веб-приложение для автоматической публикации видео на различные платформы. Просто загрузите видео через браузер, и оно автоматически опубликуется на выбранной платформе!

### 🎯 Поддерживаемые платформы

- ✅ **YouTube** - полная поддержка (публичное/приватное/по ссылке)
- ✅ **VK (ВКонтакте)** - загрузка видео и клипов (публичное/приватное)
- ✅ **TikTok** - Content Posting API (приватное/публичное, требует VPN для РФ)

### ✨ Возможности

- 🎨 **Современный веб-интерфейс** — красивый UI для работы с видео
- 🌐 **Мультиплатформенность** — загрузка на YouTube и VK (больше платформ в разработке)
- 📤 **Drag & Drop** — перетащите видео прямо в браузер
- 📊 **Отслеживание прогресса** — следите за загрузкой в реальном времени
- 📋 **История загрузок** — просматривайте все загруженные видео
- 🔒 **Приватность** — выбирайте публичность видео для каждой платформы
- 📹 **Большие файлы** — поддержка видео до 2 ГБ
- 🚀 **Асинхронная обработка** — используется Celery для фоновой загрузки

## 🎬 Скриншоты

Веб-интерфейс доступен по адресу: **http://localhost:8000**

## 🚀 Быстрый старт

### 1. Предварительные требования

- Docker и Docker Compose
- YouTube API credentials ([как получить](#получение-youtube-api-credentials))

### 2. Клонирование и настройка

```bash
# Клонируйте репозиторий
git clone <ваш-репозиторий>
cd fanout-publisher

# Создайте .env файл на основе шаблона
cp ENV_TEMPLATE.txt .env

# Отредактируйте .env и заполните credentials для нужных платформ
nano .env
```

### 3. Заполните .env файл

Минимальная конфигурация:

```bash
# Секретный токен (сгенерируйте случайную строку)
SERVICE_TOKEN=your-secret-token-123

# Пароль для PostgreSQL
POSTGRES_PASSWORD=strong-password-here

# YouTube API (см. инструкцию ниже)
YOUTUBE_CLIENT_ID=ваш-client-id.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=ваш-client-secret
YOUTUBE_REFRESH_TOKEN=ваш-refresh-token
YOUTUBE_DEFAULT_PRIVACY=private  # или public, unlisted

# VK API (опционально, если используете VK)
VK_ACCESS_TOKEN=ваш-vk-access-token
VK_GROUP_ID=0  # 0 = от пользователя, или ID группы
VK_DEFAULT_PRIVACY=private  # или public

# TikTok API (опционально, если используете TikTok)
TIKTOK_CLIENT_KEY=ваш-client-key
TIKTOK_CLIENT_SECRET=ваш-client-secret
TIKTOK_ACCESS_TOKEN=ваш-access-token
TIKTOK_DEFAULT_PRIVACY=SELF_ONLY  # или PUBLIC_TO_EVERYONE
```

### 4. Получение API credentials

#### YouTube (обязательно для работы с YouTube)

**Вариант 1: Быстрый (через скрипт)**

```bash
# Установите зависимости
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Запустите скрипт
python scripts/get_youtube_token.py

# Следуйте инструкциям в терминале
# Скопируйте полученные Client ID, Client Secret и Refresh Token в .env
```

**Вариант 2: Вручную**

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект
3. Включите **YouTube Data API v3**
4. Создайте **OAuth 2.0 Client ID** (тип: Desktop app)
5. Скачайте credentials и используйте скрипт выше

#### VK (опционально, если используете VK)

**Быстрая настройка:**

```bash
# Запустите скрипт для получения VK токена
python scripts/get_vk_token.py

# Следуйте инструкциям в терминале
# Скопируйте полученный Access Token в .env
```

**Подробная инструкция:** см. [VK_SETUP_GUIDE.md](VK_SETUP_GUIDE.md)

#### TikTok (опционально, если используете TikTok)

**Быстрая настройка:**

```bash
# Зарегистрируйтесь на https://developers.tiktok.com/
# Создайте приложение и получите Client Key/Secret
# Запустите скрипт для получения токена
python scripts/get_tiktok_token.py

# Следуйте инструкциям в терминале
# Скопируйте Client Key, Secret и Access Token в .env
```

**Подробная инструкция:** см. [TIKTOK_SETUP_GUIDE.md](TIKTOK_SETUP_GUIDE.md)

⚠️ **Для России**: требуется VPN для работы с TikTok API

### 5. Запуск приложения

```bash
# Запустите все сервисы
docker-compose up -d

# Проверьте статус (все должны быть healthy/running)
docker-compose ps

# Откройте браузер
# Веб-интерфейс: http://localhost:8000
# MinIO Console: http://localhost:9003
```

### 6. Загрузите первое видео! 🎉

1. Откройте http://localhost:8000
2. Перетащите видео или нажмите на область загрузки
3. Заполните название и описание
4. Нажмите "Загрузить на YouTube"
5. Получите ссылку на опубликованное видео!

## 📚 Документация

### 🚀 Начало работы
- **[QUICK_START_WEB.md](QUICK_START_WEB.md)** — Быстрый старт за 5 минут
- **[QUICK_LINKS.md](QUICK_LINKS.md)** — 🔗 Шпаргалка с важными URL и командами
- **[WEB_VERSION_README.md](WEB_VERSION_README.md)** — Полная документация веб-версии

### 🔧 Настройка платформ
- **[GITHUB_PAGES_SETUP.md](GITHUB_PAGES_SETUP.md)** — 🚀 Настройка GitHub Pages (Terms & Privacy)
- **[TIKTOK_АВТООБНОВЛЕНИЕ_ТОКЕНОВ.md](TIKTOK_АВТООБНОВЛЕНИЕ_ТОКЕНОВ.md)** — 🔄 **Автообновление TikTok токенов (ВАЖНО!)**
- **[TIKTOK_QUICK_START.md](TIKTOK_QUICK_START.md)** — ⚡ TikTok Quick Start (старт за 5 шагов)
- **[TIKTOK_TOKEN_JUSTINSTOLPE.md](TIKTOK_TOKEN_JUSTINSTOLPE.md)** — 🎯 **Получение токена через justinstolpe.com (ПРОЩЕ ВСЕГО!)**
- **[TIKTOK_SETUP_GUIDE.md](TIKTOK_SETUP_GUIDE.md)** — 📘 Полное руководство по TikTok API
- **[TIKTOK_MANUAL_TOKEN.md](TIKTOK_MANUAL_TOKEN.md)** — 🔐 Получение токена вручную
- **[TIKTOK_APP_FORM_TEMPLATE.md](TIKTOK_APP_FORM_TEMPLATE.md)** — 📋 Шаблон для заполнения формы TikTok
- **[TIKTOK_ENV_SETUP.md](TIKTOK_ENV_SETUP.md)** — 🔧 Настройка .env для TikTok
- **[VK_SETUP_GUIDE.md](VK_SETUP_GUIDE.md)** — 📘 Настройка VK (ВКонтакте) API

### 📖 Дополнительно
- **[ФАЙЛЫ_ДЛЯ_УДАЛЕНИЯ.md](ФАЙЛЫ_ДЛЯ_УДАЛЕНИЯ.md)** — Какие файлы можно удалить после миграции
- **[README_TELEGRAM_OLD.md](README_TELEGRAM_OLD.md)** — Старая документация Telegram бота (устарела)

## 🏗️ Архитектура

```
┌──────────────┐
│  Web Browser │
│  (You)       │
└──────┬───────┘
       │
       ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   FastAPI    │──▶│    Celery    │──▶│   YouTube    │
│   Web UI     │   │   Workers    │   │   API v3     │
└──────┬───────┘   └──────┬───────┘   └──────────────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│  PostgreSQL  │   │   MinIO/S3   │
│   (Jobs DB)  │   │   (Videos)   │
└──────────────┘   └──────────────┘
```

### Компоненты:

- **FastAPI** — REST API + веб-интерфейс
- **Static Files** — HTML/CSS/JS для веб-интерфейса
- **Celery Workers** — Асинхронная загрузка на YouTube
- **PostgreSQL** — База данных заявок на публикацию
- **Redis** — Очередь задач для Celery
- **MinIO** — S3-совместимое хранилище видео

## 📁 Структура проекта

```
fanout-publisher/
├── app/                    # FastAPI приложение
│   ├── main.py            # API + веб-интерфейс
│   ├── config.py          # Конфигурация
│   ├── database.py        # Модели БД
│   └── schemas.py         # Pydantic схемы
├── static/                # Веб-интерфейс
│   ├── index.html         # Главная страница
│   ├── style.css          # Стили (YouTube-style)
│   └── script.js          # JavaScript логика
├── workers/               # Celery workers
│   ├── celery_app.py      # Конфигурация Celery
│   └── tasks_publish.py   # Задачи публикации
├── platforms/             # Адаптеры платформ
│   └── youtube.py         # YouTube publisher
├── scripts/               # Утилиты
│   └── get_youtube_token.py
├── docker-compose.yml     # Docker конфигурация
├── requirements.txt       # Python зависимости
└── .env                   # Настройки (создайте сами!)
```

## 🔍 API Endpoints

### Публичные (для веб-интерфейса):
- `GET /` — Веб-интерфейс
- `POST /upload` — Загрузка видео
- `GET /api/status/{id}` — Проверка статуса
- `GET /api/jobs` — Список последних загрузок
- `GET /health` — Health check

### Защищенные (требуют X-Service-Token):
- `POST /ingest` — Программная загрузка
- `GET /status/{id}` — Статус с токеном
- `POST /retry_failed/{id}` — Повтор публикации

## 🛠️ Полезные команды

```bash
# Остановить все сервисы
docker-compose down

# Перезапустить
docker-compose restart

# Посмотреть логи
docker-compose logs -f api
docker-compose logs -f worker

# Очистить всё (ВНИМАНИЕ: удалит все данные!)
docker-compose down -v
```

## 🐛 Troubleshooting

### Веб-интерфейс не открывается

```bash
# Проверьте логи API
docker-compose logs -f api

# Проверьте что сервис запущен
docker-compose ps api
```

### Ошибка "YouTube credentials not configured"

Убедитесь, что в `.env` заполнены все три поля:
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

### Видео загружается, но не публикуется

```bash
# Проверьте логи worker
docker-compose logs -f worker

# Убедитесь, что YouTube API включен в Google Cloud Console
# Проверьте квоты API (10,000 units/day)
```

## 🔐 Безопасность

- ⚠️ **НЕ коммитьте .env файл** в git!
- 🔑 Используйте сильные пароли для `POSTGRES_PASSWORD` и `SERVICE_TOKEN`
- 🌐 В продакшене настройте HTTPS
- 👤 Рассмотрите добавление аутентификации пользователей

## 🎯 Roadmap

### ✅ Реализовано
- [x] Веб-интерфейс с drag & drop
- [x] Загрузка на YouTube
- [x] Отслеживание прогресса
- [x] История загрузок
- [x] Выбор приватности

### 🚧 В планах
- [ ] Аутентификация пользователей
- [ ] Поддержка Instagram Reels
- [ ] Поддержка Facebook Reels
- [ ] Поддержка X (Twitter)
- [ ] Поддержка Дзен
- [ ] Поддержка Одноклассники
- [ ] Расписание публикаций
- [ ] Массовая загрузка
- [ ] Редактирование метаданных

## 📝 Changelog

### Version 2.2.0 - TikTok Support (текущая)
- ✅ Добавлена поддержка TikTok через Content Posting API
- ✅ OAuth 2.0 авторизация для TikTok
- ✅ Поддержка приватных/публичных видео
- ✅ Скрипт для получения TikTok токена
- ✅ Подробная документация с учетом VPN для РФ

### Version 2.1.0 - VK Support
- ✅ Добавлена поддержка VK (ВКонтакте)
- ✅ Мультиплатформенный выбор в веб-интерфейсе
- ✅ Скрипты для настройки VK токена
- ✅ Тестовый скрипт для VK
- ✅ Подробная документация по VK

### Version 2.0.0 - Web Version
- ✅ Полностью переписан на веб-интерфейс
- ✅ Удалён Telegram бот
- ✅ Современный UI/UX в стиле YouTube
- ✅ Упрощённая архитектура

### Version 1.0.0 - Telegram Bot (устарела)
- Загрузка через Telegram (см. README_TELEGRAM_OLD.md)

## 📄 Лицензия

MIT License — используйте свободно!

## 🤝 Поддержка

Если возникли вопросы:
1. Проверьте [WEB_VERSION_README.md](WEB_VERSION_README.md)
2. Посмотрите логи: `docker-compose logs -f`
3. Проверьте `.env` файл

## ⭐ Благодарности

- [FastAPI](https://fastapi.tiangolo.com/) — веб-фреймворк
- [Celery](https://docs.celeryq.dev/) — асинхронные задачи
- [MinIO](https://min.io/) — хранилище видео
- [Google YouTube API](https://developers.google.com/youtube) — публикация на YouTube
- [VK API](https://dev.vk.com/) — публикация на VK
- [TikTok Content Posting API](https://developers.tiktok.com/) — публикация на TikTok

---

**Приятного использования! 🚀 Загружайте видео на YouTube в один клик!**

