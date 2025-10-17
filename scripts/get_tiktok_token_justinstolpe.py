#!/usr/bin/env python3
"""
Скрипт для получения TikTok токена через сайт Justin Stolpe
Использует его тестовое приложение для демонстрации
"""

import requests
import json
from pathlib import Path

print("=" * 70)
print("🔐 Получение TikTok Token через Justin Stolpe")
print("=" * 70)
print("\n⚠️  ВНИМАНИЕ: Этот скрипт использует тестовое приложение Justin Stolpe!")
print("   НЕ используйте полученный токен в production!")
print("   Для production создайте свое приложение и используйте get_tiktok_token.py")
print("=" * 70)

# Credentials от Justin Stolpe (публичные, только для тестирования)
CLIENT_KEY = "sbaw4p2aqcik26biuo"
CLIENT_SECRET = "h70qAC0IZJ4RBfIIqQxDu0M3ybTUmFyu"
REDIRECT_URI = "https://justinstolpe.com/blog_code/tiktokapi/login.php"

print("\n📋 ИНСТРУКЦИЯ:")
print("=" * 70)
print("1. Откройте в браузере (с VPN):")
print("   https://justinstolpe.com/blog_code/tiktokapi/login.php")
print()
print("2. Нажмите кнопку 'Click here to log in with TikTok'")
print()
print("3. Авторизуйтесь в TikTok и разрешите доступ")
print()
print("4. На странице результата найдите 'Code From TikTok'")
print("   (Это длинная строка с символами)")
print()
print("5. Скопируйте ТОЛЬКО КОД (без звездочки * в конце)")
print("=" * 70)

AUTHORIZATION_CODE = input("\n📝 Вставьте Authorization Code: ").strip()

if not AUTHORIZATION_CODE:
    print("❌ Код не может быть пустым!")
    exit(1)

# Удаляем возможные артефакты
AUTHORIZATION_CODE = AUTHORIZATION_CODE.replace('*0!', '*0!')  # Исправляем возможные опечатки

print("\n🔄 Обмен кода на Access Token...")

url = "https://open.tiktokapis.com/v2/oauth/token/"
data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "code": AUTHORIZATION_CODE,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI
}

try:
    response = requests.post(url, data=data, timeout=30)
    result = response.json()
    
    print(f"\n📥 Ответ от TikTok (HTTP {response.status_code}):")
    
    # TikTok API v2 возвращает токен в поле data
    if "data" in result and "access_token" in result["data"]:
        token_data = result["data"]
        
        print("\n" + "=" * 70)
        print("🎉 УСПЕХ! Токен получен!")
        print("=" * 70)
        
        print(f"\n✅ Access Token:")
        print(token_data["access_token"])
        
        if "refresh_token" in token_data:
            print(f"\n✅ Refresh Token:")
            print(token_data["refresh_token"])
        
        if "expires_in" in token_data:
            expires_hours = token_data["expires_in"] // 3600
            print(f"\n⏰ Срок действия: {expires_hours} часов")
        
        if "open_id" in token_data:
            print(f"\n🆔 Open ID: {token_data['open_id']}")
        
        print("\n" + "=" * 70)
        print("📝 ДЛЯ ТЕСТИРОВАНИЯ скопируйте в .env:")
        print("=" * 70)
        print(f"TIKTOK_CLIENT_KEY={CLIENT_KEY}")
        print(f"TIKTOK_CLIENT_SECRET={CLIENT_SECRET}")
        print(f"TIKTOK_ACCESS_TOKEN={token_data['access_token']}")
        
        if "refresh_token" in token_data:
            print(f"TIKTOK_REFRESH_TOKEN={token_data['refresh_token']}")
        
        print("\n" + "=" * 70)
        print("⚠️  ВАЖНО!")
        print("=" * 70)
        print("❌ Это токен тестового приложения Justin Stolpe")
        print("❌ НЕ используйте его для публикации реальных видео")
        print("✅ Для production создайте СВОЕ приложение:")
        print("   1. https://developers.tiktok.com/")
        print("   2. Создайте приложение")
        print("   3. Запустите: python scripts/get_tiktok_token.py")
        print("=" * 70)
        
        # Автосохранение
        try:
            auto_save = input("\n💾 Сохранить в .env для тестирования? (y/n): ").strip().lower()
            
            if auto_save == 'y':
                env_path = Path('.env')
                
                if env_path.exists():
                    env_content = env_path.read_text(encoding='utf-8')
                else:
                    env_content = ""
                
                lines = env_content.split('\n')
                updated = {
                    'client_key': False,
                    'client_secret': False,
                    'access_token': False,
                    'refresh_token': False
                }
                
                for i, line in enumerate(lines):
                    if line.startswith('TIKTOK_CLIENT_KEY='):
                        lines[i] = f'TIKTOK_CLIENT_KEY={CLIENT_KEY}'
                        updated['client_key'] = True
                    elif line.startswith('TIKTOK_CLIENT_SECRET='):
                        lines[i] = f'TIKTOK_CLIENT_SECRET={CLIENT_SECRET}'
                        updated['client_secret'] = True
                    elif line.startswith('TIKTOK_ACCESS_TOKEN='):
                        lines[i] = f'TIKTOK_ACCESS_TOKEN={token_data["access_token"]}'
                        updated['access_token'] = True
                    elif "refresh_token" in token_data and line.startswith('TIKTOK_REFRESH_TOKEN='):
                        lines[i] = f'TIKTOK_REFRESH_TOKEN={token_data["refresh_token"]}'
                        updated['refresh_token'] = True
                
                # Добавляем недостающие поля
                if not updated['client_key']:
                    lines.append(f'TIKTOK_CLIENT_KEY={CLIENT_KEY}')
                if not updated['client_secret']:
                    lines.append(f'TIKTOK_CLIENT_SECRET={CLIENT_SECRET}')
                if not updated['access_token']:
                    lines.append(f'TIKTOK_ACCESS_TOKEN={token_data["access_token"]}')
                if "refresh_token" in token_data and not updated['refresh_token']:
                    lines.append(f'TIKTOK_REFRESH_TOKEN={token_data["refresh_token"]}')
                
                new_content = '\n'.join(lines)
                env_path.write_text(new_content, encoding='utf-8')
                
                print("✅ Файл .env обновлен!")
        except Exception as e:
            print(f"⚠️  Не удалось сохранить в .env: {e}")
    
    # Старый формат ответа (если вдруг)
    elif "access_token" in result:
        print("\n" + "=" * 70)
        print("🎉 Токен получен!")
        print("=" * 70)
        print(f"\nAccess Token: {result['access_token']}")
    
    else:
        print("\n❌ Ошибка:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "error" in result:
            error = result["error"]
            error_desc = result.get("error_description", "")
            
            print(f"\n💡 Причина: {error} - {error_desc}")
            
            if error == "invalid_grant":
                print("\n🔴 Код истёк или уже использован!")
                print("   Authorization code действует только 10 минут")
                print("   Получите новый код на сайте:")
                print("   https://justinstolpe.com/blog_code/tiktokapi/login.php")
            elif error == "invalid_client":
                print("\n🔴 Неверные credentials!")
                print("   (Это не должно происходить с публичным приложением)")
            
            print("\n📋 Советы:")
            print("   - Код можно использовать только один раз")
            print("   - Код действует 10 минут")
            print("   - Копируйте код БЕЗ пробелов и лишних символов")
            print("   - Используйте VPN если находитесь в РФ")

except requests.RequestException as e:
    print(f"\n❌ Ошибка сети: {e}")
    print("\n💡 Проверьте:")
    print("   - Интернет соединение")
    print("   - VPN (если в РФ)")
    print("   - Firewall не блокирует запросы")

except Exception as e:
    print(f"\n❌ Неожиданная ошибка: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ Завершено!")
print("=" * 70)
