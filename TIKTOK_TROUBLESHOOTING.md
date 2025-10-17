# 🔧 Решение проблемы 403 Forbidden при загрузке видео в TikTok

## 🎯 Проблема
При попытке загрузки видео получаете ошибку:
```
Ошибка: TikTok API request failed: 403 Client Error: Forbidden for url: 
https://open.tiktokapis.com/v2/post/publish/video/init/
```

## ✅ Пошаговое решение

### 1. Проверьте настройки приложения TikTok

Откройте [TikTok Developer Portal](https://developers.tiktok.com/) и проверьте:

#### 1.1 Тип приложения
1. Откройте ваше приложение
2. Убедитесь, что это **Web App** или **Third-party App**
3. Проверьте, что включен **Login Kit**

#### 1.2 Redirect URI
1. Перейдите в: **Login Kit → Redirect URLs**
2. **ОБЯЗАТЕЛЬНО**: Redirect URI должен быть **HTTPS** (не HTTP!)
3. Варианты настройки:
   
   **Для локальной разработки (рекомендуется):**
   ```
   https://ваш-ngrok-url.ngrok.io/callback
   ```
   ⚠️ **Важно**: ngrok URL меняется при каждом запуске (если нет платного аккаунта)
   
   **Для продакшена:**
   ```
   https://ваш-домен.com/oauth/tiktok/callback
   ```

#### 1.3 Scopes (Права доступа)
В разделе **Login Kit → Scopes** должны быть включены:
- ✅ `user.info.basic` - базовая информация
- ✅ `video.upload` - загрузка видео
- ✅ `video.publish` - публикация видео

⚠️ **ВАЖНО**: Если вы изменили scopes - нужно **заново получить токен**!

#### 1.4 Content Posting API
1. Перейдите в раздел **Products**
2. Убедитесь, что подключен **Content Posting API**
3. Если его нет - подайте заявку на доступ

---

### 2. Получите новый токен с правильными настройками

#### Вариант A: Через ngrok (HTTPS туннель) - РЕКОМЕНДУЕТСЯ

1. **Установите ngrok** (если еще не установлен):
   ```powershell
   # Через Chocolatey
   choco install ngrok
   
   # Или скачайте с https://ngrok.com/download
   ```

2. **Зарегистрируйтесь на ngrok.com** (бесплатно):
   - Откройте: https://dashboard.ngrok.com/signup
   - Получите authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
   - Настройте authtoken:
     ```powershell
     ngrok config add-authtoken ваш-токен
     ```

3. **Запустите скрипт получения токена**:
   ```powershell
   python scripts/get_tiktok_token_ngrok.py
   ```

4. **Следуйте инструкциям**:
   - Скрипт запустит ngrok и покажет HTTPS URL
   - Добавьте этот URL в TikTok Developer Portal (Redirect URLs)
   - Авторизуйтесь через браузер
   - Скрипт автоматически сохранит токен в `.env`

#### Вариант B: Через продакшен сервер (HTTPS)

Если у вас есть сервер с HTTPS:
1. Настройте redirect URI: `https://ваш-домен.com/oauth/tiktok/callback`
2. Добавьте его в TikTok Developer Portal
3. Используйте стандартный OAuth 2.0 flow

---

### 3. Проверьте ваш токен

После получения токена проверьте его:

```python
# Запустите тестовый скрипт
python scripts/test_tiktok_upload.py
```

Или вручную проверьте информацию о пользователе:

```python
import requests

access_token = "ваш-токен"

headers = {
    'Authorization': f'Bearer {access_token}',
}

response = requests.get(
    'https://open.tiktokapis.com/v2/user/info/',
    headers=headers,
    params={'fields': 'open_id,union_id,avatar_url,display_name'}
)

print(response.json())
```

Если получите ошибку - токен недействителен или истек.

---

### 4. Настройте автоматическое обновление токена

В `.env` файле **ОБЯЗАТЕЛЬНО** добавьте `TIKTOK_REFRESH_TOKEN`:

```env
TIKTOK_CLIENT_KEY=ваш-client-key
TIKTOK_CLIENT_SECRET=ваш-client-secret
TIKTOK_ACCESS_TOKEN=ваш-access-token
TIKTOK_REFRESH_TOKEN=ваш-refresh-token    # ← ВАЖНО!
```

Refresh token позволит системе автоматически обновлять access token при истечении срока действия.

---

## 🔍 Частые ошибки и их решение

### Ошибка: "redirect_uri mismatch"
**Причина**: redirect_uri в запросе не совпадает с настройками в TikTok Developer Portal

**Решение**:
1. Скопируйте ТОЧНЫЙ redirect_uri из скрипта (включая протокол https://)
2. Вставьте его в TikTok Developer Portal → Login Kit → Redirect URLs
3. Дождитесь сохранения (может занять несколько секунд)
4. Попробуйте снова

### Ошибка: "invalid_scope"
**Причина**: Запрашиваемые scopes не включены в настройках приложения

**Решение**:
1. Откройте TikTok Developer Portal
2. Login Kit → Scopes → Включите: `user.info.basic`, `video.upload`, `video.publish`
3. Сохраните
4. **Получите токен заново** (старый токен имеет старые scopes!)

### Ошибка: 403 Forbidden
**Причина**: Один из случаев:
- Токен истек
- Токен получен без нужных scopes
- Приложение не имеет доступа к Content Posting API

**Решение**:
1. Проверьте scopes (см. выше)
2. Убедитесь, что Content Posting API подключен
3. Получите новый токен
4. Добавьте TIKTOK_REFRESH_TOKEN для автоматического обновления

---

## 🎯 Ответ на вопрос про localhost и HTTP vs HTTPS

### Влияет ли localhost через HTTP на загрузку видео?

**Краткий ответ: НЕТ, но влияет на получение токена!**

**Подробно**:

1. **При загрузке видео** (ваша текущая ошибка 403):
   - API запросы идут к `https://open.tiktokapis.com` (HTTPS)
   - Ваш сервер (localhost HTTP или HTTPS) НЕ влияет на эти запросы
   - Ошибка 403 связана с **токеном доступа**, а не с вашим сервером

2. **При получении токена** (OAuth авторизация):
   - ⚠️ **TikTok ТРЕБУЕТ HTTPS для redirect_uri**
   - `http://localhost:8080/callback` - ❌ **НЕ будет работать**
   - `https://ngrok-url.ngrok.io/callback` - ✅ **Работает через ngrok**
   - Поэтому используется ngrok для создания HTTPS туннеля

**Вывод**: Ваша проблема связана НЕ с тем, что вы загружаете с localhost, а с тем, что:
- Токен был получен неправильно (не через HTTPS)
- Или токен не имеет нужных scopes
- Или токен истек

---

## 📋 Чек-лист проверки

Перед загрузкой видео убедитесь:

- [ ] В TikTok Developer Portal включен Content Posting API
- [ ] В Login Kit → Scopes включены: `user.info.basic`, `video.upload`, `video.publish`
- [ ] В Login Kit → Redirect URLs добавлен HTTPS redirect URI (ngrok или домен)
- [ ] Токен получен через HTTPS redirect URI (ngrok)
- [ ] В `.env` файле указаны все необходимые переменные:
  - [ ] `TIKTOK_CLIENT_KEY`
  - [ ] `TIKTOK_CLIENT_SECRET`
  - [ ] `TIKTOK_ACCESS_TOKEN`
  - [ ] `TIKTOK_REFRESH_TOKEN` (для автообновления)
- [ ] Токен не истек (проверьте дату получения)

---

## 🆘 Дополнительная помощь

Если проблема не решается:

1. **Проверьте логи**:
   ```bash
   docker-compose logs worker
   ```

2. **Включите отладку**:
   В `platforms/tiktok.py` строка 184 логирует отправляемые данные

3. **Создайте тестовый запрос**:
   ```bash
   python scripts/test_tiktok_upload.py
   ```

4. **Проверьте статус приложения TikTok**:
   - Приложение должно быть в статусе "Live" или "In development"
   - Проверьте, нет ли ограничений или блокировок

---

## 📚 Полезные ссылки

- [TikTok Developer Portal](https://developers.tiktok.com/)
- [TikTok Content Posting API Docs](https://developers.tiktok.com/doc/content-posting-api-get-started/)
- [ngrok Documentation](https://ngrok.com/docs)
- [OAuth 2.0 Spec](https://oauth.net/2/)

---

**Последнее обновление**: 2025-10-17

