# 🔧 Инструкция по настройке .env файла

Файл `.env` уже создан в корне проекта. Теперь нужно заполнить реальные значения.

## ✅ ШАГ 1: SERVICE_TOKEN (ОБЯЗАТЕЛЬНО)

Я сгенерировал для вас токен:
```
fxKRAphBNLtJwglO3ZS4XConiTduWM0qV19mj7P5aFzH2cr6
```

Откройте `.env` и замените:
```bash
SERVICE_TOKEN=your-secret-service-token-here
```

На:
```bash
SERVICE_TOKEN=fxKRAphBNLtJwglO3ZS4XConiTduWM0qV19mj7P5aFzH2cr6
```

---

## ✅ ШАГ 2: TELEGRAM BOT TOKEN (ОБЯЗАТЕЛЬНО)

1. Откройте Telegram
2. Найдите бота [@BotFather](https://t.me/BotFather)
3. Отправьте команду: `/newbot`
4. Придумайте имя бота (например: `My Fanout Publisher`)
5. Придумайте username (например: `my_fanout_publisher_bot`)
6. Скопируйте полученный токен

В `.env` замените:
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

На ваш токен:
```bash
TELEGRAM_BOT_TOKEN=5123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
```
(это пример, используйте свой!)

---

## ✅ ШАГ 3: TELEGRAM API CREDENTIALS (ОБЯЗАТЕЛЬНО)

1. Перейдите на: https://my.telegram.org/apps
2. Авторизуйтесь через Telegram
3. Нажмите "Create new application"
4. Заполните форму:
   - App title: `Fanout Publisher`
   - Short name: `fanout`
   - Platform: `Other`
5. Получите `api_id` (число) и `api_hash` (строка)

В `.env` замените:
```bash
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
```

На ваши данные:
```bash
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

---

## ✅ ШАГ 4: TELEGRAM ADMIN ID (ОБЯЗАТЕЛЬНО)

1. Откройте Telegram
2. Найдите бота [@userinfobot](https://t.me/userinfobot)
3. Нажмите "Start" или отправьте любое сообщение
4. Скопируйте ваш `Id` (число)

В `.env` замените:
```bash
TELEGRAM_ADMIN_ID=123456789
```

На ваш ID:
```bash
TELEGRAM_ADMIN_ID=987654321
```

---

## 🟡 ШАГ 5: YOUTUBE (ОПЦИОНАЛЬНО)

**Если вы НЕ планируете публиковать на YouTube прямо сейчас - пропустите этот шаг!**

Оставьте пустыми значениями:
```bash
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_REFRESH_TOKEN=
```

### Когда будете готовы настроить YouTube:

1. Перейдите на: https://console.cloud.google.com/
2. Создайте проект
3. Включите "YouTube Data API v3"
4. Создайте OAuth 2.0 credentials (Desktop app)
5. Скачайте JSON с credentials
6. Запустите скрипт:
   ```bash
   python scripts/get_youtube_token.py
   ```
7. Следуйте инструкциям в скрипте

---

## ✅ ШАГ 6: ПРОВЕРКА

После заполнения всех обязательных полей, ваш `.env` должен выглядеть так:

```bash
# GENERAL SETTINGS
ENV=development
DEBUG=true
LOG_LEVEL=INFO

# SECURITY
SERVICE_TOKEN=fxKRAphBNLtJwglO3ZS4XConiTduWM0qV19mj7P5aFzH2cr6

# DATABASE (оставить как есть)
POSTGRES_DB=fanout_publisher
POSTGRES_USER=fanout_user
POSTGRES_PASSWORD=fanout_password
DATABASE_URL=postgresql://fanout_user:fanout_password@postgres:5432/fanout_publisher

# REDIS (оставить как есть)
REDIS_URL=redis://redis:6379/0

# CELERY (оставить как есть)
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# MinIO (оставить как есть)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=videos
MINIO_SECURE=false

# API SERVER (оставить как есть)
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://api:8000

# YOUTUBE (пока оставить пустым)
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_REFRESH_TOKEN=

# TELEGRAM BOT (заполнить своими данными!)
TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН_ОТ_BOTFATHER
TELEGRAM_API_ID=ВАШ_API_ID
TELEGRAM_API_HASH=ВАШ_API_HASH
TELEGRAM_LOCAL_API_URL=http://telegram-bot-api:8081
TELEGRAM_ADMIN_ID=ВАШ_TELEGRAM_USER_ID
```

---

## 🚀 ШАГ 7: ЗАПУСК

После заполнения `.env` файла:

```bash
# Запустить все сервисы
docker-compose up -d

# Инициализировать базу данных
docker-compose exec api python scripts/init_db.py

# Проверить логи
docker-compose logs -f bot
```

---

## 🔒 БЕЗОПАСНОСТЬ

**ВАЖНО:**
- ❌ НИКОГДА не коммитьте `.env` файл в Git!
- ✅ Файл `.env` уже добавлен в `.gitignore`
- ✅ Шаблон `.env.example` можно коммитить (без реальных данных)

---

## 📝 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ

Более подробные инструкции смотрите в:
- `README.md` - общая информация о проекте
- `SETUP_GUIDE.md` - детальное руководство по настройке
- `START_HERE.md` - быстрый старт

---

## ❓ ЧАСТЫЕ ВОПРОСЫ

**Q: Можно ли изменить пароли PostgreSQL?**
A: Да, измените `POSTGRES_PASSWORD` и обновите `DATABASE_URL` соответственно.

**Q: Нужно ли менять MINIO credentials для продакшена?**
A: Да! Для продакшена обязательно смените `MINIO_ACCESS_KEY` и `MINIO_SECRET_KEY`.

**Q: Как узнать, что всё настроено правильно?**
A: Запустите `docker-compose up` и проверьте логи. Если все контейнеры запустились без ошибок - всё ОК!

---

Успехов! 🎉

