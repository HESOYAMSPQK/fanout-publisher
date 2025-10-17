# 🚀 Настройка GitHub Pages для Fanout Publisher

Это краткое руководство поможет вам развернуть Terms of Service и Privacy Policy на GitHub Pages для использования в приложениях TikTok, VK и YouTube.

---

## 📋 Что такое GitHub Pages?

GitHub Pages - это бесплатный хостинг статических сайтов от GitHub. Идеально подходит для размещения документации, политики конфиденциальности и условий использования.

**Преимущества:**
- ✅ Полностью бесплатно
- ✅ Автоматический HTTPS
- ✅ Простая настройка
- ✅ Интеграция с Git
- ✅ Поддержка пользовательских доменов

---

## 🔧 Быстрая настройка

### Шаг 1: Подготовка файлов

Убедитесь, что в папке `static/` вашего репозитория есть файлы:
```
static/
├── terms-of-service.html
├── privacy-policy.html
├── index.html
├── script.js
└── style.css
```

### Шаг 2: Обновление контактной информации

**Важно!** Откройте файлы и замените `your-username` на ваше реальное имя пользователя GitHub:

1. Откройте `static/terms-of-service.html`
2. Найдите строку с `https://github.com/your-username/fanout-publisher`
3. Замените `your-username` на ваш GitHub username

Повторите для `static/privacy-policy.html`.

### Шаг 3: Коммит и пуш

```bash
# Добавьте файлы в git
git add static/terms-of-service.html static/privacy-policy.html

# Сделайте коммит
git commit -m "Add Terms of Service and Privacy Policy for platform integrations"

# Отправьте на GitHub
git push origin main
```

### Шаг 4: Включение GitHub Pages

1. Откройте ваш репозиторий на GitHub
2. Перейдите в **Settings** (⚙️)
3. В левом меню найдите раздел **Pages**
4. В разделе **Source** выберите:
   - **Branch**: `main` (или `master`)
   - **Folder**: `/ (root)`
5. Нажмите **Save**

### Шаг 5: Дождитесь деплоя

1. GitHub начнет сборку сайта (обычно 1-2 минуты)
2. После завершения вы увидите зеленое уведомление:
   ```
   Your site is live at https://your-username.github.io/fanout-publisher/
   ```
3. Скопируйте этот URL

### Шаг 6: Проверьте доступность

Откройте в браузере:
- **Terms of Service**: `https://your-username.github.io/fanout-publisher/static/terms-of-service.html`
- **Privacy Policy**: `https://your-username.github.io/fanout-publisher/static/privacy-policy.html`

Если страницы открываются - всё работает! 🎉

---

## 📝 Использование в приложениях

### TikTok Developer Portal

При создании приложения используйте:
- **Terms of Service URL**: `https://your-username.github.io/fanout-publisher/static/terms-of-service.html`
- **Privacy Policy URL**: `https://your-username.github.io/fanout-publisher/static/privacy-policy.html`

### VK Developer Portal

Аналогично укажите эти URL в настройках приложения VK.

### YouTube API Console

Google также требует эти документы при регистрации приложения.

---

## 🔄 Обновление документов

Если вы изменили файлы:

```bash
# Внесите изменения в файлы
# Сохраните и закоммитьте

git add static/terms-of-service.html static/privacy-policy.html
git commit -m "Update Terms of Service and Privacy Policy"
git push origin main

# GitHub Pages автоматически обновится через 1-2 минуты
```

---

## 🌐 Использование собственного домена (опционально)

Если у вас есть свой домен (например, `myapp.com`):

### Шаг 1: Добавьте CNAME файл

Создайте файл `static/CNAME` с содержимым:
```
docs.myapp.com
```

### Шаг 2: Настройте DNS

В настройках вашего домена добавьте CNAME запись:
```
docs.myapp.com → your-username.github.io
```

### Шаг 3: Укажите домен в GitHub

1. Settings → Pages
2. Custom domain: `docs.myapp.com`
3. Save

Теперь документы будут доступны по адресу:
- `https://docs.myapp.com/static/terms-of-service.html`
- `https://docs.myapp.com/static/privacy-policy.html`

---

## 🐛 Устранение проблем

### Ошибка 404 - страница не найдена

**Причины:**
1. GitHub Pages еще не развернут (подождите 2-5 минут)
2. Неправильный URL (проверьте путь)
3. Файлы не закоммичены в ветку `main`

**Решение:**
```bash
# Проверьте, что файлы в репозитории
git status

# Если файлы не добавлены:
git add static/*.html
git commit -m "Add policy files"
git push origin main
```

### Изменения не отображаются

**Причина:** Кэширование браузера или GitHub

**Решение:**
1. Очистите кэш браузера (Ctrl+F5)
2. Подождите 5 минут для обновления GitHub Pages
3. Проверьте коммит в репозитории

### GitHub Pages не активируется

**Причина:** Репозиторий приватный (для бесплатных аккаунтов)

**Решение:**
1. Settings → General
2. Прокрутите вниз до "Danger Zone"
3. Change visibility → Make public
4. Или используйте GitHub Pro (Pages работает с приватными репозиториями)

### Страница показывает код вместо HTML

**Причина:** Файл имеет неправильное расширение или не содержит HTML

**Решение:**
1. Убедитесь, что файлы имеют расширение `.html`
2. Первая строка должна быть `<!DOCTYPE html>`
3. Проверьте содержимое файла

---

## 📚 Дополнительные ресурсы

- [GitHub Pages документация](https://docs.github.com/en/pages)
- [Настройка пользовательского домена](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [Устранение проблем GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/troubleshooting-404-errors-for-github-pages-sites)

---

## ✅ Чек-лист

Перед использованием убедитесь:

- [ ] Файлы `terms-of-service.html` и `privacy-policy.html` находятся в папке `static/`
- [ ] В файлах заменен `your-username` на ваш GitHub username
- [ ] Файлы закоммичены и отправлены на GitHub (`git push`)
- [ ] GitHub Pages включен в настройках репозитория
- [ ] Сайт успешно развернут (зеленое уведомление)
- [ ] Страницы открываются в браузере
- [ ] URL скопированы для использования в TikTok/VK/YouTube

---

## 🎯 Что дальше?

После настройки GitHub Pages:

1. Вернитесь к **TIKTOK_SETUP_GUIDE.md** для завершения настройки TikTok
2. Используйте те же URL для **VK_SETUP_GUIDE.md**
3. При необходимости адаптируйте документы под свои нужды

**Готово!** Теперь у вас есть публичные URL для Terms of Service и Privacy Policy. 🚀

