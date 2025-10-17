#!/usr/bin/env python3
"""
Тестовый скрипт для проверки загрузки видео на TikTok

Этот скрипт позволяет протестировать загрузку видео на TikTok
без запуска всего приложения.
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platforms.tiktok import TikTokPublisher


def test_tiktok_upload(
    video_path: str,
    client_key: str,
    client_secret: str,
    access_token: str
):
    """
    Тест загрузки видео на TikTok
    
    Args:
        video_path: Путь к тестовому видео
        client_key: TikTok Client Key
        client_secret: TikTok Client Secret
        access_token: TikTok Access Token
    """
    print("="*60)
    print("🧪 Тест загрузки видео на TikTok")
    print("="*60)
    print()
    
    print("⚠️  ВАЖНО для пользователей из России:")
    print("   Убедитесь что VPN ВКЛЮЧЕН перед тестированием!")
    print()
    
    # Проверка файла
    if not os.path.exists(video_path):
        print(f"❌ Файл не найден: {video_path}")
        sys.exit(1)
    
    file_size = os.path.getsize(video_path)
    print(f"📁 Файл: {video_path}")
    print(f"📊 Размер: {file_size / (1024*1024):.2f} МБ")
    
    # Проверка размера (TikTok максимум 4 ГБ)
    if file_size > 4 * 1024 * 1024 * 1024:
        print("❌ Файл слишком большой! Максимум 4 ГБ для TikTok")
        sys.exit(1)
    
    print()
    
    # Создаем publisher
    print("🔧 Создание TikTok Publisher...")
    publisher = TikTokPublisher(
        client_key=client_key,
        client_secret=client_secret,
        access_token=access_token
    )
    print("✅ Publisher создан")
    print()
    
    # Проверяем информацию о creator
    print("👤 Получение информации о creator...")
    try:
        creator_info = publisher.get_creator_info()
        if 'error' not in creator_info:
            print(f"✅ Creator: {creator_info.get('display_name', 'Unknown')}")
            print(f"   Open ID: {creator_info.get('open_id', 'Unknown')}")
        else:
            print(f"⚠️  Не удалось получить информацию: {creator_info.get('error')}")
    except Exception as e:
        print(f"⚠️  Ошибка при получении информации: {e}")
    print()
    
    # Загружаем видео
    print("📤 Начинаем загрузку видео...")
    print("⚠️  Видео будет загружено в ПРИВАТНОМ режиме (SELF_ONLY)")
    print()
    
    try:
        result = publisher.publish_video(
            video_path=video_path,
            title="[ТЕСТ] Fanout Publisher TikTok Test",
            description="Это тестовое видео, загруженное через Fanout Publisher.\n\n#test #fanoutpublisher",
            privacy_level="SELF_ONLY",  # ПРИВАТНОЕ для теста
            disable_duet=False,
            disable_comment=False,
            disable_stitch=False,
            brand_content=False
        )
        
        print()
        print("="*60)
        print("✅ УСПЕШНО!")
        print("="*60)
        print()
        print(f"🆔 Publish ID: {result['platform_job_id']}")
        print(f"📊 Статус: {result['status']}")
        print()
        print("="*60)
        print("📋 Что дальше:")
        print("1. Откройте TikTok приложение на телефоне")
        print("2. Перейдите в 'Профиль' → 'Черновики'")
        print("3. Видео должно появиться там (может занять 1-5 минут)")
        print("4. Проверьте что видео приватное (видно только вам)")
        print("5. Тестовое видео можно удалить из черновиков")
        print()
        print("⏳ TikTok обрабатывает видео асинхронно...")
        print("   Если видео не появилось сразу - подождите несколько минут")
        print("="*60)
        print()
        
        # Проверяем статус
        print("🔍 Проверка статуса обработки...")
        try:
            import time
            time.sleep(3)  # Подождем 3 секунды
            
            status = publisher.get_video_status(result['platform_job_id'])
            print(f"   Статус: {status.get('status', 'unknown')}")
            
            if status.get('fail_reason'):
                print(f"   ⚠️  Причина ошибки: {status.get('fail_reason')}")
        except Exception as e:
            print(f"   ⚠️  Не удалось получить статус: {e}")
        
        print()
        return result
        
    except Exception as e:
        print()
        print("="*60)
        print("❌ ОШИБКА")
        print("="*60)
        print(f"Тип: {type(e).__name__}")
        print(f"Сообщение: {str(e)}")
        print()
        print("Возможные причины:")
        print("- Неверные credentials (Client Key, Secret, Access Token)")
        print("- Access Token истёк (получите новый)")
        print("- VPN отключен (для пользователей из России)")
        print("- Нет прав на загрузку видео (проверьте scopes)")
        print("- Файл слишком большой или неподдерживаемый формат")
        print("- Проблемы с сетью или TikTok API")
        print()
        print("Рекомендации:")
        print("1. Включите VPN (если в России)")
        print("2. Проверьте credentials в .env файле")
        print("3. Получите новый токен: python scripts/get_tiktok_token.py")
        print("4. Убедитесь что видео MP4, размер < 4 ГБ")
        print("="*60)
        print()
        sys.exit(1)


def main():
    """Главная функция"""
    print()
    
    # Получаем credentials из переменных окружения или запрашиваем
    client_key = os.getenv('TIKTOK_CLIENT_KEY')
    client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
    access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
    
    if not client_key or not client_secret or not access_token:
        print("⚙️  TikTok credentials не найдены в переменных окружения")
        print()
        
        if not client_key:
            client_key = input("Введите TikTok Client Key: ").strip()
            if not client_key:
                print("❌ Client Key не может быть пустым")
                sys.exit(1)
        
        if not client_secret:
            client_secret = input("Введите TikTok Client Secret: ").strip()
            if not client_secret:
                print("❌ Client Secret не может быть пустым")
                sys.exit(1)
        
        if not access_token:
            access_token = input("Введите TikTok Access Token: ").strip()
            if not access_token:
                print("❌ Access Token не может быть пустым")
                sys.exit(1)
    
    print()
    
    # Получаем путь к видео
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        print("📹 Путь к видео не указан")
        print()
        print("💡 Рекомендация: Используйте вертикальное видео (9:16)")
        print("   Разрешение: минимум 720x1280, формат: MP4")
        print()
        video_path = input("Введите путь к тестовому видео: ").strip()
        
        if not video_path:
            print("❌ Путь не может быть пустым")
            sys.exit(1)
    
    print()
    
    # Запускаем тест
    test_tiktok_upload(video_path, client_key, client_secret, access_token)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



