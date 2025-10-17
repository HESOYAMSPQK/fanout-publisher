"""Celery задачи для публикации видео"""
import os
import tempfile
import structlog
from datetime import datetime
from celery import Task
from minio import Minio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from workers.celery_app import celery_app
from app.database import PublishJob
from platforms.youtube import YouTubePublisher
from platforms.vk import VKPublisher
from platforms.tiktok import TikTokPublisher

# Настройка логирования
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Настройка БД
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Настройка MinIO
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'videos')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'false').lower() == 'true'

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

# YouTube credentials
YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID', '')
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET', '')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN', '')
YOUTUBE_DEFAULT_PRIVACY = os.getenv('YOUTUBE_DEFAULT_PRIVACY', 'private')

# VK credentials
VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN', '')
VK_GROUP_ID = int(os.getenv('VK_GROUP_ID', '0'))
VK_DEFAULT_PRIVACY = os.getenv('VK_DEFAULT_PRIVACY', 'private')
VK_AS_CLIP = os.getenv('VK_AS_CLIP', 'false').lower() == 'true'

# TikTok credentials
TIKTOK_CLIENT_KEY = os.getenv('TIKTOK_CLIENT_KEY', '')
TIKTOK_CLIENT_SECRET = os.getenv('TIKTOK_CLIENT_SECRET', '')
TIKTOK_ACCESS_TOKEN = os.getenv('TIKTOK_ACCESS_TOKEN', '')
TIKTOK_REFRESH_TOKEN = os.getenv('TIKTOK_REFRESH_TOKEN', '')
TIKTOK_DEFAULT_PRIVACY = os.getenv('TIKTOK_DEFAULT_PRIVACY', 'SELF_ONLY')
TIKTOK_DISABLE_DUET = os.getenv('TIKTOK_DISABLE_DUET', 'false').lower() == 'true'
TIKTOK_DISABLE_COMMENT = os.getenv('TIKTOK_DISABLE_COMMENT', 'false').lower() == 'true'
TIKTOK_DISABLE_STITCH = os.getenv('TIKTOK_DISABLE_STITCH', 'false').lower() == 'true'


def save_tiktok_tokens(access_token: str, refresh_token: str):
    """
    Сохранить обновленные TikTok токены в .env файл
    
    Args:
        access_token: Новый access token
        refresh_token: Новый refresh token
    """
    try:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        if not os.path.exists(env_path):
            logger.warning(".env file not found", path=env_path)
            return
        
        # Читаем текущий .env
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Обновляем токены
        updated = False
        refresh_updated = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('TIKTOK_ACCESS_TOKEN='):
                lines[i] = f'TIKTOK_ACCESS_TOKEN={access_token}\n'
                updated = True
            elif line.strip().startswith('TIKTOK_REFRESH_TOKEN='):
                lines[i] = f'TIKTOK_REFRESH_TOKEN={refresh_token}\n'
                refresh_updated = True
        
        # Если не нашли - добавляем
        if not updated:
            lines.append(f'TIKTOK_ACCESS_TOKEN={access_token}\n')
        if not refresh_updated:
            lines.append(f'TIKTOK_REFRESH_TOKEN={refresh_token}\n')
        
        # Записываем обратно
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        logger.info(
            "✅ TikTok токены сохранены в .env",
            access_token_preview=access_token[:20] + "...",
            refresh_token_preview=refresh_token[:20] + "..."
        )
        
        # Обновляем глобальные переменные для текущего процесса
        global TIKTOK_ACCESS_TOKEN, TIKTOK_REFRESH_TOKEN
        TIKTOK_ACCESS_TOKEN = access_token
        TIKTOK_REFRESH_TOKEN = refresh_token
        
    except Exception as e:
        logger.error(
            "Failed to save TikTok tokens to .env",
            error=str(e),
            error_type=type(e).__name__
        )


class PublishTask(Task):
    """Базовый класс для задач публикации"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Обработка ошибки задачи"""
        logger.error(
            "Task failed",
            task_id=task_id,
            args=args,
            kwargs=kwargs,
            error=str(exc),
            traceback=str(einfo)
        )


@celery_app.task(base=PublishTask, bind=True, max_retries=3)
def publish_submission(self, submission_id: str):
    """
    Публикация видео на платформу
    
    Args:
        submission_id: ID заявки на публикацию
    """
    db = SessionLocal()
    temp_file_path = None
    
    try:
        logger.info("Starting publish task", submission_id=submission_id)
        
        # Получаем задачу из БД
        job = db.query(PublishJob).filter_by(submission_id=submission_id).first()
        
        if not job:
            logger.error("Job not found", submission_id=submission_id)
            raise Exception(f"Job not found: {submission_id}")
        
        # Обновляем статус
        job.status = "PROCESSING"
        db.commit()
        
        logger.info(
            "Processing job",
            submission_id=submission_id,
            platform=job.platform,
            s3_key=job.s3_key
        )
        
        # Скачиваем видео из MinIO во временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file_path = temp_file.name
            
            logger.info(
                "Downloading video from MinIO",
                s3_key=job.s3_key,
                temp_path=temp_file_path
            )
            
            minio_client.fget_object(
                MINIO_BUCKET,
                job.s3_key,
                temp_file_path
            )
            
            logger.info(
                "Video downloaded",
                size=os.path.getsize(temp_file_path)
            )
        
        # Публикуем на платформу
        if job.platform == "youtube":
            result = publish_to_youtube(
                video_path=temp_file_path,
                title=job.title,
                description=job.description or "",
                tags=job.tags or []
            )
        elif job.platform == "vk":
            result = publish_to_vk(
                video_path=temp_file_path,
                title=job.title,
                description=job.description or "",
                privacy_status=None  # Используем дефолтный из настроек
            )
        elif job.platform == "tiktok":
            result = publish_to_tiktok(
                video_path=temp_file_path,
                title=job.title,
                description=job.description or "",
                privacy_level=None  # Используем дефолтный из настроек
            )
        else:
            raise Exception(f"Unsupported platform: {job.platform}")
        
        # Обновляем результаты
        job.status = "COMPLETED"
        job.platform_job_id = result['platform_job_id']
        job.public_url = result['public_url']
        job.published_at = datetime.utcnow()
        job.error_message = None
        
        db.commit()
        
        logger.info(
            "Job completed successfully",
            submission_id=submission_id,
            platform_job_id=result['platform_job_id'],
            public_url=result['public_url']
        )
        
        return {
            'submission_id': submission_id,
            'status': 'COMPLETED',
            'result': result
        }
        
    except Exception as exc:
        logger.error(
            "Error processing job",
            submission_id=submission_id,
            error=str(exc),
            error_type=type(exc).__name__
        )
        
        # Обновляем статус в БД
        if db and job:
            job.status = "FAILED"
            job.error_message = str(exc)
            job.retry_count += 1
            db.commit()
        
        # Retry с экспоненциальным backoff
        if self.request.retries < self.max_retries:
            retry_delay = 60 * (2 ** self.request.retries)  # 60s, 120s, 240s
            logger.info(
                f"Retrying in {retry_delay}s",
                submission_id=submission_id,
                retry=self.request.retries + 1,
                max_retries=self.max_retries
            )
            raise self.retry(exc=exc, countdown=retry_delay)
        else:
            logger.error(
                "Max retries reached",
                submission_id=submission_id
            )
            raise
        
    finally:
        # Очистка временного файла
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info("Temporary file deleted", path=temp_file_path)
            except Exception as e:
                logger.warning(
                    "Failed to delete temporary file",
                    path=temp_file_path,
                    error=str(e)
                )
        
        # Закрываем сессию БД
        if db:
            db.close()


def publish_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: list,
    privacy_status: str = None
) -> dict:
    """
    Публикация на YouTube
    
    Args:
        video_path: Путь к видеофайлу
        title: Заголовок
        description: Описание
        tags: Теги
        privacy_status: Статус приватности (public, private, unlisted)
        
    Returns:
        Dict с результатами публикации
    """
    if not YOUTUBE_CLIENT_ID or not YOUTUBE_CLIENT_SECRET or not YOUTUBE_REFRESH_TOKEN:
        raise Exception(
            "YouTube credentials not configured. "
            "Set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, and YOUTUBE_REFRESH_TOKEN"
        )
    
    # Используем переданный статус или дефолтный из .env
    if privacy_status is None:
        privacy_status = YOUTUBE_DEFAULT_PRIVACY
    
    logger.info(
        "Publishing to YouTube",
        title=title,
        privacy_status=privacy_status
    )
    
    publisher = YouTubePublisher(
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
        refresh_token=YOUTUBE_REFRESH_TOKEN
    )
    
    result = publisher.publish_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status=privacy_status,
        made_for_kids=False
    )
    
    return result


def publish_to_vk(
    video_path: str,
    title: str,
    description: str,
    privacy_status: str = None
) -> dict:
    """
    Публикация на VK
    
    Args:
        video_path: Путь к видеофайлу
        title: Заголовок
        description: Описание
        privacy_status: Статус приватности (private или public)
        
    Returns:
        Dict с результатами публикации
    """
    if not VK_ACCESS_TOKEN:
        raise Exception(
            "VK credentials not configured. "
            "Set VK_ACCESS_TOKEN in .env"
        )
    
    # Используем переданный статус или дефолтный из .env
    if privacy_status is None:
        privacy_status = VK_DEFAULT_PRIVACY
    
    is_private = privacy_status == "private"
    
    logger.info(
        "Publishing to VK",
        title=title,
        is_private=is_private,
        is_clip=VK_AS_CLIP
    )
    
    publisher = VKPublisher(
        access_token=VK_ACCESS_TOKEN,
        group_id=VK_GROUP_ID if VK_GROUP_ID > 0 else None
    )
    
    result = publisher.publish_video(
        video_path=video_path,
        title=title,
        description=description,
        is_private=is_private,
        is_clip=VK_AS_CLIP,
        wallpost=False  # Не публикуем на стене автоматически
    )
    
    return result


def publish_to_tiktok(
    video_path: str,
    title: str,
    description: str,
    privacy_level: str = None
) -> dict:
    """
    Публикация на TikTok с автоматическим обновлением токена
    
    Args:
        video_path: Путь к видеофайлу
        title: Заголовок
        description: Описание
        privacy_level: Уровень приватности (SELF_ONLY, PUBLIC_TO_EVERYONE, etc.)
        
    Returns:
        Dict с результатами публикации
    """
    if not TIKTOK_CLIENT_KEY or not TIKTOK_CLIENT_SECRET or not TIKTOK_ACCESS_TOKEN:
        raise Exception(
            "TikTok credentials not configured. "
            "Set TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, and TIKTOK_ACCESS_TOKEN"
        )
    
    # Используем переданный статус или дефолтный из .env
    if privacy_level is None:
        privacy_level = TIKTOK_DEFAULT_PRIVACY
    
    logger.info(
        "Publishing to TikTok",
        title=title,
        privacy_level=privacy_level,
        has_refresh_token=bool(TIKTOK_REFRESH_TOKEN)
    )
    
    # Создаем publisher с refresh token и callback для сохранения
    publisher = TikTokPublisher(
        client_key=TIKTOK_CLIENT_KEY,
        client_secret=TIKTOK_CLIENT_SECRET,
        access_token=TIKTOK_ACCESS_TOKEN,
        refresh_token=TIKTOK_REFRESH_TOKEN if TIKTOK_REFRESH_TOKEN else None,
        on_token_refresh=save_tiktok_tokens  # Callback для автосохранения токенов
    )
    
    result = publisher.publish_video(
        video_path=video_path,
        title=title,
        description=description,
        privacy_level=privacy_level,
        disable_duet=TIKTOK_DISABLE_DUET,
        disable_comment=TIKTOK_DISABLE_COMMENT,
        disable_stitch=TIKTOK_DISABLE_STITCH
    )
    
    return result


