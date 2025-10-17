#!/usr/bin/env python3
"""
Получение TikTok Access Token с использованием httpbin.org
Для случаев, когда localhost не работает
"""

import hashlib
import base64
import secrets
import requests
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse

print("=" * 70)
print("🔐 TikTok Access Token - С использованием httpbin.org")
print("=" * 70)
print("\n⚠️  Этот метод использует httpbin.org вместо localhost")
print("Используйте его, если localhost не работает\n")

# Шаг 1: Ввод данных
print("📝 Введите данные из TikTok Developer Portal:\n")

CLIENT_KEY = input("Client Key: ").strip()
CLIENT_SECRET = input("Client Secret: ").strip()

if not CLIENT_KEY or not CLIENT_SECRET:
    print("❌ Ошибка: Client Key и Client Secret обязательны!")
    exit(1)

# ВАЖНО: Нужно добавить этот URL в TikTok Developer Portal!
REDIRECT_URI = "https://httpbin.org/get"
STATE = secrets.token_urlsafe(16)

print("\n" + "=" * 70)
print("⚠️  ВАЖНО! Перед продолжением:")
print("=" * 70)
print("\n1. Откройте TikTok Developer Portal")
print("2. Ваше приложение → Login Kit → Settings")
print("3. Добавьте Redirect URL:")
print(f"   {REDIRECT_URI}")
print("4. Нажмите Save")
print("\n" + "=" * 70)

input("\n🔵 После добавления Redirect URL нажмите Enter...")

# Шаг 2: Генерация PKCE
print("\n🔐 Генерация PKCE параметров...")

code_verifier = secrets.token_urlsafe(64)
code_challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode('utf-8').rstrip('=')

print(f"✅ Code verifier создан")
print(f"✅ Code challenge создан")

# Шаг 3: Создание Authorization URL
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
print("\n1. Сейчас откроется браузер")
print("2. Авторизуйтесь в TikTok")
print("3. Нажмите 'Authorize'")
print("4. Вы увидите JSON от httpbin.org")
print("5. Найдите в JSON строку с 'code'")
print("6. Скопируйте значение code")
print("\n" + "=" * 70)

input("\n🔵 Нажмите Enter чтобы открыть браузер...")

# Открываем браузер
webbrowser.open(auth_url)

print("\n✅ Браузер открыт!")
print("\n📋 После авторизации вы увидите JSON вида:")
print('{')
print('  "args": {')
print('    "code": "ВАШ_КОД_ЗДЕСЬ",')
print('    "scopes": "...",')
print('    "state": "..."')
print('  }')
print('}')
print("\nСкопируйте значение 'code' (без кавычек)")

# Шаг 4: Получение кода
authorization_code = input("\n📋 Вставьте code сюда:\n").strip()

if not authorization_code:
    print("❌ Code не введен!")
    exit(1)

print(f"\n✅ Code получен: {authorization_code[:20]}...")

# Шаг 5: Обмен кода на токен
print("\n🔄 Обмен кода на Access Token...")

token_url = "https://open.tiktokapis.com/v2/oauth/token/"
token_data = {
    'client_key': CLIENT_KEY,
    'client_secret': CLIENT_SECRET,
    'code': authorization_code,
    'grant_type': 'authorization_code',
    'redirect_uri': REDIRECT_URI,
    'code_verifier': code_verifier
}

try:
    response = requests.post(token_url, data=token_data)
    result = response.json()
    
    if response.status_code == 200 and 'access_token' in result:
        print("\n" + "=" * 70)
        print("🎉 УСПЕХ! Токен получен!")
        print("=" * 70)
        
        access_token = result['access_token']
        refresh_token = result.get('refresh_token', '')
        
        print(f"\n✅ Access Token:")
        print(f"   {access_token}")
        
        if refresh_token:
            print(f"\n✅ Refresh Token:")
            print(f"   {refresh_token}")
        
        print("\n" + "=" * 70)
        print("📝 СКОПИРУЙТЕ В .env ФАЙЛ:")
        print("=" * 70)
        print(f"\nTIKTOK_ACCESS_TOKEN={access_token}")
        if refresh_token:
            print(f"TIKTOK_REFRESH_TOKEN={refresh_token}")
        
        # Автосохранение
        auto_save = input("\n💾 Автоматически обновить .env файл? (y/n): ").strip().lower()
        
        if auto_save == 'y':
            try:
                from pathlib import Path
                
                env_path = Path('.env')
                
                if env_path.exists():
                    env_content = env_path.read_text(encoding='utf-8')
                else:
                    env_content = ""
                
                lines = env_content.split('\n')
                updated_access = False
                updated_refresh = False
                
                for i, line in enumerate(lines):
                    if line.startswith('TIKTOK_ACCESS_TOKEN='):
                        lines[i] = f'TIKTOK_ACCESS_TOKEN={access_token}'
                        updated_access = True
                    elif refresh_token and line.startswith('TIKTOK_REFRESH_TOKEN='):
                        lines[i] = f'TIKTOK_REFRESH_TOKEN={refresh_token}'
                        updated_refresh = True
                
                if not updated_access:
                    if env_content and not env_content.endswith('\n'):
                        lines.append('')
                    lines.append(f'TIKTOK_ACCESS_TOKEN={access_token}')
                
                if refresh_token and not updated_refresh:
                    lines.append(f'TIKTOK_REFRESH_TOKEN={refresh_token}')
                
                new_content = '\n'.join(lines)
                env_path.write_text(new_content, encoding='utf-8')
                
                print("✅ Файл .env обновлен!")
                
            except Exception as e:
                print(f"❌ Ошибка сохранения: {e}")
        
        print("\n✅ Готово!")
        
    else:
        print("\n❌ ОШИБКА получения токена:")
        print("=" * 70)
        
        if 'error' in result:
            print(f"Ошибка: {result['error']}")
        if 'error_description' in result:
            print(f"Описание: {result['error_description']}")
        
        import json
        print("\nПолный ответ:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
except Exception as e:
    print(f"\n❌ Ошибка: {e}")

print("\n" + "=" * 70)

