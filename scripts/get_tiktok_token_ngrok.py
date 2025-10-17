#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для получения TikTok Access Token через OAuth 2.0 с ngrok (HTTPS)

TikTok требует HTTPS для redirect URI, поэтому используем ngrok для туннеля.

Требования:
1. Установите ngrok: https://ngrok.com/download
2. (Опционально) Зарегистрируйтесь на ngrok.com для постоянного URL

Использование:
    python scripts/get_tiktok_token_ngrok.py
"""

import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import requests
import secrets
import subprocess
import time
import json
import re
import os

# Настройка кодировки для Windows
if sys.platform == 'win32':
    # Для Python 3.7+
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass
    # Альтернатива для старых версий
    try:
        os.system('chcp 65001 >nul 2>&1')
    except:
        pass

# Конфигурация
TIKTOK_CLIENT_KEY = None
TIKTOK_CLIENT_SECRET = None
LOCAL_PORT = 8080

# OAuth endpoints
AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"

# Scopes для Content Posting API
SCOPES = ['user.info.basic', 'video.upload', 'video.publish']

# Переменная для хранения данных
auth_code = None
ngrok_url = None
ngrok_process = None


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
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 20px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                    }
                    h1 { 
                        color: #00f7ef;
                        font-size: 2.5em;
                        margin-bottom: 20px;
                    }
                    .success { 
                        color: #28a745;
                        font-size: 1.3em;
                        margin: 20px 0;
                    }
                    .icon {
                        font-size: 4em;
                        margin: 20px 0;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">🎉</div>
                    <h1>Авторизация TikTok успешна!</h1>
                    <p class="success">Authorization code получен!</p>
                    <p>Сейчас получаем access token...</p>
                    <p>Вернитесь в терминал для получения токена.</p>
                    <p class="success">Можете закрыть это окно.</p>
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


def check_ngrok_installed():
    """Проверить установлен ли ngrok"""
    try:
        result = subprocess.run(['ngrok', 'version'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_ngrok_auth():
    """Проверить настроен ли auth token для ngrok"""
    try:
        # Пытаемся проверить конфигурацию
        result = subprocess.run(['ngrok', 'config', 'check'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        
        output = result.stdout + result.stderr
        
        # Если в выводе есть ошибки про authtoken - токена нет
        if 'authtoken' in output.lower() or 'authentication' in output.lower():
            return False
        
        # Если команда выполнена успешно - проверяем наличие конфига
        if result.returncode == 0:
            # Пробуем прочитать конфиг напрямую
            config_paths = [
                os.path.expanduser('~/.ngrok2/ngrok.yml'),
                os.path.expanduser('~/Library/Application Support/ngrok/ngrok.yml'),
                os.path.join(os.getenv('LOCALAPPDATA', ''), 'ngrok', 'ngrok.yml')
            ]
            
            for config_path in config_paths:
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            content = f.read()
                            if 'authtoken:' in content or 'authtoken :' in content:
                                return True
                    except:
                        pass
            
            # Если дошли сюда - токена скорее всего нет
            return False
        
        return False
    except:
        return False


def setup_ngrok_auth():
    """Помочь пользователю настроить ngrok auth token"""
    print()
    print("⚠️  ngrok требует настройки auth token!")
    print("=" * 70)
    print()
    print("📋 ИНСТРУКЦИЯ ПО НАСТРОЙКЕ:")
    print("-" * 70)
    print("1. Откройте: https://dashboard.ngrok.com/signup")
    print("2. Зарегистрируйтесь (можно через GitHub)")
    print("3. После входа откройте: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("4. Скопируйте ваш authtoken")
    print()
    print("-" * 70)
    
    auth_token = input("📝 Вставьте authtoken (или 'skip' для продолжения без него): ").strip()
    
    if auth_token.lower() == 'skip':
        print("⚠️  Продолжаем без auth token (могут быть ограничения)...")
        return False
    
    if not auth_token:
        print("❌ Auth token не может быть пустым")
        return False
    
    try:
        # Настраиваем auth token
        result = subprocess.run(
            ['ngrok', 'config', 'add-authtoken', auth_token],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Auth token успешно настроен!")
            return True
        else:
            print(f"❌ Ошибка настройки: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def start_ngrok(port):
    """Запустить ngrok и получить публичный URL"""
    global ngrok_process
    
    print(f"🚀 Запуск ngrok туннеля на порт {port}...")
    
    # Запускаем ngrok с перенаправлением вывода
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    )
    
    # Проверяем что процесс не умер сразу
    time.sleep(0.5)
    if ngrok_process.poll() is not None:
        stdout, stderr = ngrok_process.communicate()
        raise Exception(f"ngrok завершился с ошибкой:\nSTDOUT: {stdout}\nSTDERR: {stderr}")
    
    # Ждем пока ngrok запустится (с повторными попытками)
    print("⏳ Ожидание запуска ngrok API...")
    max_attempts = 20  # Максимум 20 попыток (20 секунд)
    
    for attempt in range(max_attempts):
        time.sleep(1)
        
        # Проверяем что процесс еще жив
        if ngrok_process.poll() is not None:
            stdout, stderr = ngrok_process.communicate()
            raise Exception(f"ngrok неожиданно завершился:\nSTDOUT: {stdout}\nSTDERR: {stderr}")
        
        try:
            response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=2)
            data = response.json()
            
            if 'tunnels' in data and len(data['tunnels']) > 0:
                print("✅ ngrok API ответил!")
                # Ищем HTTPS туннель
                for tunnel in data['tunnels']:
                    if tunnel['proto'] == 'https':
                        return tunnel['public_url']
                
                # Если нет HTTPS, берем первый
                return data['tunnels'][0]['public_url']
        
        except requests.exceptions.ConnectionError:
            # ngrok еще не запустился, ждем еще
            if attempt < max_attempts - 1:
                if attempt % 3 == 0:  # Показываем каждые 3 попытки
                    print(f"   Попытка {attempt + 1}/{max_attempts}...")
                continue
            else:
                # Финальная попытка - показываем вывод ngrok
                raise Exception(
                    "ngrok не запустился за отведенное время.\n"
                    "Возможные причины:\n"
                    "  1. Не настроен authtoken (зарегистрируйтесь на ngrok.com)\n"
                    "  2. Порт 4040 уже занят\n"
                    "  3. Firewall блокирует ngrok\n"
                    "\nПопробуйте запустить ngrok вручную:\n"
                    f"  ngrok http {port}\n"
                )
        
        except requests.exceptions.Timeout:
            if attempt < max_attempts - 1:
                continue
            else:
                raise Exception("Timeout при подключении к ngrok API")
        
        except Exception as e:
            if attempt < max_attempts - 1:
                continue
            else:
                raise Exception(f"Ошибка получения ngrok URL: {e}")
    
    raise Exception("Не удалось получить URL от ngrok")


def stop_ngrok():
    """Остановить ngrok"""
    global ngrok_process
    if ngrok_process:
        print("\n🛑 Остановка ngrok...")
        ngrok_process.terminate()
        try:
            ngrok_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ngrok_process.kill()


def exchange_code_for_token(code: str, redirect_uri: str) -> dict:
    """Обменять authorization code на access token"""
    data = {
        'client_key': TIKTOK_CLIENT_KEY,
        'client_secret': TIKTOK_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    
    try:
        response = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
        result = response.json()
        
        if 'error' in result:
            raise Exception(f"TikTok API Error: {result.get('error')} - {result.get('error_description')}")
        
        return result
        
    except requests.RequestException as e:
        raise Exception(f"Token exchange request failed: {str(e)}")


def get_tiktok_access_token():
    """Получить TikTok Access Token через OAuth 2.0 с ngrok"""
    global TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, auth_code, ngrok_url
    
    print("="*70)
    print("🔑 Получение TikTok Access Token через ngrok (HTTPS)")
    print("="*70)
    print()
    
    # Проверяем ngrok
    if not check_ngrok_installed():
        print("❌ ngrok не установлен!")
        print()
        print("📥 Установите ngrok:")
        print("   1. Откройте: https://ngrok.com/download")
        print("   2. Скачайте для Windows")
        print("   3. Распакуйте в папку (например, C:\\ngrok)")
        print("   4. Добавьте путь в PATH или скопируйте в папку с Python")
        print()
        print("   Или через Chocolatey:")
        print("   choco install ngrok")
        print()
        sys.exit(1)
    
    print("✅ ngrok установлен")
    
    # Проверяем auth token
    if not check_ngrok_auth():
        if not setup_ngrok_auth():
            print()
            print("⚠️  Попытаемся продолжить без auth token...")
            print("   (Если не сработает - зарегистрируйтесь на ngrok.com)")
    
    print()
    
    # Получаем credentials
    print("📱 Введите данные из TikTok Developer Portal:")
    print("-" * 70)
    
    TIKTOK_CLIENT_KEY = input("Client Key: ").strip()
    if not TIKTOK_CLIENT_KEY:
        print("❌ Client Key не может быть пустым")
        sys.exit(1)
    
    TIKTOK_CLIENT_SECRET = input("Client Secret: ").strip()
    if not TIKTOK_CLIENT_SECRET:
        print("❌ Client Secret не может быть пустым")
        sys.exit(1)
    
    print()
    
    try:
        # Запускаем ngrok
        ngrok_url = start_ngrok(LOCAL_PORT)
        
        print(f"✅ ngrok туннель создан!")
        print(f"🌐 Публичный URL: {ngrok_url}")
        print()
        
        # Формируем redirect URI
        redirect_uri = f"{ngrok_url}/callback"
        
        print("⚠️  ВАЖНО! Добавьте этот Redirect URI в TikTok Developer Portal:")
        print("=" * 70)
        print(f"   {redirect_uri}")
        print("=" * 70)
        print()
        print("1. Откройте: https://developers.tiktok.com/")
        print("2. Ваше приложение → Login Kit → Redirect URLs")
        print("3. Нажмите 'Add redirect URL'")
        print(f"4. Вставьте: {redirect_uri}")
        print("5. Сохраните")
        print()
        
        input("⏸️  Нажмите Enter когда добавите redirect URI... ")
        
        print()
        print("🌐 Генерация Authorization URL...")
        
        # Генерируем state
        state = secrets.token_urlsafe(32)
        
        # Формируем OAuth URL
        auth_params = {
            'client_key': TIKTOK_CLIENT_KEY,
            'scope': ','.join(SCOPES),
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'state': state
        }
        
        auth_url = f"{AUTHORIZE_URL}?{urllib.parse.urlencode(auth_params)}"
        
        print("✅ Authorization URL создан")
        print()
        print("🌐 Открываем браузер для авторизации...")
        print()
        print("⚠️  ВАЖНО для пользователей из России:")
        print("   TikTok может быть недоступен без VPN!")
        print("   Если авторизация не проходит - включите VPN.")
        print()
        
        # Запускаем локальный сервер
        server = HTTPServer(('localhost', LOCAL_PORT), OAuthCallbackHandler)
        
        print(f"✅ Локальный сервер запущен на localhost:{LOCAL_PORT}")
        print(f"✅ Публичный URL: {ngrok_url}")
        print("⏳ Ожидание авторизации...")
        print()
        
        # Открываем браузер
        webbrowser.open(auth_url)
        
        # Ждем callback (с таймаутом)
        server.timeout = 120  # 2 минуты на авторизацию
        server.handle_request()
        server.server_close()
        
        if not auth_code:
            print("\n⚠️  Authorization code не был получен автоматически")
            print("   (Возможно, ngrok показал страницу предупреждения)")
            print()
            print("📋 Вставьте callback URL из браузера вручную:")
            print("   (Полный URL с параметрами, начинающийся с https://...)")
            print()
            
            callback_url = input("Callback URL: ").strip()
            
            if callback_url:
                try:
                    parsed = urllib.parse.urlparse(callback_url)
                    params = urllib.parse.parse_qs(parsed.query)
                    
                    if 'code' in params:
                        auth_code = params['code'][0]
                        auth_code = urllib.parse.unquote(auth_code)
                        print(f"\n✅ Код извлечен из URL!")
                    else:
                        print("\n❌ Параметр 'code' не найден в URL")
                        sys.exit(1)
                
                except Exception as e:
                    print(f"\n❌ Ошибка парсинга URL: {e}")
                    sys.exit(1)
            else:
                print("\n❌ URL не может быть пустым")
                sys.exit(1)
        
        print("\n✅ Authorization code получен!")
        print("🔄 Обмениваем code на access token...")
        print()
        
        # Обмениваем code на access token
        token_data = exchange_code_for_token(auth_code, redirect_uri)
        
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
            raise Exception("Access token not found in response")
        
        print("="*70)
        print("✅ TikTok Access Token успешно получен!")
        print("="*70)
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
        print("="*70)
        print("📋 Скопируйте в .env:")
        print("="*70)
        print(f"TIKTOK_CLIENT_KEY={TIKTOK_CLIENT_KEY}")
        print(f"TIKTOK_CLIENT_SECRET={TIKTOK_CLIENT_SECRET}")
        print(f"TIKTOK_ACCESS_TOKEN={access_token}")
        
        if refresh_token:
            print(f"TIKTOK_REFRESH_TOKEN={refresh_token}")
        
        print("="*70)
        
        # Автосохранение в .env
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
                        lines[i] = f'TIKTOK_CLIENT_KEY={TIKTOK_CLIENT_KEY}'
                        updated['client_key'] = True
                    elif line.startswith('TIKTOK_CLIENT_SECRET='):
                        lines[i] = f'TIKTOK_CLIENT_SECRET={TIKTOK_CLIENT_SECRET}'
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
                    lines.append(f'TIKTOK_CLIENT_KEY={TIKTOK_CLIENT_KEY}')
                if not updated['client_secret']:
                    lines.append(f'TIKTOK_CLIENT_SECRET={TIKTOK_CLIENT_SECRET}')
                if not updated['access_token']:
                    lines.append(f'TIKTOK_ACCESS_TOKEN={access_token}')
                if refresh_token and not updated['refresh_token']:
                    lines.append(f'TIKTOK_REFRESH_TOKEN={refresh_token}')
                
                new_content = '\n'.join(lines)
                env_path.write_text(new_content, encoding='utf-8')
                
                print("✅ Файл .env обновлен!")
        
        except Exception as e:
            print(f"⚠️  Ошибка сохранения: {e}")
        
        return access_token
        
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        stop_ngrok()


def main():
    """Главная функция"""
    try:
        get_tiktok_access_token()
        print("\n🎉 Готово!")
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        stop_ngrok()


if __name__ == "__main__":
    main()

