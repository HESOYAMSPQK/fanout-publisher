# 📘 Настройка TikTok для Fanout Publisher

> Пошаговая инструкция по подключению TikTok Content Posting API для автоматической загрузки видео

## 📋 Содержание

1. [Предварительные требования](#1-предварительные-требования)
2. [Создание TikTok приложения](#2-создание-tiktok-приложения)
3. [Настройка Content Posting API](#3-настройка-content-posting-api)
4. [Получение Access Token](#4-получение-access-token)
5. [Настройка .env файла](#5-настройка-env-файла)
6. [Тестирование](#6-тестирование)
7. [Использование](#7-использование)
8. [FAQ](#faq)

---

## ⚠️ Важная информация

### Региональные ограничения

- **Россия**: TikTok ограничил загрузку видео с марта 2022 года
- **Решение**: Используйте VPN для доступа к TikTok API
- **Рекомендация**: Все действия (регистрация, OAuth, загрузка) выполняйте с включенным VPN

### Требования к видео

- **Формат**: MP4 (рекомендуется)
- **Максимальный размер**: 4 ГБ
- **Максимальная длительность**: 10 минут
- **Рекомендуемое соотношение сторон**: 9:16 (вертикальное видео)
- **Минимальное разрешение**: 720x1280
- **Кодек**: H.264/H.265

---

## 1. Предварительные требования

Перед началом убедитесь, что у вас есть:

- ✅ TikTok аккаунт (личный или бизнес)
- ✅ Доступ к https://developers.tiktok.com/
- ✅ VPN (для пользователей из России)
- ✅ Python 3.11+ установлен
- ✅ Библиотека `requests` установлена

```bash
pip install requests
```

---

## 2. Создание TikTok приложения

### Шаг 2.1: Регистрация на TikTok for Developers

1. **Включите VPN** (если находитесь в России)
2. Откройте **https://developers.tiktok.com/**
3. Нажмите **"Login"** и войдите через ваш TikTok аккаунт
4. Подтвердите email (если требуется)

### Шаг 2.2: Подготовка Terms of Service и Privacy Policy

TikTok требует публичные URL для Terms of Service и Privacy Policy. Мы уже подготовили эти документы.

**Вариант А: Использование GitHub Pages (Рекомендуется)**

1. Убедитесь, что файлы `terms-of-service.html` и `privacy-policy.html` находятся в папке `static/`
2. Откройте GitHub → Settings вашего репозитория
3. Прокрутите до раздела **"Pages"**
4. В разделе **"Source"** выберите:
   - Branch: `main` (или `master`)
   - Folder: `/ (root)`
5. Нажмите **"Save"**
6. Дождитесь деплоя (обычно 1-2 минуты)
7. GitHub предоставит вам URL вида: `https://your-username.github.io/fanout-publisher/`

Теперь ваши документы будут доступны по адресам:
- **Terms of Service**: `https://your-username.github.io/fanout-publisher/static/terms-of-service.html`
- **Privacy Policy**: `https://your-username.github.io/fanout-publisher/static/privacy-policy.html`

**Вариант Б: Локальное тестирование**

Для разработки можно использовать локальные URL (но TikTok может потребовать публичные URL):
- `http://localhost:8000/terms-of-service.html`
- `http://localhost:8000/privacy-policy.html`

> 💡 **Совет**: Замените `your-username` на ваше имя пользователя GitHub в файлах HTML (раздел контактов).

### Шаг 2.3: Создание приложения

1. После входа перейдите в **"Manage apps"**
2. Нажмите **"Create an app"** (или "Connect an app")
3. Заполните форму создания приложения:

   **Основная информация:**
   - **App name**: `Fanout Publisher` (или любое другое)
   - **App type**: выберите **"Web App"**
   - **Category**: `Video Tools` или `Social Media`
   - **App description**: `Video publishing tool for multiple platforms`
   
   **Обязательные поля:**
   - **Terms of Service URL**: `https://your-username.github.io/fanout-publisher/static/terms-of-service.html`
   - **Privacy Policy URL**: `https://your-username.github.io/fanout-publisher/static/privacy-policy.html`
   
   ⚠️ **Замените `your-username`** на ваше фактическое имя пользователя GitHub!

4. Нажмите **"Submit"** или "Create"
5. Подтвердите условия использования

### Шаг 2.4: Получение Client Key и Client Secret

После создания приложения:

1. Перейдите в настройки созданного приложения
2. В разделе **"Basic Information"** найдите:
   - **Client Key** - скопируйте и сохраните
   - **Client Secret** - нажмите "Show" и скопируйте

> 💡 **Важно**: Client Secret показывается только один раз! Сохраните его в надежном месте.

---

## 3. Настройка Content Posting API

### Шаг 3.1: Добавление продуктов

1. В настройках приложения перейдите в раздел **"Add products"**
2. Найдите и добавьте следующие продукты:
   - **Login Kit** - для OAuth авторизации
   - **Content Posting API** - для загрузки видео

### Шаг 3.2: Настройка Login Kit

1. Перейдите в **"Login Kit"** → **"Settings"**
2. В разделе **"Redirect URL"** добавьте:
   ```
   http://localhost:8080/callback
   ```
3. Нажмите **"Save"**

### Шаг 3.3: Настройка Content Posting API

1. Перейдите в **"Content Posting API"** → **"Settings"**
2. Активируйте следующие **Scopes**:
   - `user.info.basic` - базовая информация о пользователе
   - `video.upload` - загрузка видео
   - `video.publish` - публикация видео

3. Нажмите **"Save"**

> ℹ️ **Примечание**: Некоторые scopes могут требовать одобрения TikTok. Для тестирования базовые scopes обычно доступны сразу.

---

## 4. Получение Access Token

### Вариант 1: Автоматический (рекомендуется)

Используйте готовый скрипт:

```bash
# Убедитесь, что включен VPN (для РФ)
# Установите зависимости
pip install requests

# Запустите скрипт
python scripts/get_tiktok_token.py

# Следуйте инструкциям в терминале:
# 1. Введите Client Key
# 2. Введите Client Secret
# 3. Откроется браузер для авторизации
# 4. Разрешите доступ к вашему TikTok аккаунту
# 5. Токен появится в терминале
```

### Вариант 2: Вручную (сложно)

Если автоматический способ не работает, следуйте официальной документации:
https://developers.tiktok.com/doc/content-posting-api-get-started

---

## 5. Настройка .env файла

Откройте файл `.env` в корне проекта и добавьте/обновите:

```bash
# ===== TikTok API =====
TIKTOK_CLIENT_KEY=ваш-client-key
TIKTOK_CLIENT_SECRET=ваш-client-secret
TIKTOK_ACCESS_TOKEN=ваш-access-token

# Приватность по умолчанию
# SELF_ONLY - только автор (приватное)
# MUTUAL_FOLLOW_FRIENDS - взаимные подписчики
# FOLLOWER_OF_CREATOR - все подписчики
# PUBLIC_TO_EVERYONE - публичное
TIKTOK_DEFAULT_PRIVACY=SELF_ONLY

# Отключить функции (true/false)
TIKTOK_DISABLE_DUET=false        # Запретить дуэты
TIKTOK_DISABLE_COMMENT=false     # Запретить комментарии
TIKTOK_DISABLE_STITCH=false      # Запретить стичи
```

### Параметры:

- **TIKTOK_CLIENT_KEY** ⚠️ **ОБЯЗАТЕЛЬНО** - Client Key из шага 2.3
- **TIKTOK_CLIENT_SECRET** ⚠️ **ОБЯЗАТЕЛЬНО** - Client Secret из шага 2.3
- **TIKTOK_ACCESS_TOKEN** ⚠️ **ОБЯЗАТЕЛЬНО** - Access Token из шага 4
- **TIKTOK_DEFAULT_PRIVACY** - уровень приватности по умолчанию
- **TIKTOK_DISABLE_DUET** - запретить создание дуэтов с вашим видео
- **TIKTOK_DISABLE_COMMENT** - отключить комментарии
- **TIKTOK_DISABLE_STITCH** - запретить использование в стичах

---

## 6. Тестирование

### Шаг 6.1: Подготовка тестового видео

Создайте короткое тестовое видео:
- Формат: MP4
- Длительность: 5-30 секунд
- Соотношение сторон: 9:16 (вертикальное)
- Разрешение: минимум 720x1280

### Шаг 6.2: Запуск тестового скрипта

```bash
# ВАЖНО: Включите VPN перед тестированием!

# С указанием пути к видео
python scripts/test_tiktok_upload.py path/to/test_video.mp4

# Или без аргументов (будет запрошено)
python scripts/test_tiktok_upload.py
```

### Шаг 6.3: Проверка результата

1. Скрипт выведет `publish_id` загруженного видео
2. Откройте TikTok приложение на телефоне
3. Перейдите в "Профиль" → "Черновики"
4. Проверьте что видео загружено в приватном режиме

> ⚠️ **Важно**: TikTok обрабатывает видео асинхронно. Видео может появиться в черновиках через 1-5 минут.

---

## 7. Использование

### Через веб-интерфейс

1. **Включите VPN** (если в России)
2. Откройте http://localhost:8000
3. Выберите платформу **"TikTok"**
4. Загрузите видео (желательно вертикальное 9:16)
5. Заполните описание (caption)
6. Выберите приватность
7. Нажмите **"Загрузить на TikTok"**
8. Дождитесь завершения обработки

### Через API

```bash
curl -X POST http://localhost:8000/upload \
  -H "Content-Type: multipart/form-data" \
  -F "video=@vertical_video.mp4" \
  -F "title=Мой TikTok" \
  -F "description=Описание с #хештегами" \
  -F "platform=tiktok" \
  -F "privacy=private"
```

---

## FAQ

### ❓ Нужен ли VPN для работы с TikTok API из России?

**Да!** TikTok ограничил доступ из России с марта 2022 года. Все операции (OAuth, загрузка видео) требуют VPN.

Рекомендуемые VPN:
- Расположение сервера: США, Европа, Сингапур
- Убедитесь что VPN работает стабильно

### ❓ Какие права нужны для токена?

Access Token должен иметь следующие scopes:
- `user.info.basic` - базовая информация
- `video.upload` - загрузка видео
- `video.publish` - публикация видео

### ❓ Как долго действителен Access Token?

- **Access Token**: обычно 24 часа (86400 секунд)
- **Refresh Token**: можно использовать для обновления
- После истечения нужно получить новый токен

### ❓ Можно ли загружать горизонтальные видео?

Технически - да, но **не рекомендуется**:
- TikTok оптимизирован для вертикальных видео (9:16)
- Горизонтальные видео будут обрезаны или плохо отображаться
- Рекомендуемое разрешение: 1080x1920

### ❓ Ошибка "Invalid client_key"

Возможные причины:
1. Неверный Client Key
2. Приложение не активировано
3. VPN отключен (для РФ)

**Решение**:
1. Проверьте Client Key в настройках TikTok app
2. Убедитесь что приложение активно
3. Включите VPN

### ❓ Видео не появляется в TikTok

TikTok обрабатывает видео асинхронно:
1. После загрузки статус будет `PROCESSING_UPLOAD`
2. Обработка занимает 1-10 минут
3. После обработки видео появится в черновиках (если приватное)
4. Проверьте статус через `get_video_status()`

### ❓ Ошибка "Scope not authorized"

Некоторые scopes требуют одобрения от TikTok:
1. Базовые scopes (`user.info.basic`, `video.upload`) обычно доступны сразу
2. Для production может потребоваться App Review
3. Подайте заявку на проверку в TikTok Developer Portal

### ❓ Можно ли загружать видео на бизнес-аккаунт?

Да! Content Posting API работает как с личными, так и с бизнес-аккаунтами TikTok.

### ❓ Как обновить истекший Access Token?

Используйте Refresh Token:

```python
# В разработке - функция refresh_token
# Или запустите get_tiktok_token.py снова
```

### ❓ Лимиты API

TikTok устанавливает следующие лимиты:
- **Загрузка видео**: до 5 видео в день (может меняться)
- **Размер файла**: максимум 4 ГБ
- **Длительность**: максимум 10 минут
- **Rate limits**: проверьте текущие в документации

---

## 🎯 Быстрый чеклист

- [ ] Создан TikTok Developer аккаунт
- [ ] Создано приложение
- [ ] Добавлены Login Kit и Content Posting API
- [ ] Настроен Redirect URI
- [ ] Активированы необходимые scopes
- [ ] Получен Client Key и Client Secret
- [ ] Получен Access Token (через скрипт)
- [ ] Токены добавлены в `.env` файл
- [ ] VPN включен (для РФ)
- [ ] Запущен тестовый скрипт
- [ ] Тестовое видео успешно загружено
- [ ] Проверено в TikTok приложении
- [ ] Готово к использованию! 🎉

---

## 📚 Полезные ссылки

- [TikTok for Developers](https://developers.tiktok.com/) - **Главная страница**
- [Content Posting API Docs](https://developers.tiktok.com/doc/content-posting-api-overview) - Документация
- [OAuth 2.0 Guide](https://developers.tiktok.com/doc/oauth-user-access-token-management) - OAuth документация
- [API Reference](https://developers.tiktok.com/doc/content-posting-api-reference-upload-video) - Справочник API
- [Rate Limits](https://developers.tiktok.com/doc/content-posting-api-rate-limits) - Лимиты API

---

## 🆘 Поддержка

Если возникли проблемы:

1. **Проверьте VPN** (для РФ) - должен быть включен
2. **Проверьте логи**: `docker-compose logs -f worker`
3. **Убедитесь в правильности токенов** в `.env`
4. **Проверьте срок действия** Access Token
5. **Запустите тестовый скрипт** для диагностики

### Типичные ошибки

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `Invalid client_key` | Неверный Client Key | Проверьте в TikTok Developer Portal |
| `Unauthorized` | Токен истёк | Получите новый токен |
| `Network error` | VPN отключен | Включите VPN (для РФ) |
| `File too large` | Файл > 4 ГБ | Сожмите видео |
| `Invalid video format` | Неподдерживаемый формат | Используйте MP4 H.264 |

---

## ⚠️ Важные замечания

### Для пользователей из России:

1. **Всегда используйте VPN** при работе с TikTok API
2. Выбирайте стабильные VPN-серверы (США, Европа)
3. Проверяйте, что VPN работает перед каждой загрузкой

### Приватность и безопасность:

1. **Никогда не коммитьте** `.env` файл в git
2. **Не делитесь** Client Secret и Access Token
3. Для тестов используйте **приватные** видео (`SELF_ONLY`)
4. Регулярно обновляйте токены

### Production:

1. Рассмотрите получение **долгосрочных токенов**
2. Подайте заявку на **App Review** для снятия ограничений
3. Настройте **мониторинг** истечения токенов
4. Реализуйте **автообновление** через Refresh Token

---

**Готово!** Теперь вы можете загружать видео на TikTok через Fanout Publisher! 🚀

> 💡 **Совет**: Начните с тестовых приватных видео, чтобы убедиться что всё работает правильно.


