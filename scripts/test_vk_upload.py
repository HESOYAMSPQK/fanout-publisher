#!/usr/bin/env python3
"""
Тестовый скрипт для проверки загрузки видео на VK

Этот скрипт позволяет протестировать загрузку видео на VK
без запуска всего приложения.
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platforms.vk import VKPublisher


def test_vk_upload(video_path: str, access_token: str):
    """
    Тест загрузки видео на VK
    
    Args:
        video_path: Путь к тестовому видео
        access_token: VK Access Token
    """
    print("="*60)
    print("🧪 Тест загрузки видео на VK")
    print("="*60)
    print()
    
    # Проверка файла
    if not os.path.exists(video_path):
        print(f"❌ Файл не найден: {video_path}")
        sys.exit(1)
    
    file_size = os.path.getsize(video_path)
    print(f"📁 Файл: {video_path}")
    print(f"📊 Размер: {file_size / (1024*1024):.2f} МБ")
    print()
    
    # Создаем publisher
    print("🔧 Создание VK Publisher...")
    publisher = VKPublisher(
        access_token=access_token,
        group_id=None  # Публикуем от имени пользователя
    )
    print("✅ Publisher создан")
    print()
    
    # Загружаем видео
    print("📤 Начинаем загрузку видео...")
    print("⚠️  Видео будет загружено в ПРИВАТНОМ режиме")
    print()
    
    try:
        result = publisher.publish_video(
            video_path=video_path,
            title="[ТЕСТ] Fanout Publisher VK Test",
            description="Это тестовое видео, загруженное через Fanout Publisher.\nМожно удалить.",
            is_private=True,  # ПРИВАТНОЕ для теста
            is_clip=False,  # Обычное видео, не клип
            wallpost=False  # Не публикуем на стене
        )
        
        print()
        print("="*60)
        print("✅ УСПЕШНО!")
        print("="*60)
        print()
        print(f"🆔 Video ID: {result['platform_job_id']}")
        print(f"🔗 URL: {result['public_url']}")
        print(f"📊 Статус: {result['status']}")
        print()
        print("="*60)
        print("📋 Что дальше:")
        print("1. Проверьте видео по ссылке выше")
        print("2. Убедитесь, что оно приватное")
        print("3. Если всё ок - можете использовать VK в приложении!")
        print("4. Тестовое видео можно удалить на странице видео")
        print("="*60)
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
        print("- Неверный Access Token")
        print("- Токен не имеет прав на загрузку видео (scope: video)")
        print("- Файл слишком большой")
        print("- Проблемы с сетью")
        print("="*60)
        print()
        sys.exit(1)


def main():
    """Главная функция"""
    print()
    
    # Получаем Access Token из переменной окружения или запрашиваем
    access_token = os.getenv('VK_ACCESS_TOKEN')
    
    if not access_token:
        print("⚙️  VK_ACCESS_TOKEN не найден в переменных окружения")
        print()
        access_token = input("Введите VK Access Token: ").strip()
        
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
        video_path = input("Введите путь к тестовому видео: ").strip()
        
        if not video_path:
            print("❌ Путь не может быть пустым")
            sys.exit(1)
    
    print()
    
    # Запускаем тест
    test_vk_upload(video_path, access_token)


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



