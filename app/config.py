"""Конфигурация приложения"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Общие настройки
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Безопасность
    SERVICE_TOKEN: str
    
    # База данных
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # MinIO/S3
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "videos"
    MINIO_SECURE: bool = False
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_BASE_URL: str = "http://api:8000"
    
    # YouTube
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    YOUTUBE_REFRESH_TOKEN: str = ""
    YOUTUBE_DEFAULT_PRIVACY: str = "private"  # public, private, unlisted
    
    # VK (ВКонтакте)
    VK_ACCESS_TOKEN: str = ""
    VK_GROUP_ID: int = 0  # ID группы (опционально, 0 = публикация от имени пользователя)
    VK_DEFAULT_PRIVACY: str = "private"  # private или public
    VK_AS_CLIP: bool = False  # Публиковать как клип (короткое вертикальное видео)
    
    # TikTok
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    TIKTOK_ACCESS_TOKEN: str = ""
    TIKTOK_REFRESH_TOKEN: str = ""  # Для автоматического обновления access token
    TIKTOK_DEFAULT_PRIVACY: str = "SELF_ONLY"  # SELF_ONLY, MUTUAL_FOLLOW_FRIENDS, FOLLOWER_OF_CREATOR, PUBLIC_TO_EVERYONE
    TIKTOK_DISABLE_DUET: bool = False
    TIKTOK_DISABLE_COMMENT: bool = False
    TIKTOK_DISABLE_STITCH: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Разрешить дополнительные поля из .env


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки приложения (с кешированием)"""
    return Settings()

