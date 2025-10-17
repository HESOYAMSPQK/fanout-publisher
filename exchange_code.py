import requests
import json
import os
from pathlib import Path

print("=" * 70)
print("🔐 Обмен TikTok Authorization Code на Access Token")
print("=" * 70)

# Запрос данных у пользователя
CLIENT_KEY = input("\n📝 Введите ваш TikTok Client Key: ").strip()

if not CLIENT_KEY:
    print("❌ Client Key обязателен!")
    exit(1)

CLIENT_SECRET = input("📝 Введите ваш TikTok Client Secret: ").strip()

if not CLIENT_SECRET:
    print("❌ Client Secret обязателен!")
    exit(1)

# Попытка прочитать код из файла tiktok_pkce_info.txt
authorization_code_default = ""
pkce_file = Path("tiktok_pkce_info.txt")
if pkce_file.exists():
    print("\n📄 Найден файл tiktok_pkce_info.txt")
    content = pkce_file.read_text(encoding='utf-8')
    # Не показываем содержимое, просто информируем

AUTHORIZATION_CODE = input("\n📝 Введите Authorization Code (из браузера): ").strip()

if not AUTHORIZATION_CODE:
    print("❌ Authorization Code обязателен!")
    exit(1)

# Выбор redirect URI (должен совпадать с тем, что использовался при генерации URL)
print("\n🔗 Выберите Redirect URI (тот же, что использовали при авторизации):")
print("1. https://justinstolpe.com/blog_code/tiktokapi/login.php")
print("2. http://localhost:8080/callback")
print("3. Другой (введите вручную)")

choice = input("\nВыбор (1/2/3): ").strip()

if choice == "1":
    REDIRECT_URI = "https://justinstolpe.com/blog_code/tiktokapi/login.php"
elif choice == "2":
    REDIRECT_URI = "http://localhost:8080/callback"
elif choice == "3":
    REDIRECT_URI = input("Введите Redirect URI: ").strip()
else:
    print("❌ Неверный выбор!")
    exit(1)

print("🔄 Обмен кода на Access Token...")

url = "https://open.tiktokapis.com/v2/oauth/token/"
data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "code": AUTHORIZATION_CODE,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI
}

response = requests.post(url, data=data)
result = response.json()

print(f"\n📥 Ответ от TikTok (HTTP {response.status_code}):")

if "access_token" in result:
    print("\n" + "=" * 70)
    print("🎉 УСПЕХ! Токен получен!")
    print("=" * 70)
    
    print(f"\n✅ Access Token:")
    print(result["access_token"])
    
    if "refresh_token" in result:
        print(f"\n✅ Refresh Token:")
        print(result["refresh_token"])
    
    print("\n📝 Скопируйте в .env файл:")
    print("=" * 70)
    print(f"TIKTOK_ACCESS_TOKEN={result['access_token']}")
    
    if "refresh_token" in result:
        print(f"TIKTOK_REFRESH_TOKEN={result['refresh_token']}")
    
    print("\n✅ Готово!")
    
    # Предложение автосохранения
    try:
        auto_save = input("\n💾 Автоматически обновить .env файл? (y/n): ").strip().lower()
        
        if auto_save == 'y':
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
                    lines[i] = f'TIKTOK_ACCESS_TOKEN={result["access_token"]}'
                    updated_access = True
                elif "refresh_token" in result and line.startswith('TIKTOK_REFRESH_TOKEN='):
                    lines[i] = f'TIKTOK_REFRESH_TOKEN={result["refresh_token"]}'
                    updated_refresh = True
            
            if not updated_access:
                if env_content and not env_content.endswith('\n'):
                    lines.append('')
                lines.append(f'TIKTOK_ACCESS_TOKEN={result["access_token"]}')
            
            if "refresh_token" in result and not updated_refresh:
                lines.append(f'TIKTOK_REFRESH_TOKEN={result["refresh_token"]}')
            
            new_content = '\n'.join(lines)
            env_path.write_text(new_content, encoding='utf-8')
            
            print("✅ Файл .env обновлен!")
    except:
        pass
        
else:
    print("\n❌ Ошибка:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if "error" in result:
        error = result["error"]
        if error == "invalid_code":
            print("\n💡 Код истёк (действителен 10 минут) или уже использован.")
            print("   Получите новый код: python scripts/create_tiktok_auth_url.py")
        elif error == "invalid_client":
            print("\n💡 Неверный Client Key или Client Secret.")
            print("   Проверьте значения в TikTok Developer Portal")

