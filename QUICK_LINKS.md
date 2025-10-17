# 🔗 Быстрые ссылки для настройки платформ

> Шпаргалка с важными URL для регистрации приложений

---

## 📝 Ваши URL для Terms of Service и Privacy Policy

После деплоя на GitHub Pages используйте эти URL:

```
Terms of Service:
https://your-username.github.io/fanout-publisher/static/terms-of-service.html

Privacy Policy:
https://your-username.github.io/fanout-publisher/static/privacy-policy.html
```

⚠️ **Замените `your-username`** на ваше реальное имя пользователя GitHub!

---

## 🎯 Где использовать эти URL

### TikTok Developer Portal
- **URL**: https://developers.tiktok.com/
- **Куда вставить**: При создании приложения в разделе "Basic Information"
- **Поля**: Terms of Service URL, Privacy Policy URL
- **Руководство**: [TIKTOK_SETUP_GUIDE.md](TIKTOK_SETUP_GUIDE.md)

### VK Developer Portal
- **URL**: https://dev.vk.com/
- **Куда вставить**: В настройках приложения (если требуется)
- **Руководство**: [VK_SETUP_GUIDE.md](VK_SETUP_GUIDE.md)

### YouTube API Console
- **URL**: https://console.cloud.google.com/
- **Куда вставить**: OAuth consent screen
- **Поля**: Terms of service, Privacy policy
- **Руководство**: WEB_VERSION_README.md

---

## 🚀 Быстрая настройка GitHub Pages

```bash
# 1. Закоммитьте файлы
git add static/terms-of-service.html static/privacy-policy.html
git commit -m "Add Terms of Service and Privacy Policy"
git push origin main

# 2. Включите GitHub Pages
# GitHub → Repository Settings → Pages
# Source: main branch, / (root)
# Save
```

**Подробнее**: [GITHUB_PAGES_SETUP.md](GITHUB_PAGES_SETUP.md)

---

## ✅ Проверка работоспособности

После деплоя откройте в браузере:

```
https://your-username.github.io/fanout-publisher/static/terms-of-service.html
https://your-username.github.io/fanout-publisher/static/privacy-policy.html
```

Если страницы открываются - всё готово! 🎉

---

## 🔧 Redirect URLs для OAuth

### TikTok
```
http://localhost:8080/callback
```

### VK
```
http://localhost:8080/vk_callback
```

### YouTube
```
http://localhost:8080/oauth2callback
```

---

## 📋 Полезные команды

### Запуск локально
```bash
# С Docker
docker-compose up

# Без Docker
python -m uvicorn app.main:app --reload --port 8000
```

### Тестирование токенов
```bash
# TikTok
python scripts/get_tiktok_token.py

# VK
python scripts/get_vk_token.py

# YouTube
python scripts/get_youtube_token.py
```

### Проверка API
```bash
# Windows
scripts\check_local_api.bat

# Linux/Mac
bash scripts/check_local_api.sh
```

---

## 📚 Документация

| Документ | Описание |
|----------|----------|
| [README.md](README.md) | Главная документация проекта |
| [QUICK_START_WEB.md](QUICK_START_WEB.md) | Быстрый старт за 5 минут |
| [GITHUB_PAGES_SETUP.md](GITHUB_PAGES_SETUP.md) | Настройка GitHub Pages |
| [TIKTOK_SETUP_GUIDE.md](TIKTOK_SETUP_GUIDE.md) | Подробная настройка TikTok |
| [TIKTOK_APP_FORM_TEMPLATE.md](TIKTOK_APP_FORM_TEMPLATE.md) | 📋 Готовые значения для формы TikTok |
| [VK_SETUP_GUIDE.md](VK_SETUP_GUIDE.md) | Подробная настройка VK |
| [WEB_VERSION_README.md](WEB_VERSION_README.md) | Полная документация веб-версии |

---

## 🆘 Частые проблемы

### GitHub Pages возвращает 404
- Подождите 2-5 минут после включения
- Проверьте, что файлы закоммичены в ветку `main`
- Убедитесь, что GitHub Pages включен в Settings

### TikTok не принимает URL
- Убедитесь, что URL публично доступен (откройте в браузере)
- Проверьте, что используете HTTPS (GitHub Pages автоматически)
- URL должен возвращать HTML страницу, а не 404

### Токены не работают
- Проверьте, что они правильно сохранены в `.env`
- Убедитесь, что не истёк срок действия токена
- Для VK: проверьте scopes при получении токена
- Для TikTok: используйте VPN если в России

---

**Нужна помощь?** Создайте [issue на GitHub](https://github.com/your-username/fanout-publisher/issues) или обратитесь к документации выше.

