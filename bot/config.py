"""Конфигурация бота"""
import os
from dotenv import load_dotenv

load_dotenv()


class BotConfig:
    """Конфигурация Telegram бота"""
    
    # Telegram
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    LOCAL_API_URL = os.getenv("TELEGRAM_LOCAL_API_URL", "")  # Пусто = использовать стандартный API
    ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))
    
    # API
    API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
    SERVICE_TOKEN = os.getenv("SERVICE_TOKEN")
    
    # MinIO
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET", "videos")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
    
    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


config = BotConfig()


