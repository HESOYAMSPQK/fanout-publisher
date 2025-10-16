# 📖 Пошаговая инструкция по настройке Fanout Publisher

Эта инструкция проведёт тебя через все этапы настройки от нуля до полностью работающего сервиса.

---

## 📋 Контрольный список перед началом

- [ ] Установлен Docker Desktop (Windows/Mac) или Docker Engine (Linux)
- [ ] Установлен Docker Compose
- [ ] Есть аккаунт Google (для YouTube API)
- [ ] Есть аккаунт Telegram
- [ ] 10-15 минут свободного времени

---

## Шаг 1: Подготовка проекта

### 1.1 Клонирование репозитория

```bash
cd /путь/к/проектам
git clone <repository_url>
cd fanout-publisher
```

### 1.2 Копирование .env файла

```bash
# Linux/Mac
cp .env.example .env

# Windows (PowerShell)
copy .env.example .env

# Windows (CMD)
copy .env.example .env
```

---

## Шаг 2: Настройка Telegram

### 2.1 Получение API ID и API Hash

1. Открой браузер и перейди на **https://my.telegram.org**
2. Войди, используя свой номер телефона
3. Перейди в раздел **"API development tools"**
4. Заполни форму создания приложения:
   - **App title:** `Fanout Publisher`
   - **Short name:** `fanout`
   - **Platform:** Other
   - **Description:** `Video publishing automation`
5. Нажми **"Create application"**
6. Скопируй `api_id` и `api_hash`

**Внеси в .env:**
```bash
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abc123def456...
```

### 2.2 Создание бота через BotFather

1. Открой Telegram и найди **@BotFather**
2. Отправь команду `/newbot`
3. Следуй инструкциям:
   - **Название бота:** `My Fanout Publisher` (любое имя)
   - **Username бота:** `my_fanout_bot` (должен заканчиваться на `bot`)
4. BotFather пришлёт тебе **Bot Token**, например:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
   ```
5. Скопируй токен

**Внеси в .env:**
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
```

### 2.3 Получение своего User ID

1. Найди в Telegram бота **@userinfobot**
2. Отправь ему `/start`
3. Бот пришлёт информацию о тебе, включая **User ID**, например: `123456789`
4. Скопируй User ID

**Внеси в .env:**
```bash
TELEGRAM_ADMIN_ID=123456789
```

---

## Шаг 3: Настройка YouTube API

### 3.1 Создание проекта в Google Cloud

1. Перейди на **https://console.cloud.google.com/**
2. Войди в свой Google аккаунт
3. Нажми на название проекта вверху → **"New Project"**
4. Введи название: `Fanout Publisher`
5. Нажми **"Create"**
6. Дождись создания проекта (несколько секунд)

### 3.2 Включение YouTube Data API v3

1. В левом меню выбери **"APIs & Services"** → **"Library"**
2. В поиске найди `YouTube Data API v3`
3. Нажми на API
4. Нажми **"Enable"**
5. Дождись активации

### 3.3 Создание OAuth 2.0 Credentials

1. Перейди в **"APIs & Services"** → **"Credentials"**
2. Нажми **"Create Credentials"** → **"OAuth client ID"**
3. Если появится предупреждение о настройке OAuth consent screen:
   - Нажми **"Configure Consent Screen"**
   - Выбери **"External"** (если нет организации)
   - Нажми **"Create"**
   - Заполни минимальные поля:
     - **App name:** `Fanout Publisher`
     - **User support email:** твой email
     - **Developer contact:** твой email
   - Нажми **"Save and Continue"**
   - На странице Scopes нажми **"Save and Continue"**
   - На странице Test users добавь свой email
   - Нажми **"Save and Continue"**
4. Вернись к созданию OAuth client ID
5. Выбери **Application type:** `Desktop app`
6. **Name:** `Fanout Publisher Desktop`
7. Нажми **"Create"**
8. Появится окно с **Client ID** и **Client Secret**
9. Скопируй оба значения

**Внеси в .env:**
```bash
YOUTUBE_CLIENT_ID=123456789-abc...apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-abc123...
```

### 3.4 Получение Refresh Token

Этот шаг выполнится **после** запуска сервисов (см. Шаг 5).

---

## Шаг 4: Настройка остальных переменных в .env

### 4.1 Генерация SERVICE_TOKEN

**Linux/Mac:**
```bash
openssl rand -hex 32
```

**Windows (PowerShell):**
```powershell
-join ((48..57) + (97..102) | Get-Random -Count 64 | % {[char]$_})
```

**Или онлайн:** https://www.random.org/strings/

**Внеси в .env:**
```bash
SERVICE_TOKEN=сгенерированный_токен_64_символа
```

### 4.2 Пароли для БД и MinIO

Придумай надёжные пароли или сгенерируй их.

**Внеси в .env:**
```bash
POSTGRES_PASSWORD=твой_надежный_пароль_для_postgres
MINIO_SECRET_KEY=твой_надежный_пароль_для_minio
```

**Обнови DATABASE_URL:**
```bash
DATABASE_URL=postgresql://fanout_user:твой_надежный_пароль_для_postgres@postgres:5432/fanout_publisher
```

### 4.3 Проверка .env

Убедись, что все эти переменные заполнены:
- ✅ SERVICE_TOKEN
- ✅ POSTGRES_PASSWORD
- ✅ MINIO_SECRET_KEY
- ✅ DATABASE_URL (с правильным паролем)
- ✅ TELEGRAM_API_ID
- ✅ TELEGRAM_API_HASH
- ✅ TELEGRAM_BOT_TOKEN
- ✅ TELEGRAM_ADMIN_ID
- ✅ YOUTUBE_CLIENT_ID
- ✅ YOUTUBE_CLIENT_SECRET

❗ `YOUTUBE_REFRESH_TOKEN` пока оставляем пустым, получим его в Шаге 5.

---

## Шаг 5: Запуск сервисов

### 5.1 Запуск Docker Compose

**Linux/Mac:**
```bash
# Вариант 1: Автоматический скрипт
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh

# Вариант 2: Вручную
docker compose up -d
```

**Windows:**
```cmd
REM Вариант 1: Автоматический скрипт
scripts\quick_start.bat

REM Вариант 2: Вручную
docker compose up -d
```

### 5.2 Проверка статуса сервисов

```bash
docker compose ps
```

Должно быть запущено 7 сервисов:
- ✅ postgres
- ✅ redis
- ✅ minio
- ✅ telegram-bot-api
- ✅ api
- ✅ worker
- ✅ bot

### 5.3 Просмотр логов

```bash
# Все логи
docker compose logs -f

# Только API
docker compose logs -f api

# Только Bot
docker compose logs -f bot

# Только Worker
docker compose logs -f worker
```

Для выхода нажми `Ctrl+C`

### 5.4 Инициализация базы данных

```bash
docker compose exec api python scripts/init_db.py
```

Должно появиться: `✅ Database tables created successfully!`

---

## Шаг 6: Получение YouTube Refresh Token

### 6.1 Запуск скрипта получения токена

```bash
docker compose exec api python scripts/get_youtube_token.py
```

### 6.2 Авторизация

1. Скрипт откроет браузер автоматически (или выведет ссылку для ручного открытия)
2. Войди в свой Google аккаунт (если не вошёл)
3. Появится предупреждение **"Google hasn't verified this app"**:
   - Нажми **"Advanced"**
   - Нажми **"Go to Fanout Publisher (unsafe)"**
4. Разреши доступ к YouTube:
   - Поставь галочку
   - Нажми **"Continue"**
5. В консоли появится:
   ```
   ✅ Authorization successful!
   
   📋 Your refresh token:
   
   YOUTUBE_REFRESH_TOKEN=1//abc123def456...
   ```
6. Скопируй токен

### 6.3 Добавление токена в .env

Открой `.env` и вставь токен:
```bash
YOUTUBE_REFRESH_TOKEN=1//abc123def456...
```

Сохрани файл.

### 6.4 Перезапуск сервисов

```bash
docker compose restart worker bot
```

---

## Шаг 7: Тестирование API

### 7.1 Health Check

```bash
curl http://localhost:8000/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-15T12:00:00",
  "service": "fanout-publisher-api"
}
```

### 7.2 Интеграционный тест

```bash
docker compose exec api python scripts/probe_ingest.py
```

**Ожидаемый вывод:**
```
======================================================================
API Integration Test
======================================================================
API URL: http://api:8000

🏥 Testing /health endpoint...
✅ Health check passed: {...}

📤 Testing /ingest endpoint...
✅ Ingest successful!
   Submission ID: abc-123-def-456
   Status: QUEUED

⏳ Waiting 2 seconds before checking status...

📊 Testing /status endpoint for abc-123-def-456...
✅ Status retrieved!
   Status: PENDING
   Platform: youtube
   ...
```

---

## Шаг 8: Тестирование Telegram бота

### 8.1 Поиск бота в Telegram

1. Открой Telegram
2. В поиске введи username своего бота (например, `@my_fanout_bot`)
3. Открой чат с ботом

### 8.2 Запуск бота

Отправь боту команду:
```
/start
```

**Ожидаемый ответ:**
```
👋 Привет, Имя!

Я помогу тебе автоматически публиковать короткие видео на YouTube Shorts
и другие платформы.

📹 Просто отправь мне видео (до 2 ГБ), и я опубликую его!

Доступные команды:
/start - Начать работу
/help - Помощь
/cancel - Отменить текущую операцию
```

### 8.3 Отправка тестового видео

1. Подготовь короткое вертикальное видео (9:16, желательно до 60 секунд)
2. Отправь видео боту (как файл, видео или видеосообщение)
3. Бот скачает видео и попросит описание:
   ```
   ✅ Видео загружено!
   
   📝 Теперь напиши название и описание для видео.
   ```
4. Отправь текст, например:
   ```
   Мое тестовое видео
   Это тестовая загрузка на YouTube Shorts #shorts #test
   ```
5. Бот отправит видео на публикацию:
   ```
   ✅ Видео принято на публикацию!
   
   🆔 ID заявки: abc-123-def-456
   📺 Платформа: YouTube Shorts
   📋 Заголовок: Мое тестовое видео
   
   ⏳ Публикация займет несколько минут.
   Я уведомлю тебя, когда видео будет опубликовано!
   ```
6. Через 1-3 минуты бот пришлёт уведомление:
   ```
   🎉 Видео успешно опубликовано!
   
   🆔 ID: abc-123-def-456
   🔗 Ссылка: https://youtube.com/watch?v=xyz
   
   Поздравляю! 🚀
   ```

---

## Шаг 9: Проверка результата на YouTube

1. Перейди по ссылке из сообщения бота
2. Или открой **YouTube Studio** → **Content**
3. Найди своё видео
4. Проверь:
   - ✅ Видео загружено
   - ✅ Название корректное
   - ✅ Описание корректное
   - ✅ Видео публичное (или unlisted, если так настроено)

---

## 🎉 Поздравляем! Сервис настроен и работает!

---

## 🔧 Полезные команды

### Просмотр логов

```bash
# Все сервисы
docker compose logs -f

# Конкретный сервис
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f bot
```

### Перезапуск сервисов

```bash
# Все сервисы
docker compose restart

# Конкретный сервис
docker compose restart api
docker compose restart worker
docker compose restart bot
```

### Остановка сервисов

```bash
docker compose down
```

### Полная очистка (включая volumes)

```bash
docker compose down -v
```

### Доступ к БД

```bash
docker compose exec postgres psql -U fanout_user -d fanout_publisher
```

### Доступ к Redis

```bash
docker compose exec redis redis-cli
```

### MinIO Console

Открой в браузере: **http://localhost:9001**
- **Username:** minioadmin
- **Password:** (твой `MINIO_SECRET_KEY` из .env)

---

## 🐛 Troubleshooting

### Проблема: API не запускается

**Решение:**
```bash
# Проверь логи
docker compose logs api

# Проверь .env файл
cat .env | grep DATABASE_URL

# Проверь доступность PostgreSQL
docker compose exec postgres psql -U fanout_user -d fanout_publisher -c "SELECT 1"
```

### Проблема: Worker не обрабатывает задачи

**Решение:**
```bash
# Проверь логи
docker compose logs worker

# Проверь Redis
docker compose exec redis redis-cli ping

# Проверь очередь Celery
docker compose exec redis redis-cli KEYS "*celery*"
```

### Проблема: Бот не отвечает

**Решение:**
```bash
# Проверь логи
docker compose logs bot

# Проверь токен
docker compose exec bot env | grep TELEGRAM_BOT_TOKEN

# Перезапусти бота
docker compose restart bot
```

### Проблема: YouTube upload fails

**Решение:**
1. Проверь квоты API: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
2. Проверь refresh token не истёк
3. Получи новый refresh token:
   ```bash
   docker compose exec api python scripts/get_youtube_token.py
   ```
4. Обнови .env и перезапусти:
   ```bash
   docker compose restart worker
   ```

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверь все переменные в `.env`
2. Посмотри логи: `docker compose logs -f`
3. Перезапусти сервисы: `docker compose restart`
4. Создай issue в GitHub с описанием проблемы и логами

---

**Удачи! 🚀**


