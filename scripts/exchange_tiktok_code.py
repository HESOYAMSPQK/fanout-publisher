#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обмена TikTok authorization code на access token

Используйте этот скрипт, если получили authorization code вручную
через callback URL из браузера.

Использование:
    python scripts/exchange_tiktok_code.py
"""

import sys
import os
import requests
import urllib.parse

# Настройка кодировки для Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass
    try:
        os.system('chcp 65001 >nul 2>&1')
    except:
        pass


TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"


def extract_code_from_url(url: str) -> str:
    """Извлечь authorization code из callback URL"""
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        if 'code' in params:
            code = params['code'][0]
            # URL decode на всякий случай
            code = urllib.parse.unquote(code)
            return code
        else:
            raise ValueError("Параметр 'code' не найден в URL")
    
    except Exception as e:
        raise ValueError(f"Не удалось распарсить URL: {e}")


def exchange_code_for_token(
    client_key: str,
    client_secret: str,
    code: str,
    redirect_uri: str
) -> dict:
    """Обменять authorization code на access token"""
    
    data = {
        'client_key': client_key,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    
    print("\n🔄 Обмен authorization code на access token...")
    print(f"📡 Запрос к: {TOKEN_URL}")
    print()
    
    try:
        response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
        
        print(f"📥 Статус ответа: {response.status_code}")
        
        result = response.json()
        
        # Показываем сырой ответ для отладки
        if response.status_code != 200:
            print("\n⚠️  Ответ от API:")
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if 'error' in result:
            error_msg = result.get('error', 'Unknown error')
            error_desc = result.get('error_description', 'No description')
            raise Exception(f"TikTok API Error: {error_msg} - {error_desc}")
        
        return result
        
    except requests.RequestException as e:
        raise Exception(f"Ошибка HTTP запроса: {str(e)}")


def main():
    """Главная функция"""
    
    print("=" * 70)
    print("🔄 Обмен TikTok Authorization Code на Access Token")
    print("=" * 70)
    print()
    
    # Получаем Client Key и Secret
    print("📱 Введите данные из TikTok Developer Portal:")
    print("-" * 70)
    
    client_key = input("Client Key: ").strip()
    if not client_key:
        print("❌ Client Key не может быть пустым")
        sys.exit(1)
    
    client_secret = input("Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret не может быть пустым")
        sys.exit(1)
    
    print()
    print("-" * 70)
    print("📋 Теперь вставьте callback URL из браузера")
    print("   (Полный URL с параметрами, например:")
    print("   https://xxx.ngrok-free.dev/callback?code=...&scopes=...)")
    print("-" * 70)
    print()
    
    callback_url = input("Callback URL: ").strip()
    if not callback_url:
        print("❌ URL не может быть пустым")
        sys.exit(1)
    
    try:
        # Извлекаем код из URL
        auth_code = extract_code_from_url(callback_url)
        
        print()
        print("✅ Authorization code извлечен из URL:")
        print(f"   {auth_code[:50]}..." if len(auth_code) > 50 else f"   {auth_code}")
        print()
        
        # Извлекаем redirect_uri (базовая часть URL)
        parsed = urllib.parse.urlparse(callback_url)
        redirect_uri = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        print(f"✅ Redirect URI:")
        print(f"   {redirect_uri}")
        print()
        
        # Обмениваем код на токен
        token_data = exchange_code_for_token(
            client_key,
            client_secret,
            auth_code,
            redirect_uri
        )
        
        # Проверяем формат ответа (TikTok API v2)
        if 'data' in token_data:
            token_info = token_data['data']
        else:
            token_info = token_data
        
        access_token = token_info.get('access_token')
        refresh_token = token_info.get('refresh_token')
        expires_in = token_info.get('expires_in', 0)
        open_id = token_info.get('open_id', '')
        
        if not access_token:
            raise Exception("Access token не найден в ответе API")
        
        # Показываем результат
        print()
        print("=" * 70)
        print("✅ TikTok Access Token успешно получен!")
        print("=" * 70)
        print()
        print(f"🆔 Open ID: {open_id}")
        print(f"⏰ Срок действия: {expires_in} сек ({expires_in // 3600} часов)")
        print()
        print(f"✅ Access Token:")
        print(access_token)
        
        if refresh_token:
            print()
            print(f"✅ Refresh Token:")
            print(refresh_token)
        
        print()
        print("=" * 70)
        print("📋 Скопируйте эти строки в .env файл:")
        print("=" * 70)
        print(f"TIKTOK_CLIENT_KEY={client_key}")
        print(f"TIKTOK_CLIENT_SECRET={client_secret}")
        print(f"TIKTOK_ACCESS_TOKEN={access_token}")
        
        if refresh_token:
            print(f"TIKTOK_REFRESH_TOKEN={refresh_token}")
        
        print("=" * 70)
        
        # Предложение автосохранения
        try:
            save = input("\n💾 Сохранить в .env файл? (y/n): ").strip().lower()
            
            if save == 'y':
                from pathlib import Path
                
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
                        lines[i] = f'TIKTOK_CLIENT_KEY={client_key}'
                        updated['client_key'] = True
                    elif line.startswith('TIKTOK_CLIENT_SECRET='):
                        lines[i] = f'TIKTOK_CLIENT_SECRET={client_secret}'
                        updated['client_secret'] = True
                    elif line.startswith('TIKTOK_ACCESS_TOKEN='):
                        lines[i] = f'TIKTOK_ACCESS_TOKEN={access_token}'
                        updated['access_token'] = True
                    elif line.startswith('TIKTOK_REFRESH_TOKEN='):
                        if refresh_token:
                            lines[i] = f'TIKTOK_REFRESH_TOKEN={refresh_token}'
                            updated['refresh_token'] = True
                
                # Добавляем недостающие
                if not updated['client_key']:
                    lines.append(f'TIKTOK_CLIENT_KEY={client_key}')
                if not updated['client_secret']:
                    lines.append(f'TIKTOK_CLIENT_SECRET={client_secret}')
                if not updated['access_token']:
                    lines.append(f'TIKTOK_ACCESS_TOKEN={access_token}')
                if refresh_token and not updated['refresh_token']:
                    lines.append(f'TIKTOK_REFRESH_TOKEN={refresh_token}')
                
                new_content = '\n'.join(lines)
                env_path.write_text(new_content, encoding='utf-8')
                
                print("✅ Файл .env обновлен!")
                print()
                print("🎉 Готово! Теперь можете использовать TikTok API")
        
        except Exception as e:
            print(f"⚠️  Ошибка сохранения: {e}")
    
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


