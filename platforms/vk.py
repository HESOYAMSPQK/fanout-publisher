"""VK (ВКонтакте) адаптер для публикации видео и клипов"""
import os
import time
import requests
import structlog
from typing import Dict, Optional

logger = structlog.get_logger()


class VKPublisher:
    """Публикация видео на VK (ВКонтакте)"""
    
    # API версия VK
    API_VERSION = "5.131"
    API_BASE_URL = "https://api.vk.com/method"
    
    def __init__(
        self,
        access_token: str,
        group_id: Optional[int] = None
    ):
        """
        Инициализация VK publisher
        
        Args:
            access_token: VK Access Token с правами video,offline
            group_id: ID группы (опционально, если публикуем от имени группы)
        """
        self.access_token = access_token
        self.group_id = group_id
        
    def _api_request(self, method: str, params: dict) -> dict:
        """
        Выполнить запрос к VK API
        
        Args:
            method: Название метода API
            params: Параметры запроса
            
        Returns:
            Ответ API
            
        Raises:
            Exception: При ошибке API
        """
        params['access_token'] = self.access_token
        params['v'] = self.API_VERSION
        
        url = f"{self.API_BASE_URL}/{method}"
        
        try:
            response = requests.post(url, data=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if 'error' in result:
                error = result['error']
                error_msg = f"VK API Error {error.get('error_code')}: {error.get('error_msg')}"
                logger.error(
                    "VK API error",
                    error_code=error.get('error_code'),
                    error_msg=error.get('error_msg')
                )
                raise Exception(error_msg)
            
            return result.get('response', {})
            
        except requests.RequestException as e:
            logger.error("VK API request failed", error=str(e))
            raise Exception(f"VK API request failed: {str(e)}")
    
    def publish_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        is_private: bool = True,
        is_clip: bool = False,
        wallpost: bool = False
    ) -> Dict[str, str]:
        """
        Публикация видео на VK
        
        Args:
            video_path: Путь к видеофайлу
            title: Заголовок видео
            description: Описание видео
            is_private: Приватное видео (True) или публичное (False)
            is_clip: Опубликовать как клип (короткое вертикальное видео)
            wallpost: Опубликовать на стене после загрузки
            
        Returns:
            Dict с platform_job_id и public_url
            
        Raises:
            Exception: При ошибке загрузки
        """
        logger.info(
            "Starting VK upload",
            title=title,
            video_path=video_path,
            is_private=is_private,
            is_clip=is_clip
        )
        
        try:
            # Проверка существования файла
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            file_size = os.path.getsize(video_path)
            
            # Шаг 1: Получить upload URL
            logger.info("Getting VK upload URL")
            
            save_params = {
                'name': title[:128],  # VK ограничивает 128 символами
                'description': description[:5000],
                'is_private': 1 if is_private else 0,
                'wallpost': 1 if wallpost else 0,
            }
            
            # Если публикуем от имени группы
            if self.group_id:
                save_params['group_id'] = self.group_id
            
            upload_data = self._api_request('video.save', save_params)
            
            upload_url = upload_data.get('upload_url')
            video_id = upload_data.get('video_id')
            owner_id = upload_data.get('owner_id')
            
            if not upload_url:
                raise Exception("Failed to get upload URL from VK")
            
            logger.info(
                "Got upload URL",
                video_id=video_id,
                owner_id=owner_id
            )
            
            # Шаг 2: Загрузить видео
            logger.info("Uploading video to VK", size=file_size)
            
            with open(video_path, 'rb') as video_file:
                files = {'video_file': video_file}
                
                upload_response = requests.post(
                    upload_url,
                    files=files,
                    timeout=600  # 10 минут на загрузку
                )
                upload_response.raise_for_status()
                
                upload_result = upload_response.json()
                
                if 'error' in upload_result:
                    raise Exception(f"Upload error: {upload_result.get('error')}")
            
            logger.info(
                "Video uploaded successfully",
                video_id=video_id,
                owner_id=owner_id
            )
            
            # Шаг 3: Если это клип, конвертируем в клип
            if is_clip:
                logger.info("Converting to clip")
                try:
                    # Пытаемся создать клип (метод может быть недоступен для некоторых аккаунтов)
                    clip_params = {
                        'video_id': video_id,
                        'owner_id': owner_id
                    }
                    self._api_request('clips.add', clip_params)
                    logger.info("Video converted to clip")
                except Exception as e:
                    logger.warning(
                        "Failed to convert to clip, keeping as regular video",
                        error=str(e)
                    )
            
            # Формируем публичную ссылку
            public_url = f"https://vk.com/video{owner_id}_{video_id}"
            
            logger.info(
                "VK upload completed",
                video_id=video_id,
                owner_id=owner_id,
                public_url=public_url
            )
            
            return {
                'platform_job_id': f"{owner_id}_{video_id}",
                'public_url': public_url,
                'status': 'uploaded'
            }
            
        except requests.RequestException as e:
            logger.error(
                "Upload request error",
                error=str(e)
            )
            raise Exception(f"VK upload request error: {str(e)}")
            
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
            video_id: ID видео в формате "{owner_id}_{video_id}"
            
        Returns:
            Dict со статусом обработки
        """
        try:
            params = {
                'videos': video_id
            }
            
            response = self._api_request('video.get', params)
            
            if not response.get('items'):
                return {'status': 'not_found'}
            
            video = response['items'][0]
            
            # VK обрабатывает видео и создает превью
            processing_status = 'ready' if video.get('player') else 'processing'
            
            return {
                'status': processing_status,
                'title': video.get('title'),
                'duration': video.get('duration'),
                'views': video.get('views', 0),
                'privacy': 'private' if video.get('is_private') else 'public'
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
            video_id: ID видео в формате "{owner_id}_{video_id}"
            
        Returns:
            True если удалено успешно
        """
        try:
            # Разбираем video_id
            parts = video_id.split('_')
            if len(parts) != 2:
                raise ValueError(f"Invalid video_id format: {video_id}")
            
            owner_id, vid = parts
            
            params = {
                'video_id': vid,
                'owner_id': owner_id
            }
            
            self._api_request('video.delete', params)
            
            logger.info("Video deleted", video_id=video_id)
            return True
            
        except Exception as e:
            logger.error(
                "Error deleting video",
                video_id=video_id,
                error=str(e)
            )
            return False



