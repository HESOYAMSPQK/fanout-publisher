# ⚡ Быстрый старт - Команды для копирования

Этот файл содержит все команды для быстрого запуска Fanout Publisher.

---

## 🔧 1. Подготовка окружения

### Windows (PowerShell):

```powershell
# Клонирование (замени <repository_url> на актуальный)
git clone <repository_url>
cd fanout-publisher

# Копирование .env
copy .env.example .env

# Генерация SERVICE_TOKEN (скопируй результат в .env)
-join ((48..57) + (97..102) | Get-Random -Count 64 | % {[char]$_})

# Редактирование .env
notepad .env
```

### Linux/Mac:

```bash
# Клонирование (замени <repository_url> на актуальный)
git clone <repository_url>
cd fanout-publisher

# Копирование .env
cp .env.example .env

# Генерация SERVICE_TOKEN (скопируй результат в .env)
openssl rand -hex 32

# Редактирование .env
nano .env
# или
vim .env
# или
code .env
```

---

## 🚀 2. Запуск сервисов

### Вариант 1: Автоматический скрипт (рекомендуется)

**Linux/Mac:**
```bash
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh
```

**Windows:**
```cmd
scripts\quick_start.bat
```

### Вариант 2: Вручную

```bash
# Сборка и запуск всех сервисов
docker compose up -d

# Ожидание запуска (30 секунд)
# Linux/Mac:
sleep 30

# Windows PowerShell:
Start-Sleep -Seconds 30

# Инициализация базы данных
docker compose exec api python scripts/init_db.py

# Проверка статуса
docker compose ps
```

---

## 📊 3. Проверка работоспособности

### Health Check API:

```bash
curl http://localhost:8000/health
```

**Ожидаемый ответ:**
```json
{"status":"healthy","timestamp":"2025-10-15T12:00:00","service":"fanout-publisher-api"}
```

### Интеграционный тест:

```bash
docker compose exec api python scripts/probe_ingest.py
```

---

## 🔑 4. Получение YouTube Refresh Token

```bash
# Запуск скрипта (откроется браузер)
docker compose exec api python scripts/get_youtube_token.py

# После авторизации скопируй YOUTUBE_REFRESH_TOKEN из вывода
# Добавь его в .env файл

# Перезапусти worker и bot
docker compose restart worker bot
```

---

## 🎥 5. Тестирование загрузки на YouTube

```bash
# Подготовь тестовое видео, например test_video.mp4
# Скопируй его в контейнер
docker cp test_video.mp4 fanout-publisher-api-1:/tmp/test_video.mp4

# Запусти тест загрузки
docker compose exec api python scripts/test_youtube_upload.py /tmp/test_video.mp4

# Или локально (если Python установлен):
python scripts/test_youtube_upload.py test_video.mp4
```

---

## 📱 6. Тестирование Telegram бота

1. Открой Telegram
2. Найди своего бота (username из @BotFather)
3. Отправь `/start`
4. Отправь видео
5. Введи название и описание
6. Дождись публикации

---

## 📋 7. Полезные команды

### Просмотр логов:

```bash
# Все сервисы
docker compose logs -f

# API
docker compose logs -f api

# Worker
docker compose logs -f worker

# Bot
docker compose logs -f bot

# Telegram Bot API
docker compose logs -f telegram-bot-api

# PostgreSQL
docker compose logs -f postgres

# Redis
docker compose logs -f redis

# MinIO
docker compose logs -f minio
```

### Перезапуск сервисов:

```bash
# Все
docker compose restart

# Конкретный сервис
docker compose restart api
docker compose restart worker
docker compose restart bot
```

### Остановка и запуск:

```bash
# Остановить все
docker compose stop

# Запустить все
docker compose start

# Остановить и удалить контейнеры
docker compose down

# Остановить и удалить контейнеры + volumes (ВНИМАНИЕ: удалит БД)
docker compose down -v
```

### Доступ к контейнерам:

```bash
# Shell в API контейнере
docker compose exec api bash

# Shell в Worker контейнере
docker compose exec worker bash

# Shell в Bot контейнере
docker compose exec bot bash

# PostgreSQL
docker compose exec postgres psql -U fanout_user -d fanout_publisher

# Redis CLI
docker compose exec redis redis-cli
```

### Работа с БД:

```bash
# Подключение к PostgreSQL
docker compose exec postgres psql -U fanout_user -d fanout_publisher

# Внутри psql:
# \dt - список таблиц
# SELECT * FROM publish_jobs LIMIT 10; - просмотр заданий
# \q - выход
```

```sql
-- Примеры SQL запросов:

-- Все задания
SELECT id, submission_id, platform, status, title, created_at 
FROM publish_jobs 
ORDER BY created_at DESC 
LIMIT 10;

-- Статистика по статусам
SELECT status, COUNT(*) 
FROM publish_jobs 
GROUP BY status;

-- Проваленные задания
SELECT submission_id, platform, title, error_message, created_at
FROM publish_jobs
WHERE status = 'FAILED'
ORDER BY created_at DESC;

-- Успешные публикации
SELECT submission_id, platform, title, public_url, published_at
FROM publish_jobs
WHERE status = 'COMPLETED'
ORDER BY published_at DESC
LIMIT 10;
```

### Работа с Redis:

```bash
# Подключение к Redis
docker compose exec redis redis-cli

# Внутри redis-cli:
# KEYS * - все ключи
# GET key - получить значение
# DEL key - удалить ключ
# FLUSHALL - очистить всё (ОСТОРОЖНО!)
```

```bash
# Примеры команд Redis:

# Просмотр очереди Celery
KEYS *celery*

# Количество задач в очереди
LLEN celery

# Просмотр задач (первые 10)
LRANGE celery 0 9

# Очистка очереди (ОСТОРОЖНО!)
DEL celery
```

### MinIO Console:

```bash
# Открой в браузере
open http://localhost:9001

# Windows:
start http://localhost:9001

# Логин:
# Username: minioadmin
# Password: (твой MINIO_SECRET_KEY из .env)
```

### Мониторинг:

```bash
# Статус контейнеров
docker compose ps

# Использование ресурсов
docker stats

# Логи с временными метками
docker compose logs -f --timestamps

# Последние 100 строк логов
docker compose logs --tail=100 api
```

---

## 🧪 8. API тестирование

### Через curl:

```bash
# Health Check
curl http://localhost:8000/health

# POST /ingest (замени YOUR_SERVICE_TOKEN)
curl -X POST http://localhost:8000/ingest \
  -H "X-Service-Token: YOUR_SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "video_hash": "test_hash_123",
    "s3_key": "videos/test/video.mp4",
    "file_size": 1000000,
    "duration": 30,
    "platform": "youtube",
    "title": "Test Video",
    "description": "Test Description",
    "tags": ["shorts", "test"]
  }'

# GET /status (замени SUBMISSION_ID и YOUR_SERVICE_TOKEN)
curl http://localhost:8000/status/SUBMISSION_ID \
  -H "X-Service-Token: YOUR_SERVICE_TOKEN"

# POST /retry_failed (замени SUBMISSION_ID и YOUR_SERVICE_TOKEN)
curl -X POST http://localhost:8000/retry_failed/SUBMISSION_ID \
  -H "X-Service-Token: YOUR_SERVICE_TOKEN"
```

### Через Python requests:

```python
import requests

API_URL = "http://localhost:8000"
SERVICE_TOKEN = "your_token_here"

headers = {"X-Service-Token": SERVICE_TOKEN}

# Health
response = requests.get(f"{API_URL}/health")
print(response.json())

# Ingest
payload = {
    "video_hash": "test123",
    "s3_key": "videos/test.mp4",
    "file_size": 1000000,
    "duration": 30,
    "platform": "youtube",
    "title": "Test Video",
    "description": "Test Description",
    "tags": ["test"]
}
response = requests.post(f"{API_URL}/ingest", json=payload, headers=headers)
print(response.json())

submission_id = response.json()["submission_id"]

# Status
response = requests.get(f"{API_URL}/status/{submission_id}", headers=headers)
print(response.json())
```

### Через requests.http (REST Client в VS Code):

Открой файл `requests.http` и используй кнопку "Send Request" над каждым запросом.

---

## 🧹 9. Очистка и обслуживание

### Очистка Docker:

```bash
# Удалить неиспользуемые образы
docker image prune -a

# Удалить неиспользуемые volumes
docker volume prune

# Удалить всё неиспользуемое
docker system prune -a --volumes

# Полная очистка проекта
docker compose down -v
docker system prune -a
```

### Backup базы данных:

```bash
# Экспорт БД
docker compose exec postgres pg_dump -U fanout_user fanout_publisher > backup.sql

# Импорт БД
cat backup.sql | docker compose exec -T postgres psql -U fanout_user -d fanout_publisher
```

### Backup MinIO (видео):

```bash
# Используй MinIO Console или mc client
# Скачай mc: https://min.io/docs/minio/linux/reference/minio-mc.html

# Настрой alias
mc alias set local http://localhost:9000 minioadmin YOUR_MINIO_SECRET_KEY

# Скачать bucket
mc mirror local/videos ./backup/videos/

# Загрузить bucket обратно
mc mirror ./backup/videos/ local/videos
```

---

## 🔧 10. Troubleshooting

### API не запускается:

```bash
# Проверь логи
docker compose logs api

# Проверь переменные окружения
docker compose exec api env | grep DATABASE_URL

# Проверь БД доступна
docker compose exec postgres pg_isready -U fanout_user

# Перезапусти API
docker compose restart api

# Пересобери образ
docker compose build api
docker compose up -d api
```

### Worker не обрабатывает задачи:

```bash
# Проверь логи
docker compose logs worker

# Проверь Redis
docker compose exec redis redis-cli ping

# Проверь очередь
docker compose exec redis redis-cli LLEN celery

# Перезапусти worker
docker compose restart worker

# Если не помогло - очисти очередь и перезапусти
docker compose exec redis redis-cli DEL celery
docker compose restart worker
```

### Бот не отвечает:

```bash
# Проверь логи
docker compose logs bot

# Проверь токен бота
docker compose exec bot env | grep TELEGRAM_BOT_TOKEN

# Проверь локальный Bot API
docker compose logs telegram-bot-api

# Проверь API доступен из бота
docker compose exec bot curl http://api:8000/health

# Перезапусти бота
docker compose restart bot
```

### YouTube upload fails:

```bash
# Проверь логи worker
docker compose logs worker | grep -i youtube

# Проверь YouTube credentials
docker compose exec api python -c "
from platforms.youtube import YouTubePublisher
import os
print('Client ID:', os.getenv('YOUTUBE_CLIENT_ID'))
print('Has Secret:', bool(os.getenv('YOUTUBE_CLIENT_SECRET')))
print('Has Refresh:', bool(os.getenv('YOUTUBE_REFRESH_TOKEN')))
"

# Получи новый refresh token
docker compose exec api python scripts/get_youtube_token.py

# Обнови .env и перезапусти
docker compose restart worker api
```

### Порты заняты:

```bash
# Проверь какие порты используются
# Linux/Mac:
lsof -i :8000
lsof -i :5432
lsof -i :6379
lsof -i :9000

# Windows PowerShell:
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Останови конфликтующие процессы или измени порты в docker-compose.yml
```

---

## 📚 11. Makefile команды (если установлен make)

```bash
make help           # Показать все команды
make build          # Собрать образы
make up             # Запустить сервисы
make down           # Остановить сервисы
make restart        # Перезапустить сервисы
make logs           # Показать все логи
make logs-api       # Логи API
make logs-worker    # Логи Worker
make logs-bot       # Логи Bot
make clean          # Удалить всё включая volumes
make init-db        # Инициализировать БД
make test           # Запустить тесты
make test-api       # Тестировать API
make shell-api      # Открыть shell в API
make shell-db       # Открыть psql
make redis-cli      # Открыть Redis CLI
make ps             # Статус контейнеров
make youtube-token  # Получить YouTube token
```

---

## 🎯 12. Типичный workflow

### Первый запуск:

```bash
# 1. Подготовка
cp .env.example .env
# Отредактируй .env

# 2. Запуск
docker compose up -d
sleep 30

# 3. Инициализация
docker compose exec api python scripts/init_db.py

# 4. YouTube token
docker compose exec api python scripts/get_youtube_token.py
# Добавь токен в .env
docker compose restart worker bot

# 5. Тестирование
docker compose exec api python scripts/probe_ingest.py

# 6. Telegram бот
# Найди бота в Telegram и отправь /start
```

### Ежедневное использование:

```bash
# Запуск (если остановлен)
docker compose start

# Проверка логов
docker compose logs -f

# Остановка
docker compose stop
```

### Обновление после изменений:

```bash
# Остановить
docker compose down

# Обновить код (git pull или изменения)
git pull

# Пересобрать образы
docker compose build

# Запустить
docker compose up -d

# Проверить
docker compose ps
docker compose logs -f
```

### Отладка проблем:

```bash
# 1. Посмотри логи
docker compose logs -f

# 2. Проверь статус
docker compose ps

# 3. Проверь БД
docker compose exec postgres psql -U fanout_user -d fanout_publisher -c "SELECT COUNT(*) FROM publish_jobs;"

# 4. Проверь Redis
docker compose exec redis redis-cli ping

# 5. Проверь API
curl http://localhost:8000/health

# 6. Перезапусти проблемный сервис
docker compose restart api  # или worker, bot
```

---

## ✅ Checklist перед запуском в production

- [ ] Изменены все пароли в .env (не используй примеры)
- [ ] SERVICE_TOKEN сгенерирован случайно
- [ ] DEBUG=false в .env
- [ ] Настроен SSL/TLS (HTTPS)
- [ ] Настроен firewall (только нужные порты открыты)
- [ ] Настроены backups БД и MinIO
- [ ] Настроен мониторинг (Prometheus/Grafana)
- [ ] Настроены алерты при ошибках
- [ ] Ограничены квоты YouTube API
- [ ] Протестированы все сценарии
- [ ] Документирован процесс восстановления

---

**Готово! Удачи! 🚀**


