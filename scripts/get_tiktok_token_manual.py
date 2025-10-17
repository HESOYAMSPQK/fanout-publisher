#!/usr/bin/env python3
"""
Получение TikTok Access Token вручную с поддержкой PKCE
"""

import hashlib
import base64
import secrets
import requests
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse

print("=" * 70)
print("🔐 TikTok Access Token - Ручное получение с PKCE")
print("=" * 70)

# Шаг 1: Ввод данных
print("\n📝 Введите данные из TikTok Developer Portal:\n")

CLIENT_KEY = input("Client Key: ").strip()
CLIENT_SECRET = input("Client Secret: ").strip()

if not CLIENT_KEY or not CLIENT_SECRET:
    print("❌ Ошибка: Client Key и Client Secret обязательны!")
    exit(1)

REDIRECT_URI = "http://localhost:8080/callback"
STATE = secrets.token_urlsafe(16)

# Шаг 2: Генерация PKCE code_verifier и code_challenge
print("\n🔐 Генерация PKCE параметров...")

# Code verifier: случайная строка 43-128 символов
code_verifier = secrets.token_urlsafe(64)

# Code challenge: SHA256 hash of code_verifier, base64url encoded
code_challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode('utf-8').rstrip('=')

print(f"✅ Code verifier создан: {code_verifier[:20]}...")
print(f"✅ Code challenge создан: {code_challenge[:20]}...")

# Шаг 3: Создание Authorization URL
print("\n🌐 Создание Authorization URL...")

auth_params = {
    'client_key': CLIENT_KEY,
    'scope': 'user.info.basic,video.upload,video.publish',
    'response_type': 'code',
    'redirect_uri': REDIRECT_URI,
    'state': STATE,
    'code_challenge': code_challenge,
    'code_challenge_method': 'S256'
}

auth_url = f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(auth_params)}"

print("\n" + "=" * 70)
print("📋 ИНСТРУКЦИЯ:")
print("=" * 70)
print("\n1. Сейчас откроется браузер с TikTok авторизацией")
print("2. Войдите в ваш TikTok аккаунт")
print("3. Нажмите 'Authorize' / 'Разрешить'")
print("4. После этого браузер покажет ошибку - ЭТО НОРМАЛЬНО!")
print("5. СКОПИРУЙТЕ ВЕСЬ URL из адресной строки браузера")
print("\n" + "=" * 70)

input("\n🔵 Нажмите Enter чтобы открыть браузер...")

# Открываем браузер
webbrowser.open(auth_url)

print("\n✅ Браузер открыт!")
print("⚠️  После авторизации скопируйте URL из адресной строки браузера\n")

# Шаг 4: Получение callback URL
callback_url = input("📋 Вставьте сюда URL из браузера:\n").strip()

if not callback_url:
    print("❌ URL не введен!")
    exit(1)

# Парсим callback URL
try:
    parsed = urlparse(callback_url)
    params = parse_qs(parsed.query)
    
    if 'code' not in params:
        print("❌ Ошибка: код авторизации не найден в URL!")
        print(f"Полученный URL: {callback_url}")
        exit(1)
    
    authorization_code = params['code'][0]
    print(f"\n✅ Код авторизации получен: {authorization_code[:20]}...")
    
except Exception as e:
    print(f"❌ Ошибка парсинга URL: {e}")
    exit(1)

# Шаг 5: Обмен кода на токен
print("\n🔄 Обмен кода на Access Token...")

token_url = "https://open.tiktokapis.com/v2/oauth/token/"
token_data = {
    'client_key': CLIENT_KEY,
    'client_secret': CLIENT_SECRET,
    'code': authorization_code,
    'grant_type': 'authorization_code',
    'redirect_uri': REDIRECT_URI,
    'code_verifier': code_verifier  # Важно! PKCE verifier
}

try:
    response = requests.post(token_url, data=token_data)
    result = response.json()
    
    print(f"\n📥 Ответ от TikTok (HTTP {response.status_code}):")
    
    if response.status_code == 200 and 'access_token' in result:
        print("\n" + "=" * 70)
        print("🎉 УСПЕХ! Токен получен!")
        print("=" * 70)
        
        access_token = result['access_token']
        refresh_token = result.get('refresh_token', '')
        expires_in = result.get('expires_in', 0)
        
        print(f"\n✅ Access Token:")
        print(f"   {access_token}")
        
        if refresh_token:
            print(f"\n✅ Refresh Token:")
            print(f"   {refresh_token}")
        
        print(f"\n⏰ Срок действия: {expires_in} секунд ({expires_in//3600} часов)")
        
        # Инструкция по сохранению
        print("\n" + "=" * 70)
        print("📝 СКОПИРУЙТЕ В .env ФАЙЛ:")
        print("=" * 70)
        print(f"\nTIKTOK_ACCESS_TOKEN={access_token}")
        if refresh_token:
            print(f"TIKTOK_REFRESH_TOKEN={refresh_token}")
        
        print("\n" + "=" * 70)
        print("🚀 СЛЕДУЮЩИЕ ШАГИ:")
        print("=" * 70)
        print("\n1. Откройте файл .env в корне проекта")
        print("2. Добавьте/обновите строку TIKTOK_ACCESS_TOKEN")
        print("3. Запустите: docker-compose up -d")
        print("4. Тестируйте: python scripts/test_tiktok_upload.py")
        
        # Предложение автоматически обновить .env
        print("\n" + "=" * 70)
        auto_save = input("\n💾 Автоматически обновить .env файл? (y/n): ").strip().lower()
        
        if auto_save == 'y':
            try:
                import os
                from pathlib import Path
                
                env_path = Path('.env')
                
                if env_path.exists():
                    env_content = env_path.read_text(encoding='utf-8')
                else:
                    env_content = ""
                
                # Обновляем или добавляем токены
                lines = env_content.split('\n')
                updated = False
                
                for i, line in enumerate(lines):
                    if line.startswith('TIKTOK_ACCESS_TOKEN='):
                        lines[i] = f'TIKTOK_ACCESS_TOKEN={access_token}'
                        updated = True
                    elif refresh_token and line.startswith('TIKTOK_REFRESH_TOKEN='):
                        lines[i] = f'TIKTOK_REFRESH_TOKEN={refresh_token}'
                
                if not updated:
                    # Добавляем новые строки
                    if env_content and not env_content.endswith('\n'):
                        lines.append('')
                    lines.append(f'TIKTOK_ACCESS_TOKEN={access_token}')
                    if refresh_token:
                        lines.append(f'TIKTOK_REFRESH_TOKEN={refresh_token}')
                
                new_content = '\n'.join(lines)
                env_path.write_text(new_content, encoding='utf-8')
                
                print("✅ Файл .env обновлен!")
                
            except Exception as e:
                print(f"❌ Ошибка сохранения в .env: {e}")
                print("📝 Скопируйте токен вручную")
        
        print("\n✅ Готово! Токен получен успешно!")
        
    else:
        print("\n❌ ОШИБКА получения токена:")
        print("=" * 70)
        
        if 'error' in result:
            print(f"Ошибка: {result['error']}")
        if 'error_description' in result:
            print(f"Описание: {result['error_description']}")
        if 'message' in result:
            print(f"Сообщение: {result['message']}")
        
        print("\nПолный ответ:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n💡 Возможные причины:")
        print("- Неверный Client Key или Client Secret")
        print("- Код авторизации истёк (действует 10 минут)")
        print("- Redirect URI не совпадает с настройками в TikTok Developer Portal")
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ Ошибка сети: {e}")
    print("💡 Проверьте подключение к интернету и VPN (для РФ)")
    
except Exception as e:
    print(f"\n❌ Неожиданная ошибка: {e}")

print("\n" + "=" * 70)
print("📚 Документация: TIKTOK_MANUAL_TOKEN.md")
print("=" * 70)

