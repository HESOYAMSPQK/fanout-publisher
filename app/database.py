"""Настройка базы данных и моделей"""
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from app.config import get_settings

settings = get_settings()

# Создание движка БД
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class PublishJob(Base):
    """Модель задачи публикации"""
    __tablename__ = "publish_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, unique=True, nullable=False, index=True)
    
    # Видео
    video_hash = Column(String, nullable=False, index=True)
    s3_key = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=True)  # секунды
    
    # Метаданные публикации
    platform = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True, default=list)
    
    # Статус
    status = Column(String, nullable=False, default="PENDING", index=True)
    # PENDING -> PROCESSING -> COMPLETED / FAILED
    
    # Результаты публикации
    platform_job_id = Column(String, nullable=True)
    public_url = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)
    
    # Telegram metadata
    telegram_user_id = Column(String, nullable=True)
    telegram_message_id = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<PublishJob(id={self.id}, platform={self.platform}, status={self.status})>"


def get_db():
    """Dependency для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализация базы данных (создание таблиц)"""
    Base.metadata.create_all(bind=engine)


