#!/usr/bin/env python3
"""
Скрипт для получения YouTube OAuth2 refresh token

Использование:
1. Получи Client ID и Client Secret на https://console.cloud.google.com/apis/credentials
2. Запусти этот скрипт: python scripts/get_youtube_token.py
3. Открой предложенную ссылку в браузере
4. Разреши доступ
5. Скопируй код авторизации
6. Вставь код в консоль
7. Скопируй refresh_token в .env
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()

# Scopes для YouTube API
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_refresh_token():
    """Получить refresh token через OAuth2 flow"""
    
    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Error: YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET must be set in .env")
        print("\n📝 Get them from: https://console.cloud.google.com/apis/credentials")
        print("   1. Create OAuth 2.0 Client ID")
        print("   2. Application type: Desktop app or Web application")
        print("   3. Add authorized redirect URIs: http://localhost:8080/")
        return
    
    # Создаем client config
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/", "urn:ietf:wg:oauth:2.0:oob"]
        }
    }
    
    try:
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=SCOPES
        )
        
        print("\n🔐 Starting OAuth2 flow...")
        print("\n⚠️  If browser doesn't open automatically, copy the URL and open it manually.")
        
        # Запускаем локальный сервер для получения кода
        creds = flow.run_local_server(
            port=8080,
            authorization_prompt_message='Opening browser for authorization...',
            success_message='Authorization successful! You can close this window.',
            open_browser=True
        )
        
        print("\n✅ Authorization successful!")
        print(f"\n📋 Your refresh token:\n")
        print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")
        print(f"\n💾 Add this line to your .env file")
        
        # Также выводим access token для информации
        print(f"\n🔑 Access token (expires in {creds.expiry}):")
        print(f"{creds.token[:50]}...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 If you see 'redirect_uri_mismatch' error:")
        print("   1. Go to Google Cloud Console")
        print("   2. Add http://localhost:8080/ to authorized redirect URIs")


if __name__ == "__main__":
    print("=" * 70)
    print("YouTube OAuth2 Refresh Token Generator")
    print("=" * 70)
    get_refresh_token()


