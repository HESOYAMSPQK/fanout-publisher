#!/usr/bin/env python3
"""Скрипт инициализации базы данных"""
import sys
import os

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db
import structlog

logger = structlog.get_logger()

if __name__ == "__main__":
    logger.info("Initializing database...")
    
    try:
        init_db()
        logger.info("Database initialized successfully!")
        print("✅ Database tables created successfully!")
        
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        print(f"❌ Error: {e}")
        sys.exit(1)


