#!/usr/bin/env python3
"""
Скрипт для тестирования API endpoint /ingest

Использование:
    python scripts/probe_ingest.py
"""
import os
import sys
import requests
import time
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
SERVICE_TOKEN = os.getenv('SERVICE_TOKEN')


def test_health():
    """Проверка health endpoint"""
    print("\n🏥 Testing /health endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Health check passed: {data}")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_ingest():
    """Проверка /ingest endpoint"""
    print("\n📤 Testing /ingest endpoint...")
    
    if not SERVICE_TOKEN:
        print("❌ SERVICE_TOKEN not set in .env")
        return None
    
    # Тестовые данные
    payload = {
        "video_hash": "test_" + str(int(time.time())),
        "s3_key": "test/video.mp4",
        "file_size": 1024000,
        "duration": 30,
        "platform": "youtube",
        "title": "Test Video from API",
        "description": "This is a test video submission",
        "tags": ["test", "shorts"],
        "telegram_user_id": "123456789"
    }
    
    headers = {
        "X-Service-Token": SERVICE_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/ingest",
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Ingest successful!")
        print(f"   Submission ID: {data['submission_id']}")
        print(f"   Status: {data['status']}")
        
        return data['submission_id']
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Response: {e.response.text}")
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_status(submission_id):
    """Проверка /status endpoint"""
    print(f"\n📊 Testing /status endpoint for {submission_id}...")
    
    if not SERVICE_TOKEN:
        print("❌ SERVICE_TOKEN not set in .env")
        return
    
    headers = {
        "X-Service-Token": SERVICE_TOKEN
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/status/{submission_id}",
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Status retrieved!")
        print(f"   Status: {data['status']}")
        print(f"   Platform: {data['platform']}")
        print(f"   Created: {data['created_at']}")
        
        if data.get('public_url'):
            print(f"   URL: {data['public_url']}")
        
        if data.get('error_message'):
            print(f"   Error: {data['error_message']}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Запуск всех тестов"""
    print("=" * 70)
    print("API Integration Test")
    print("=" * 70)
    print(f"API URL: {API_BASE_URL}")
    
    # Проверяем health
    if not test_health():
        print("\n⚠️  API is not healthy. Make sure services are running:")
        print("   docker compose up -d")
        sys.exit(1)
    
    # Тестируем ingest
    submission_id = test_ingest()
    
    if not submission_id:
        print("\n❌ Ingest test failed")
        sys.exit(1)
    
    # Ждем немного
    print("\n⏳ Waiting 2 seconds before checking status...")
    time.sleep(2)
    
    # Проверяем статус
    test_status(submission_id)
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
    print(f"\n💡 Track the submission: {API_BASE_URL}/status/{submission_id}")
    print(f"   (Remember to add X-Service-Token header)")


if __name__ == "__main__":
    main()


