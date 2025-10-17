"""Главное приложение FastAPI"""
from fastapi import FastAPI, Depends, HTTPException, Header, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
import structlog
import uuid
import hashlib
import tempfile
import os
from datetime import datetime
from minio import Minio

from app.config import get_settings
from app.database import get_db, init_db, PublishJob
from app.schemas import IngestRequest, IngestResponse, StatusResponse, HealthResponse
from workers.tasks_publish import publish_submission

# Настройка структурного логирования
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()
settings = get_settings()

app = FastAPI(
    title="Fanout Publisher API",
    description="API для автоматической публикации видео на различные платформы",
    version="1.0.0"
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Инициализация MinIO клиента
minio_client = None


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения"""
    global minio_client
    logger.info("Starting Fanout Publisher API")
    init_db()
    logger.info("Database initialized")
    
    # Инициализация MinIO
    minio_client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE
    )
    
    # Проверка и создание bucket
    try:
        if not minio_client.bucket_exists(settings.MINIO_BUCKET):
            minio_client.make_bucket(settings.MINIO_BUCKET)
            logger.info("Created MinIO bucket", bucket=settings.MINIO_BUCKET)
    except Exception as e:
        logger.error("Error checking/creating MinIO bucket", error=str(e))
    
    logger.info("MinIO initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке приложения"""
    logger.info("Shutting down Fanout Publisher API")


async def verify_service_token(x_service_token: Optional[str] = Header(None)):
    """Проверка сервисного токена"""
    if not x_service_token:
        logger.warning("Missing service token in request")
        raise HTTPException(status_code=401, detail="Missing X-Service-Token header")
    
    if x_service_token != settings.SERVICE_TOKEN:
        logger.warning("Invalid service token", token_prefix=x_service_token[:10])
        raise HTTPException(status_code=403, detail="Invalid service token")
    
    return True


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница - возвращает веб-интерфейс"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Welcome to Fanout Publisher API</h1>", status_code=200)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="fanout-publisher-api"
    )


@app.post("/ingest", response_model=IngestResponse)
async def ingest_video(
    request: IngestRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_service_token)
):
    """
    Принять видео для публикации
    
    Создает задачу публикации и помещает её в очередь Celery
    """
    try:
        # Генерируем submission_id
        submission_id = str(uuid.uuid4())
        
        # Проверка идемпотентности (опционально, для повторных запросов)
        existing = db.query(PublishJob).filter_by(
            video_hash=request.video_hash,
            platform=request.platform
        ).first()
        
        if existing and existing.status in ["PENDING", "PROCESSING", "COMPLETED"]:
            logger.info(
                "Duplicate submission detected, returning existing",
                submission_id=existing.submission_id,
                status=existing.status
            )
            return IngestResponse(
                submission_id=existing.submission_id,
                status="QUEUED"
            )
        
        # Создаем новую задачу
        job = PublishJob(
            id=str(uuid.uuid4()),
            submission_id=submission_id,
            video_hash=request.video_hash,
            s3_key=request.s3_key,
            file_size=request.file_size,
            duration=request.duration,
            platform=request.platform,
            title=request.title,
            description=request.description,
            tags=request.tags or [],
            status="PENDING"
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        logger.info(
            "Created publish job",
            submission_id=submission_id,
            platform=request.platform,
            job_id=job.id
        )
        
        # Отправляем задачу в Celery
        publish_submission.delay(submission_id)
        
        logger.info(
            "Job queued for processing",
            submission_id=submission_id
        )
        
        return IngestResponse(
            submission_id=submission_id,
            status="QUEUED"
        )
        
    except Exception as e:
        logger.error(
            "Error creating publish job",
            error=str(e),
            error_type=type(e).__name__
        )
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/status/{submission_id}", response_model=StatusResponse)
async def get_status(
    submission_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_service_token)
):
    """Получить статус публикации"""
    job = db.query(PublishJob).filter_by(submission_id=submission_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return StatusResponse(
        submission_id=job.submission_id,
        status=job.status,
        platform=job.platform,
        platform_job_id=job.platform_job_id,
        public_url=job.public_url,
        error_message=job.error_message,
        retry_count=job.retry_count,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
        published_at=job.published_at.isoformat() if job.published_at else None
    )


@app.post("/retry_failed/{submission_id}")
async def retry_failed(
    submission_id: str,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_service_token)
):
    """Повторить неудавшуюся публикацию"""
    job = db.query(PublishJob).filter_by(submission_id=submission_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if job.status != "FAILED":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not in FAILED status (current: {job.status})"
        )
    
    # Сброс статуса и отправка в очередь
    job.status = "PENDING"
    job.error_message = None
    db.commit()
    
    logger.info(
        "Retrying failed job",
        submission_id=submission_id,
        retry_count=job.retry_count
    )
    
    publish_submission.delay(submission_id)
    
    return JSONResponse(
        content={
            "submission_id": submission_id,
            "status": "QUEUED",
            "message": "Job re-queued for processing"
        }
    )


@app.post("/upload")
async def upload_video(
    video: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form("[]"),
    hashtags: str = Form(""),
    privacy: str = Form("private"),
    platforms: str = Form('["youtube"]'),
    db: Session = Depends(get_db)
):
    """
    Загрузка видео через веб-форму
    
    Принимает видео файл, сохраняет в MinIO и создает задачи публикации
    для выбранных платформ
    """
    try:
        import json
        
        # Парсим список платформ
        try:
            platforms_list = json.loads(platforms)
        except:
            platforms_list = ["youtube"]
        
        if not platforms_list:
            raise HTTPException(status_code=400, detail="Выберите хотя бы одну платформу")
        
        logger.info(
            "Web upload started",
            filename=video.filename,
            title=title,
            platforms=platforms_list
        )
        
        # Проверка размера файла (2 ГБ)
        content = await video.read()
        file_size = len(content)
        
        if file_size > 2 * 1024 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Файл слишком большой! Максимальный размер: 2 ГБ")
        
        # Вычисляем хеш
        video_hash = hashlib.sha256(content).hexdigest()
        
        # Генерируем S3 ключ
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        s3_key = f"videos/web/{timestamp}_{video_hash[:16]}.mp4"
        
        # Загружаем в MinIO
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            with open(temp_path, 'rb') as f:
                minio_client.put_object(
                    settings.MINIO_BUCKET,
                    s3_key,
                    f,
                    length=file_size,
                    content_type=video.content_type or "video/mp4"
                )
        finally:
            os.unlink(temp_path)
        
        logger.info(
            "Video uploaded to MinIO",
            s3_key=s3_key,
            video_hash=video_hash
        )
        
        # Парсим теги
        try:
            tags_list = json.loads(tags)
        except:
            tags_list = []
        
        # Убрал автоматическое добавление хештега
        
        # Создаем задачи публикации для каждой платформы
        submissions = []
        
        for platform in platforms_list:
            submission_id = str(uuid.uuid4())
            
            # Адаптируем контент под платформу
            platform_title = title
            platform_description = description
            
            if platform == "youtube":
                # Для YouTube добавляем хештеги к названию
                if hashtags.strip():
                    platform_title = f"{title} {hashtags}".strip()
            elif platform == "tiktok":
                # Для TikTok добавляем хештеги к описанию
                if hashtags.strip():
                    platform_description = f"{description}\n\n{hashtags}".strip()
            elif platform == "vk":
                # Для VK тоже можно добавить хештеги к описанию
                if hashtags.strip():
                    platform_description = f"{description}\n\n{hashtags}".strip()
            
            job = PublishJob(
                id=str(uuid.uuid4()),
                submission_id=submission_id,
                video_hash=video_hash,
                s3_key=s3_key,
                file_size=file_size,
                duration=None,  # TODO: можно извлечь из видео
                platform=platform,
                title=platform_title,
                description=platform_description,
                tags=tags_list if platform == "youtube" else [],
                status="PENDING"
            )
            
            db.add(job)
            db.commit()
            db.refresh(job)
            
            logger.info(
                "Created publish job",
                submission_id=submission_id,
                platform=platform,
                job_id=job.id
            )
            
            # Отправляем задачу в Celery
            publish_submission.delay(submission_id)
            
            logger.info(
                "Job queued for processing",
                submission_id=submission_id
            )
            
            submissions.append({
                "submission_id": submission_id,
                "platform": platform
            })
        
        return {
            "status": "QUEUED",
            "message": f"Видео успешно загружено и отправлено на публикацию на {len(submissions)} платформ(у)",
            "submissions": submissions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error uploading video",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке: {str(e)}")


@app.get("/api/status/{submission_id}", response_model=StatusResponse)
async def get_status_api(
    submission_id: str,
    db: Session = Depends(get_db)
):
    """Получить статус публикации (публичный API для веб-интерфейса)"""
    job = db.query(PublishJob).filter_by(submission_id=submission_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return StatusResponse(
        submission_id=job.submission_id,
        status=job.status,
        platform=job.platform,
        platform_job_id=job.platform_job_id,
        public_url=job.public_url,
        error_message=job.error_message,
        retry_count=job.retry_count,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
        published_at=job.published_at.isoformat() if job.published_at else None
    )


@app.get("/api/jobs")
async def get_recent_jobs(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Получить список последних загрузок"""
    jobs = db.query(PublishJob).order_by(PublishJob.created_at.desc()).limit(limit).all()
    
    return [
        {
            "submission_id": job.submission_id,
            "title": job.title,
            "platform": job.platform,
            "status": job.status,
            "public_url": job.public_url,
            "error_message": job.error_message,
            "created_at": job.created_at.isoformat(),
            "published_at": job.published_at.isoformat() if job.published_at else None
        }
        for job in jobs
    ]


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик исключений"""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        error_type=type(exc).__name__
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


