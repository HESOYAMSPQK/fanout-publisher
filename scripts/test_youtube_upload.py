#!/usr/bin/env python3
"""
Скрипт для тестирования загрузки на YouTube

Требует:
- Настроенные YouTube credentials в .env
- Тестовое видео файл
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platforms.youtube import YouTubePublisher
from dotenv import load_dotenv

load_dotenv()


def test_upload(video_path: str):
    """Тестовая загрузка на YouTube"""
    
    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ YouTube credentials not configured!")
        print("   Set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN in .env")
        sys.exit(1)
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        sys.exit(1)
    
    print("🚀 Starting YouTube upload test...")
    print(f"   Video: {video_path}")
    print(f"   Size: {os.path.getsize(video_path) / 1024 / 1024:.2f} MB")
    
    try:
        publisher = YouTubePublisher(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )
        
        result = publisher.publish_video(
            video_path=video_path,
            title=f"Test Upload {os.path.basename(video_path)}",
            description="This is a test upload from Fanout Publisher",
            tags=["test", "shorts"],
            privacy_status="unlisted"  # unlisted для теста
        )
        
        print("\n✅ Upload successful!")
        print(f"   Video ID: {result['platform_job_id']}")
        print(f"   URL: {result['public_url']}")
        print(f"   Status: {result['status']}")
        
        # Проверяем статус обработки
        print("\n⏳ Checking processing status...")
        status = publisher.get_video_status(result['platform_job_id'])
        print(f"   Processing status: {status.get('status')}")
        print(f"   Upload status: {status.get('upload_status')}")
        
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_youtube_upload.py <video_file>")
        print("\nExample:")
        print("  python scripts/test_youtube_upload.py test_video.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    test_upload(video_path)


