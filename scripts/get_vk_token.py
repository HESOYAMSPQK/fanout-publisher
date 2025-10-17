#!/usr/bin/env python3
"""
Скрипт для получения VK Access Token

Этот скрипт поможет вам получить постоянный access token для VK API,
который можно использовать для загрузки видео.

Инструкция:
1. Создайте Standalone-приложение на https://id.vk.com/
   (С 2024 года VK переместил создание приложений на платформу VK ID)
2. Запустите этот скрипт и следуйте инструкциям
3. Скопируйте полученный access_token в .env файл
"""

import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

# Конфигурация
VK_APP_ID = None  # Будет запрошен у пользователя
VK_REDIRECT_URI = 'https://oauth.vk.com/blank.html'  # Официальный redirect URI VK

# Permissions (scope) для VK API
# video - загрузка видео
# offline - постоянный токен (не истекает)
SCOPE = 'video,offline'

# Переменная для хранения токена
access_token = None


def get_token_from_browser():
    """Получить токен через браузер (пользователь копирует вручную)"""
    print("\n" + "="*60)
    print("📋 Как получить Access Token:")
    print("="*60)
    print()
    print("1. После авторизации вы будете перенаправлены на:")
    print("   https://oauth.vk.com/blank.html#access_token=...")
    print()
    print("2. В адресной строке браузера скопируйте всё, что идёт")
    print("   ПОСЛЕ '#access_token=' и ДО '&expires_in'")
    print()
    print("3. Пример URL:")
    print("   https://oauth.vk.com/blank.html#access_token=vk1.a.ABCD...XYZ&expires_in=0&user_id=123456")
    print()
    print("4. Скопируйте только токен:")
    print("   vk1.a.ABCD...XYZ")
    print()
    print("="*60)
    print()
    
    # Ждем, пока пользователь скопирует токен
    access_token = input("Вставьте Access Token сюда: ").strip()
    
    if not access_token:
        print("❌ Токен не может быть пустым!")
        return None
    
    # Проверяем формат токена
    if not (access_token.startswith('vk1.') or len(access_token) > 50):
        print("⚠️  Предупреждение: токен выглядит подозрительно коротким.")
        confirm = input("Продолжить? (y/n): ").lower()
        if confirm != 'y':
            return None
    
    return access_token


def get_vk_access_token():
    """Получить VK Access Token через OAuth"""
    global VK_APP_ID
    
    print("="*60)
    print("🔑 Получение VK Access Token")
    print("="*60)
    print()
    
    # Шаг 1: Получить APP ID
    print("📱 Шаг 1: Создание VK приложения через VK ID")
    print("-" * 60)
    print("1. Откройте: https://id.vk.com/")
    print("2. Нажмите 'Создать приложение'")
    print("3. Тип приложения: 'Standalone-приложение'")
    print("4. Название: 'Fanout Publisher' (или любое другое)")
    print("5. Категория: 'Образ жизни' или 'Другое'")
    print("6. После создания перейдите в 'Настройки'")
    print("7. Скопируйте 'ID приложения'")
    print()
    print("ℹ️  С 2024 года VK переместил создание приложений на платформу VK ID!")
    print()
    
    VK_APP_ID = input("Введите ID приложения: ").strip()
    
    if not VK_APP_ID:
        print("❌ Ошибка: APP ID не может быть пустым")
        sys.exit(1)
    
    print()
    print("📝 Шаг 2: Настройка Redirect URI")
    print("-" * 60)
    print("1. В форме создания приложения заполните:")
    print("   - Базовый домен: oauth.vk.com")
    print("   - Доверенный Redirect URI: https://oauth.vk.com/blank.html")
    print("2. Нажмите 'Создать приложение'")
    print("3. После создания скопируйте 'ID приложения'")
    print()
    print("ℹ️  С 2024 года VK требует HTTPS для Redirect URI!")
    print()
    
    input("Нажмите Enter когда создадите приложение и скопируете ID... ")
    
    # Шаг 2: Формируем OAuth URL
    print()
    print("🌐 Шаг 3: Авторизация")
    print("-" * 60)
    
    auth_params = {
        'client_id': VK_APP_ID,
        'display': 'page',
        'redirect_uri': VK_REDIRECT_URI,
        'scope': SCOPE,
        'response_type': 'token',  # Implicit Flow - токен в fragment
        'v': '5.131'
    }
    
    auth_url = f"https://oauth.vk.com/authorize?{urllib.parse.urlencode(auth_params)}"
    
    print("Сейчас откроется браузер для авторизации...")
    print(f"Если не открылся, перейдите по ссылке вручную:")
    print()
    print(auth_url)
    print()
    
    # Открываем браузер
    webbrowser.open(auth_url)
    
    print("⏳ Ожидание авторизации в браузере...")
    print()
    
    # Получаем токен от пользователя (он скопирует из URL)
    access_token = get_token_from_browser()
    
    if access_token:
        print("\n" + "="*60)
        print("✅ VK Access Token успешно получен!")
        print("="*60)
        print(f"\nAccess Token:")
        print(access_token)
        print("\n" + "="*60)
        print("📋 Скопируйте Access Token и добавьте в .env файл:")
        print(f"VK_ACCESS_TOKEN={access_token}")
        print("="*60 + "\n")
        print("\n💡 Совет: Этот токен бессрочный, сохраните его в надежном месте!")
        return access_token
    else:
        print("\n❌ Ошибка: не удалось получить токен")
        print("Попробуйте еще раз или проверьте настройки приложения")
        sys.exit(1)


def main():
    """Главная функция"""
    try:
        get_vk_access_token()
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

