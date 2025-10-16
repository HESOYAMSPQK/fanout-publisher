"""Pydantic схемы для API"""
from pydantic import BaseModel, Field
from typing import Optional, List


class IngestRequest(BaseModel):
    """Запрос на публикацию видео"""
    video_hash: str = Field(..., description="SHA256 хеш видеофайла")
    s3_key: str = Field(..., description="Ключ файла в MinIO/S3")
    file_size: int = Field(..., description="Размер файла в байтах")
    duration: Optional[int] = Field(None, description="Длительность видео в секундах")
    
    platform: str = Field(..., description="Целевая платформа (youtube, instagram, etc.)")
    title: str = Field(..., description="Заголовок видео")
    description: Optional[str] = Field(None, description="Описание видео")
    tags: Optional[List[str]] = Field(None, description="Теги видео")
    
    telegram_user_id: Optional[str] = Field(None, description="Telegram User ID")
    telegram_message_id: Optional[str] = Field(None, description="Telegram Message ID")


class IngestResponse(BaseModel):
    """Ответ на запрос публикации"""
    submission_id: str = Field(..., description="Уникальный ID заявки")
    status: str = Field(..., description="Статус заявки (QUEUED)")


class StatusResponse(BaseModel):
    """Ответ со статусом публикации"""
    submission_id: str
    status: str
    platform: str
    platform_job_id: Optional[str] = None
    public_url: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: str
    updated_at: str
    published_at: Optional[str] = None


class HealthResponse(BaseModel):
    """Ответ health check"""
    status: str
    timestamp: str
    service: str


