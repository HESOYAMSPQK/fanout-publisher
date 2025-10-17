#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки настройки локального Telegram Bot API
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv()

def check_env_vars():
    """Проверка необходимых переменных окружения"""
    print("🔍 Проверка переменных окружения...")
    
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'Токен вашего бота',
        'TELEGRAM_API_ID': 'API ID из my.telegram.org',
        'TELEGRAM_API_HASH': 'API Hash из my.telegram.org',
        'TELEGRAM_LOCAL_API_URL': 'URL локального Bot API'
    }
    
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value == '':
            missing.append(f"  ❌ {var} - {description}")
            print(f"  ❌ {var} не установлена")
        else:
            # Скрываем чувствительные данные
            if var in ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_API_HASH']:
                display_value = value[:10] + '...' if len(value) > 10 else '***'
            else:
                display_value = value
            print(f"  ✅ {var} = {display_value}")
    
    if missing:
        print("\n⚠️  Отсутствуют обязательные переменные:")
        for m in missing:
            print(m)
        print("\nДобавьте их в ваш .env файл!")
        return False
    
    print("✅ Все переменные окружения установлены!\n")
    return True


def check_local_api():
    """Проверка доступности локального Bot API"""
    print("🔍 Проверка доступности локального Bot API...")
    
    local_api_url = os.getenv('TELEGRAM_LOCAL_API_URL', '')
    
    if not local_api_url:
        print("  ⚠️  TELEGRAM_LOCAL_API_URL не установлена")
        print("  ℹ️  Бот будет использовать стандартный Telegram API (лимит 50 МБ)")
        return False
    
    # Если запускаем на хосте, заменяем Docker имя на localhost
    if 'telegram-bot-api:' in local_api_url:
        local_api_url = local_api_url.replace('telegram-bot-api:', 'localhost:')
        print(f"  ℹ️  Используем localhost вместо Docker имени")
    
    # Проверяем доступность
    try:
        # Пробуем подключиться к локальному API
        # Telegram Bot API не имеет /healthcheck, просто проверим доступность порта
        test_url = local_api_url.rstrip('/')
        
        print(f"  Попытка подключения к {test_url}...")
        response = requests.get(test_url, timeout=5)
        
        # Telegram Bot API возвращает 404 на корневой путь, но это нормально
        # Главное что сервис отвечает
        if response.status_code in [200, 404]:
            if response.status_code == 404:
                # Проверяем что это действительно ответ от Telegram Bot API
                try:
                    data = response.json()
                    if 'error_code' in data or 'ok' in data:
                        print(f"  ✅ Локальный Bot API доступен!")
                        return True
                except:
                    pass
            else:
                print(f"  ✅ Локальный Bot API доступен!")
                return True
            
            print(f"  ⚠️  Локальный Bot API ответил с кодом {response.status_code}")
            return False
        else:
            print(f"  ⚠️  Локальный Bot API ответил с кодом {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Не удается подключиться к {local_api_url}")
        print(f"  ℹ️  Убедитесь, что контейнер telegram-bot-api запущен:")
        print(f"      docker-compose ps telegram-bot-api")
        return False
    except Exception as e:
        print(f"  ❌ Ошибка: {str(e)}")
        return False


def check_bot_token():
    """Проверка валидности токена бота"""
    print("🔍 Проверка токена бота...")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    local_api_url = os.getenv('TELEGRAM_LOCAL_API_URL', '')
    
    if not bot_token:
        print("  ❌ TELEGRAM_BOT_TOKEN не установлена")
        return False
    
    # Если запускаем на хосте, заменяем Docker имя на localhost
    if local_api_url and 'telegram-bot-api:' in local_api_url:
        local_api_url = local_api_url.replace('telegram-bot-api:', 'localhost:')
    
    try:
        # Используем локальный API если он настроен, иначе стандартный
        if local_api_url:
            base_url = f"{local_api_url.rstrip('/')}/bot{bot_token}"
        else:
            base_url = f"https://api.telegram.org/bot{bot_token}"
        
        response = requests.get(f"{base_url}/getMe", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"  ✅ Бот активен:")
                print(f"     Имя: @{bot_info.get('username')}")
                print(f"     ID: {bot_info.get('id')}")
                return True
            else:
                print(f"  ❌ Ошибка API: {data.get('description')}")
                return False
        else:
            print(f"  ❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Ошибка: {str(e)}")
        return False


def check_docker_compose():
    """Проверка статуса Docker контейнеров"""
    print("🔍 Проверка Docker контейнеров...")
    
    try:
        import subprocess
        
        # Проверяем статус telegram-bot-api
        result = subprocess.run(
            ['docker-compose', 'ps', 'telegram-bot-api'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if 'Up' in result.stdout:
            print("  ✅ Контейнер telegram-bot-api запущен")
            return True
        elif 'Exit' in result.stdout:
            print("  ❌ Контейнер telegram-bot-api остановлен")
            print("  ℹ️  Запустите: docker-compose up -d telegram-bot-api")
            return False
        else:
            print("  ⚠️  Не удалось определить статус контейнера")
            print(f"  Вывод: {result.stdout}")
            return False
            
    except FileNotFoundError:
        print("  ⚠️  docker-compose не найден в PATH")
        print("  ℹ️  Проверьте статус вручную: docker-compose ps")
        return None
    except Exception as e:
        print(f"  ⚠️  Не удалось проверить статус: {str(e)}")
        return None


def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🤖 Проверка настройки локального Telegram Bot API")
    print("="*60 + "\n")
    
    checks = []
    
    # Проверка 1: Переменные окружения
    checks.append(("Переменные окружения", check_env_vars()))
    
    # Проверка 2: Docker контейнер
    docker_status = check_docker_compose()
    if docker_status is not None:
        checks.append(("Docker контейнер", docker_status))
    
    # Проверка 3: Локальный API
    checks.append(("Локальный Bot API", check_local_api()))
    
    # Проверка 4: Токен бота
    checks.append(("Токен бота", check_bot_token()))
    
    # Итоги
    print("\n" + "="*60)
    print("📊 ИТОГИ ПРОВЕРКИ")
    print("="*60)
    
    passed = sum(1 for _, status in checks if status is True)
    total = len(checks)
    
    for name, status in checks:
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("✅ Ваш бот готов принимать файлы до 2 ГБ!")
        print("="*60 + "\n")
        return 0
    else:
        print(f"⚠️  Пройдено {passed}/{total} проверок")
        print("📖 Смотрите ЧЕКЛИСТ_2GB.md для инструкций")
        print("="*60 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

