"""YouTube адаптер для публикации видео"""
import os
import time
import structlog
from typing import Dict, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = structlog.get_logger()


class YouTubePublisher:
    """Публикация видео на YouTube"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str
    ):
        """
        Инициализация YouTube publisher
        
        Args:
            client_id: OAuth2 Client ID
            client_secret: OAuth2 Client Secret
            refresh_token: OAuth2 Refresh Token
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.youtube = None
        
    def _get_credentials(self) -> Credentials:
        """Получить и обновить credentials"""
        creds = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
        
        # Обновляем access token
        creds.refresh(Request())
        
        return creds
    
    def _get_youtube_service(self):
        """Получить YouTube API service"""
        if not self.youtube:
            creds = self._get_credentials()
            self.youtube = build('youtube', 'v3', credentials=creds)
        return self.youtube
    
    def publish_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: Optional[list] = None,
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "public",
        made_for_kids: bool = False
    ) -> Dict[str, str]:
        """
        Публикация видео на YouTube
        
        Args:
            video_path: Путь к видеофайлу
            title: Заголовок видео
            description: Описание видео
            tags: Список тегов
            category_id: ID категории (22 = People & Blogs)
            privacy_status: Статус приватности (public, private, unlisted)
            made_for_kids: Видео для детей
            
        Returns:
            Dict с platform_job_id и public_url
            
        Raises:
            Exception: При ошибке загрузки
        """
        logger.info(
            "Starting YouTube upload",
            title=title,
            video_path=video_path,
            privacy_status=privacy_status
        )
        
        try:
            youtube = self._get_youtube_service()
            
            # Подготовка метаданных
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube ограничивает 100 символами
                    'description': description[:5000],  # Лимит 5000 символов
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': made_for_kids
                }
            }
            
            # Проверка существования файла
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Создание MediaFileUpload
            media = MediaFileUpload(
                video_path,
                mimetype='video/*',
                resumable=True,
                chunksize=10 * 1024 * 1024  # 10 MB chunks
            )
            
            # Инициализация загрузки
            request = youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            # Resumable upload с retry
            response = None
            error = None
            retry = 0
            max_retries = 5
            
            while response is None and retry < max_retries:
                try:
                    logger.info(f"Upload attempt {retry + 1}/{max_retries}")
                    status, response = request.next_chunk()
                    
                    if status:
                        progress = int(status.progress() * 100)
                        logger.info(f"Upload progress: {progress}%")
                        
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        # Серверные ошибки - retry с backoff
                        error = f"Server error: {e.resp.status}"
                        retry += 1
                        wait_time = 2 ** retry
                        logger.warning(
                            f"Server error, retrying in {wait_time}s",
                            status=e.resp.status,
                            attempt=retry
                        )
                        time.sleep(wait_time)
                    elif e.resp.status == 429:
                        # Rate limit - увеличенный backoff
                        error = "Rate limit exceeded"
                        retry += 1
                        wait_time = 60 * retry
                        logger.warning(
                            f"Rate limit, retrying in {wait_time}s",
                            attempt=retry
                        )
                        time.sleep(wait_time)
                    else:
                        # Другие ошибки - не retry
                        raise
            
            if response is None:
                raise Exception(f"Upload failed after {max_retries} retries: {error}")
            
            video_id = response['id']
            public_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(
                "Video uploaded successfully",
                video_id=video_id,
                public_url=public_url
            )
            
            # Ожидание обработки (опционально)
            # YouTube обрабатывает видео асинхронно
            # Можно добавить проверку статуса обработки
            
            return {
                'platform_job_id': video_id,
                'public_url': public_url,
                'status': 'uploaded'
            }
            
        except HttpError as e:
            error_content = e.content.decode('utf-8') if e.content else 'No details'
            logger.error(
                "YouTube API error",
                status=e.resp.status,
                reason=e.resp.reason,
                content=error_content
            )
            raise Exception(f"YouTube API error ({e.resp.status}): {error_content}")
            
        except Exception as e:
            logger.error(
                "Upload error",
                error=str(e),
                error_type=type(e).__name__
            )
            raise
    
    def get_video_status(self, video_id: str) -> Dict:
        """
        Получить статус видео
        
        Args:
            video_id: ID видео на YouTube
            
        Returns:
            Dict со статусом обработки
        """
        try:
            youtube = self._get_youtube_service()
            
            response = youtube.videos().list(
                part='status,processingDetails',
                id=video_id
            ).execute()
            
            if not response.get('items'):
                return {'status': 'not_found'}
            
            video = response['items'][0]
            status = video.get('status', {})
            processing = video.get('processingDetails', {})
            
            return {
                'status': processing.get('processingStatus', 'unknown'),
                'upload_status': status.get('uploadStatus', 'unknown'),
                'privacy_status': status.get('privacyStatus', 'unknown'),
                'processing_progress': processing.get('processingProgress', {})
            }
            
        except Exception as e:
            logger.error(
                "Error getting video status",
                video_id=video_id,
                error=str(e)
            )
            return {'status': 'error', 'error': str(e)}
    
    def delete_video(self, video_id: str) -> bool:
        """
        Удалить видео (для тестирования)
        
        Args:
            video_id: ID видео на YouTube
            
        Returns:
            True если удалено успешно
        """
        try:
            youtube = self._get_youtube_service()
            youtube.videos().delete(id=video_id).execute()
            
            logger.info("Video deleted", video_id=video_id)
            return True
            
        except Exception as e:
            logger.error(
                "Error deleting video",
                video_id=video_id,
                error=str(e)
            )
            return False


