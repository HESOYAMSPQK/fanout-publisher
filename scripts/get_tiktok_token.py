#!/usr/bin/env python3
"""
Скрипт для получения TikTok Access Token через OAuth 2.0

Этот скрипт поможет вам получить access token для TikTok Content Posting API,
который можно использовать для загрузки видео.

Инструкция:
1. Зарегистрируйтесь на https://developers.tiktok.com/
2. Создайте приложение (App)
3. Получите Client Key и Client Secret
4. Запустите этот скрипт и следуйте инструкциям
5. Скопируйте полученный access_token в .env файл
"""

import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import requests
import secrets

# Конфигурация
TIKTOK_CLIENT_KEY = None  # Будет запрошен у пользователя
TIKTOK_CLIENT_SECRET = None  # Будет запрошен у пользователя
TIKTOK_REDIRECT_URI = 'http://localhost:8080/callback'  # Локальный callback

# OAuth endpoints
AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"

# Scopes для Content Posting API
SCOPES = ['user.info.basic', 'video.upload', 'video.publish']

# Переменная для хранения данных
auth_code = None
access_token = None
refresh_token = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Обработчик OAuth callback от TikTok"""
    
    def do_GET(self):
        """Обработка GET запроса с authorization code"""
        global auth_code
        
        # Парсим URL
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Проверяем наличие code
        if 'code' in query_params:
            auth_code = query_params['code'][0]
            
            # Отправляем HTML страницу с успехом
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>TikTok OAuth - Успешно!</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 50px auto;
                        padding: 20px;
                        background: #f5f5f5;
                    }
                    .container {
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    h1 { color: #00f7ef; }
                    .success { color: #28a745; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ Авторизация TikTok успешна!</h1>
                    <p class="success">Authorization code получен!</p>
                    <p>Сейчас получаем access token...</p>
                    <p>Вернитесь в терминал для получения токена.</p>
                    <p class="success">🎉 Можете закрыть это окно.</p>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
            
        elif 'error' in query_params:
            # Ошибка авторизации
            error = query_params.get('error', ['Unknown error'])[0]
            error_desc = query_params.get('error_description', [''])[0]
            
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>TikTok OAuth - Ошибка</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 50px auto;
                        padding: 20px;
                        background: #f5f5f5;
                    }}
                    .container {{
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .error {{ color: #dc3545; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="error">❌ Ошибка авторизации</h1>
                    <p><strong>Ошибка:</strong> {error}</p>
                    <p><strong>Описание:</strong> {error_desc}</p>
                    <p>Пожалуйста, попробуйте снова.</p>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Отключаем логи сервера"""
        pass


def exchange_code_for_token(code: str) -> dict:
    """
    Обменять authorization code на access token
    
    Args:
        code: Authorization code от TikTok
        
    Returns:
        Dict с токенами
    """
    data = {
        'client_key': TIKTOK_CLIENT_KEY,
        'client_secret': TIKTOK_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': TIKTOK_REDIRECT_URI
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    
    try:
        response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if 'error' in result:
            raise Exception(f"TikTok API Error: {result.get('error')} - {result.get('error_description')}")
        
        return result
        
    except requests.RequestException as e:
        raise Exception(f"Token exchange request failed: {str(e)}")


def get_tiktok_access_token():
    """Получить TikTok Access Token через OAuth 2.0"""
    global TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, auth_code, access_token, refresh_token
    
    print("="*60)
    print("🔑 Получение TikTok Access Token")
    print("="*60)
    print()
    
    # Шаг 1: Получить Client Key и Secret
    print("📱 Шаг 1: Создание TikTok приложения")
    print("-" * 60)
    print("1. Откройте: https://developers.tiktok.com/")
    print("2. Войдите в свой TikTok аккаунт")
    print("3. Перейдите в 'Manage apps' → 'Create an app'")
    print("4. Заполните форму:")
    print("   - App name: 'Fanout Publisher' (или любое другое)")
    print("   - App type: 'Web App'")
    print("5. После создания перейдите в настройки приложения")
    print("6. В разделе 'Basic Information' скопируйте:")
    print("   - Client Key")
    print("   - Client Secret")
    print()
    print("ℹ️  ВАЖНО: В настройках приложения добавьте:")
    print(f"   Redirect URI: {TIKTOK_REDIRECT_URI}")
    print("   В разделе 'Login Kit' → 'Redirect URL'")
    print()
    
    TIKTOK_CLIENT_KEY = input("Введите Client Key: ").strip()
    
    if not TIKTOK_CLIENT_KEY:
        print("❌ Ошибка: Client Key не может быть пустым")
        sys.exit(1)
    
    TIKTOK_CLIENT_SECRET = input("Введите Client Secret: ").strip()
    
    if not TIKTOK_CLIENT_SECRET:
        print("❌ Ошибка: Client Secret не может быть пустым")
        sys.exit(1)
    
    print()
    print("📝 Шаг 2: Настройка Redirect URI и Scopes")
    print("-" * 60)
    print("1. В настройках приложения перейдите в 'Add products'")
    print("2. Добавьте 'Login Kit' и 'Content Posting API'")
    print("3. В 'Login Kit' добавьте Redirect URL:")
    print(f"   {TIKTOK_REDIRECT_URI}")
    print("4. В 'Content Posting API' активируйте следующие scopes:")
    print(f"   {', '.join(SCOPES)}")
    print("5. Сохраните настройки")
    print()
    
    input("Нажмите Enter когда закончите настройку... ")
    
    # Шаг 2: Генерируем state для CSRF защиты
    state = secrets.token_urlsafe(32)
    
    # Формируем OAuth URL
    print()
    print("🌐 Шаг 3: Авторизация")
    print("-" * 60)
    
    auth_params = {
        'client_key': TIKTOK_CLIENT_KEY,
        'scope': ','.join(SCOPES),
        'response_type': 'code',
        'redirect_uri': TIKTOK_REDIRECT_URI,
        'state': state
    }
    
    auth_url = f"{AUTHORIZE_URL}?{urllib.parse.urlencode(auth_params)}"
    
    print("Сейчас откроется браузер для авторизации...")
    print(f"Если не открылся, перейдите по ссылке:")
    print(auth_url)
    print()
    
    # Запускаем локальный сервер для получения callback
    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
    
    print("🔄 Локальный сервер запущен на http://localhost:8080")
    print("⏳ Ожидание авторизации...")
    print()
    print("⚠️  ВАЖНО для пользователей из России:")
    print("   TikTok может быть недоступен без VPN!")
    print("   Если авторизация не проходит - включите VPN и попробуйте снова.")
    print()
    
    # Открываем браузер
    webbrowser.open(auth_url)
    
    # Ждем callback
    server.handle_request()
    server.server_close()
    
    if not auth_code:
        print("\n❌ Ошибка: не удалось получить authorization code")
        print("Попробуйте еще раз или проверьте настройки приложения")
        sys.exit(1)
    
    print("\n✅ Authorization code получен!")
    print("🔄 Обмениваем code на access token...")
    print()
    
    # Шаг 3: Обмениваем code на access token
    try:
        token_data = exchange_code_for_token(auth_code)
        
        access_token = token_data.get('data', {}).get('access_token')
        refresh_token = token_data.get('data', {}).get('refresh_token')
        expires_in = token_data.get('data', {}).get('expires_in', 0)
        open_id = token_data.get('data', {}).get('open_id', '')
        
        if not access_token:
            raise Exception("Access token not found in response")
        
        print("="*60)
        print("✅ TikTok Access Token успешно получен!")
        print("="*60)
        print(f"\nOpen ID: {open_id}")
        print(f"Expires in: {expires_in} секунд ({expires_in // 3600} часов)")
        print(f"\nAccess Token:")
        print(access_token)
        if refresh_token:
            print(f"\nRefresh Token:")
            print(refresh_token)
        print("\n" + "="*60)
        print("📋 Скопируйте Access Token и добавьте в .env файл:")
        print(f"TIKTOK_ACCESS_TOKEN={access_token}")
        print(f"TIKTOK_CLIENT_KEY={TIKTOK_CLIENT_KEY}")
        print(f"TIKTOK_CLIENT_SECRET={TIKTOK_CLIENT_SECRET}")
        print("="*60 + "\n")
        
        print("\n💡 Совет:")
        print(f"   - Access Token действителен {expires_in // 3600} часов")
        print("   - Refresh Token можно использовать для обновления токена")
        print("   - Сохраните оба токена в надежном месте!")
        
        return access_token
        
    except Exception as e:
        print(f"\n❌ Ошибка при обмене кода на токен: {e}")
        sys.exit(1)


def main():
    """Главная функция"""
    try:
        get_tiktok_access_token()
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



