"""Конфигурация Celery приложения"""
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Создание Celery приложения
celery_app = Celery(
    'fanout_publisher',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'),
    include=['workers.tasks_publish']
)

# Конфигурация
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 час максимум на задачу
    task_soft_time_limit=3300,  # 55 минут мягкий лимит
    worker_prefetch_multiplier=1,  # Берем по одной задаче
    task_acks_late=True,  # Подтверждаем после выполнения
    task_reject_on_worker_lost=True,
    worker_max_tasks_per_child=50,  # Перезапуск воркера после 50 задач
)

# Настройки retry
celery_app.conf.task_default_retry_delay = 60  # 1 минута между retry
celery_app.conf.task_max_retries = 3


