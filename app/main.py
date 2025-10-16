"""Главное приложение FastAPI"""
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import structlog
import uuid
from datetime import datetime

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


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения"""
    logger.info("Starting Fanout Publisher API")
    init_db()
    logger.info("Database initialized")


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
            status="PENDING",
            telegram_user_id=request.telegram_user_id,
            telegram_message_id=request.telegram_message_id
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


