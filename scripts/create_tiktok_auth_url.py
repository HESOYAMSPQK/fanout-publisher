#!/usr/bin/env python3
"""
Генератор Authorization URL для TikTok с PKCE
"""

import hashlib
import base64
import secrets
from urllib.parse import urlencode

print("=" * 70)
print("🔗 Генератор TikTok Authorization URL с PKCE")
print("=" * 70)

# Ввод данных
CLIENT_KEY = input("\n📝 Введите Client Key: ").strip()

if not CLIENT_KEY:
    print("❌ Client Key обязателен!")
    exit(1)

# Выбор redirect URI
print("\n🔗 Выберите метод получения токена:")
print()
print("1. Автоматический (локальный сервер) - РЕКОМЕНДУЕТСЯ ⭐")
print("   → Запустит python scripts/get_tiktok_token.py")
print("   → Всё сделает автоматически")
print()
print("2. Ручной (localhost callback)")
print("   → Redirect URI: http://localhost:8080/callback")
print("   → Нужно вручную скопировать код из URL")
print()
print("3. Другой redirect URI (свой сервер)")
print("   → Введете свой URL")
print()
print("⚠️  НЕ используйте Justin Stolpe для СВОЕГО приложения!")
print("   Сайт Justin Stolpe работает только со СВОИМ приложением.")

choice = input("\nВыбор (1/2/3): ").strip()

if choice == "1":
    print("\n" + "=" * 70)
    print("✅ Отлично! Запустите:")
    print("=" * 70)
    print("\n   python scripts/get_tiktok_token.py\n")
    print("Этот скрипт сделает всё автоматически!")
    print("=" * 70)
    exit(0)
elif choice == "2":
    REDIRECT_URI = "http://localhost:8080/callback"
    print("\n⚠️  ВАЖНО: Добавьте этот redirect URI в TikTok Developer Portal:")
    print(f"   {REDIRECT_URI}")
elif choice == "3":
    REDIRECT_URI = input("\nВведите Redirect URI: ").strip()
    if not REDIRECT_URI:
        print("❌ Redirect URI не может быть пустым!")
        exit(1)
    print("\n⚠️  ВАЖНО: Добавьте этот redirect URI в TikTok Developer Portal:")
    print(f"   {REDIRECT_URI}")
else:
    print("❌ Неверный выбор!")
    exit(1)

# Генерация PKCE
print("\n🔐 Генерация PKCE параметров...")

code_verifier = secrets.token_urlsafe(64)
code_challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode('utf-8').rstrip('=')

print(f"✅ Code verifier: {code_verifier[:30]}...")
print(f"✅ Code challenge: {code_challenge[:30]}...")

# Важно! Сохраните code_verifier
print("\n" + "=" * 70)
print("⚠️  ВАЖНО! Сохраните Code Verifier:")
print("=" * 70)
print(f"\n{code_verifier}\n")
print("Он понадобится для обмена кода на токен!")
print("=" * 70)

# Создание Authorization URL
STATE = secrets.token_urlsafe(16)

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
print("🌐 ВАШ AUTHORIZATION URL:")
print("=" * 70)
print(f"\n{auth_url}\n")
print("=" * 70)

# Инструкция
print("\n📋 ЧТО ДЕЛАТЬ ДАЛЬШЕ:")
print("=" * 70)
print("""
1. Скопируйте URL выше
2. Откройте в браузере (с VPN если в РФ)
3. Авторизуйтесь в TikTok
4. Разрешите доступ

5. После авторизации:
   - Браузер перенаправит на ваш Redirect URI
   - В адресной строке будет параметр ?code=...
   - Скопируйте значение параметра code
   
6. Обменяйте код на токен:
   python exchange_code.py
   
💡 СОВЕТ: Для автоматизации используйте:
   python scripts/get_tiktok_token.py
   
   Этот скрипт всё сделает сам!
""")

print("=" * 70)

# Сохранение в файл
with open('tiktok_pkce_info.txt', 'w') as f:
    f.write(f"Code Verifier: {code_verifier}\n")
    f.write(f"Code Challenge: {code_challenge}\n")
    f.write(f"State: {STATE}\n")
    f.write(f"Authorization URL: {auth_url}\n")

print("\n✅ Информация сохранена в файл: tiktok_pkce_info.txt")

