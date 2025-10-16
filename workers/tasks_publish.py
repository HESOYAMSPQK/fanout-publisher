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


