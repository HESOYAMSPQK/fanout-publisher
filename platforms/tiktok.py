"""TikTok адаптер для публикации видео через Content Posting API"""
import os
import json
import time
import requests
import structlog
from typing import Dict, Optional, Callable
import hashlib

logger = structlog.get_logger()


class TikTokPublisher:
    """Публикация видео на TikTok через Content Posting API"""
    
    # API endpoints
    API_BASE_URL = "https://open.tiktokapis.com"
    OAUTH_URL = "https://www.tiktok.com/v2/auth/authorize"
    TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
    
    # API версия
    API_VERSION = "v2"
    
    def __init__(
        self,
        client_key: str,
        client_secret: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        on_token_refresh: Optional[Callable[[str, str], None]] = None
    ):
        """
        Инициализация TikTok publisher
        
        Args:
            client_key: TikTok App Client Key
            client_secret: TikTok App Client Secret  
            access_token: OAuth Access Token пользователя
            refresh_token: OAuth Refresh Token для автоматического обновления
            on_token_refresh: Callback функция для сохранения нового токена (access_token, refresh_token)
        """
        self.client_key = client_key
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.on_token_refresh = on_token_refresh
    
    def _refresh_access_token(self) -> bool:
        """
        Обновить access token используя refresh token
        
        Returns:
            True если токен успешно обновлен, False иначе
        """
        if not self.refresh_token:
            logger.warning("Refresh token not available, cannot refresh access token")
            return False
        
        logger.info("Attempting to refresh TikTok access token")
        
        try:
            data = {
                'client_key': self.client_key,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache'
            }
            
            response = requests.post(self.TOKEN_URL, data=data, headers=headers, timeout=30)
            result = response.json()
            
            # Проверка на ошибки
            if 'error' in result:
                error_code = result.get('error', '')
                error_msg = result.get('error_description', '')
                logger.error(
                    "Failed to refresh token",
                    error_code=error_code,
                    error_msg=error_msg
                )
                return False
            
            # Извлекаем новые токены
            if 'data' in result:
                token_info = result['data']
            else:
                token_info = result
            
            new_access_token = token_info.get('access_token')
            new_refresh_token = token_info.get('refresh_token')
            expires_in = token_info.get('expires_in', 0)
            
            if not new_access_token:
                logger.error("No access token in refresh response")
                return False
            
            # Обновляем токены
            old_access_token = self.access_token
            self.access_token = new_access_token
            
            if new_refresh_token:
                self.refresh_token = new_refresh_token
            
            logger.info(
                "✅ Access token refreshed successfully",
                expires_in=expires_in,
                expires_in_hours=expires_in // 3600
            )
            
            # Вызываем callback если он задан (для сохранения токена в .env или БД)
            if self.on_token_refresh:
                try:
                    self.on_token_refresh(self.access_token, self.refresh_token)
                    logger.info("Token refresh callback executed successfully")
                except Exception as e:
                    logger.warning(
                        "Token refresh callback failed",
                        error=str(e)
                    )
            
            return True
            
        except requests.RequestException as e:
            logger.error("Token refresh request failed", error=str(e))
            return False
        except Exception as e:
            logger.error(
                "Unexpected error during token refresh",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
        
    def _api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
        headers: Optional[dict] = None,
        retry_on_token_error: bool = True
    ) -> dict:
        """
        Выполнить запрос к TikTok API с автоматическим обновлением токена при ошибке
        
        Args:
            method: HTTP метод (GET, POST)
            endpoint: API endpoint
            data: JSON данные
            files: Файлы для загрузки
            headers: Дополнительные заголовки
            retry_on_token_error: Повторить запрос с обновленным токеном при ошибке авторизации
            
        Returns:
            Ответ API
            
        Raises:
            Exception: При ошибке API
        """
        url = f"{self.API_BASE_URL}/{endpoint}"
        
        # Базовые заголовки
        default_headers = {
            'Authorization': f'Bearer {self.access_token}',
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=default_headers, params=data, timeout=30)
            elif method.upper() == 'POST':
                if files:
                    # Для загрузки файлов не отправляем Content-Type (requests сам установит multipart/form-data)
                    response = requests.post(url, headers=default_headers, data=data, files=files, timeout=600)
                else:
                    # Если явно указан x-www-form-urlencoded, отправляем как form-data
                    content_type = default_headers.get('Content-Type')
                    logger.info("Sending POST request", url=url, data=data)
                    if content_type == 'application/x-www-form-urlencoded':
                        response = requests.post(url, headers=default_headers, data=data, timeout=30)
                    else:
                        default_headers['Content-Type'] = 'application/json'
                        response = requests.post(url, headers=default_headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Логируем ответ для отладки
            logger.info("Response received", status_code=response.status_code)
            
            # Если ошибка, логируем тело ответа
            if not response.ok:
                try:
                    error_body = response.json()
                    error_code = error_body.get('error', {}).get('code', '')
                    error_msg = error_body.get('error', {}).get('message', '')
                    
                    # Проверяем, связана ли ошибка с токеном
                    token_related_errors = [
                        'access_token_invalid',
                        'access_token_expired', 
                        'invalid_token',
                        'token_expired',
                        'unauthorized'
                    ]
                    
                    is_token_error = error_code in token_related_errors or 'token' in error_code.lower()
                    
                    logger.error(
                        "TikTok API error response",
                        status_code=response.status_code,
                        error_code=error_code,
                        error_message=error_msg,
                        is_token_error=is_token_error,
                        error_body=error_body,
                        url=url
                    )
                    
                    # Если это ошибка токена и есть refresh_token - пробуем обновить
                    if is_token_error and retry_on_token_error and self.refresh_token:
                        logger.info("🔄 Обнаружена ошибка токена, пытаемся обновить...")
                        
                        if self._refresh_access_token():
                            logger.info("✅ Токен обновлен, повторяем запрос...")
                            # Повторяем запрос с новым токеном (без повторного retry)
                            return self._api_request(
                                method=method,
                                endpoint=endpoint,
                                data=data,
                                files=files,
                                headers=headers,
                                retry_on_token_error=False  # Не повторяем бесконечно
                            )
                        else:
                            logger.error("❌ Не удалось обновить токен")
                    
                except:
                    logger.error(
                        "TikTok API error response (non-JSON)",
                        status_code=response.status_code,
                        text=response.text[:500],
                        url=url
                    )
            
            response.raise_for_status()
            
            result = response.json()
            
            # Проверка на ошибки TikTok API
            if result.get('error'):
                error = result['error']
                error_code = error.get('code', '')
                error_message = error.get('message', '')

                # Некоторые ответы включают wrapper error: { code: 'ok' } при status_code=200
                # Не трактуем такие ответы как ошибку
                normalized_code = str(error_code).lower()
                if normalized_code in ('ok', 'success', '0', '200', ''):
                    return result
                
                # Проверяем, связана ли ошибка с токеном
                token_related_errors = [
                    'access_token_invalid',
                    'access_token_expired', 
                    'invalid_token',
                    'token_expired',
                    'unauthorized'
                ]
                
                is_token_error = error_code in token_related_errors or 'token' in error_code.lower()
                
                # Если это ошибка токена и есть refresh_token - пробуем обновить
                if is_token_error and retry_on_token_error and self.refresh_token:
                    logger.info("🔄 Обнаружена ошибка токена в JSON, пытаемся обновить...")
                    
                    if self._refresh_access_token():
                        logger.info("✅ Токен обновлен, повторяем запрос...")
                        # Повторяем запрос с новым токеном (без повторного retry)
                        return self._api_request(
                            method=method,
                            endpoint=endpoint,
                            data=data,
                            files=files,
                            headers=headers,
                            retry_on_token_error=False  # Не повторяем бесконечно
                        )
                    else:
                        logger.error("❌ Не удалось обновить токен")
                
                if is_token_error:
                    error_msg = f"❌ ОШИБКА ТОКЕНА TikTok! Код: {error_code} - {error_message}\n\n"
                    error_msg += "🔑 Ваш токен истёк или недействителен!\n"
                    if self.refresh_token:
                        error_msg += "Автоматическое обновление не удалось. Получите новый токен: python scripts/get_tiktok_token_ngrok.py"
                    else:
                        error_msg += "Добавьте TIKTOK_REFRESH_TOKEN в .env для автоматического обновления токена"
                else:
                    error_msg = f"TikTok API Error: {error_code} - {error_message}"
                
                logger.error(
                    "TikTok API error",
                    error_code=error_code,
                    error_message=error_message,
                    is_token_error=is_token_error,
                    log_id=result.get('log_id')
                )
                raise Exception(error_msg)
            
            return result
            
        except requests.RequestException as e:
            logger.error("TikTok API request failed", error=str(e), url=url)
            raise Exception(f"TikTok API request failed: {str(e)}")
    
    def publish_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        privacy_level: str = "SELF_ONLY",
        disable_duet: bool = False,
        disable_comment: bool = False,
        disable_stitch: bool = False,
        brand_content: bool = False,
        brand_organic: bool = False
    ) -> Dict[str, str]:
        """
        Публикация видео на TikTok
        
        Args:
            video_path: Путь к видеофайлу
            title: Заголовок видео (опционально, TikTok может использовать первые слова description)
            description: Описание/caption видео (до 2200 символов)
            privacy_level: Уровень приватности:
                - SELF_ONLY: только автор (приватное)
                - MUTUAL_FOLLOW_FRIENDS: взаимные подписчики
                - FOLLOWER_OF_CREATOR: все подписчики
                - PUBLIC_TO_EVERYONE: публичное
            disable_duet: Отключить дуэты
            disable_comment: Отключить комментарии
            disable_stitch: Отключить стич
            brand_content: Помечено как брендированный контент
            brand_organic: Органический брендированный контент
            
        Returns:
            Dict с platform_job_id и public_url
            
        Raises:
            Exception: При ошибке загрузки
        """
        logger.info(
            "Starting TikTok upload",
            title=title,
            video_path=video_path,
            privacy_level=privacy_level
        )
        
        try:
            # Проверка существования файла
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            file_size = os.path.getsize(video_path)
            
            # Проверка размера (TikTok: максимум 4 ГБ для видео до 10 минут)
            if file_size > 4 * 1024 * 1024 * 1024:
                raise Exception("Video file too large (max 4 GB)")
            
            logger.info("Video file validated", size=file_size)
            
            # Шаг 1: Инициализация загрузки (получение upload URL)
            logger.info("Initializing TikTok upload")
            
            # TikTok API ТРЕБУЕТ информацию о видео (title/description)!
            # Формируем текстовое содержимое для TikTok
            video_caption = ""
            if title and title.strip():
                video_caption = title.strip()
            if description and description.strip():
                if video_caption:
                    video_caption += "\n\n" + description.strip()
                else:
                    video_caption = description.strip()
            
            # Если вообще нет текста, используем дефолтное значение
            if not video_caption:
                video_caption = "Видео"
            
            # Ограничение TikTok: максимум 2200 символов
            if len(video_caption) > 2200:
                video_caption = video_caption[:2197] + "..."
            
            # Формируем post_info для TikTok API v2
            # Из рабочего примера jstolpe: поле называется "title"
            post_info = {
                "title": video_caption,
                "privacy_level": privacy_level,
                "disable_duet": disable_duet,
                "disable_comment": disable_comment,
                "disable_stitch": disable_stitch
            }
            
            logger.info(
                "TikTok post_info prepared",
                description=video_caption[:100],  # Логируем первые 100 символов
                description_length=len(video_caption),
                privacy_level=privacy_level
            )
            
            # Формируем source_info
            # Из рабочего примера jstolpe: для FILE_UPLOAD нужны chunk_size и total_chunk_count
            # Если отправляем файл целиком, chunk_size = file_size, total_chunk_count = 1
            source_info = {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": file_size,
                "total_chunk_count": 1
            }

            # Инициализацию отправляем как x-www-form-urlencoded с JSON-строками
            form_payload = {
                "post_info": json.dumps(post_info, ensure_ascii=False),
                "source_info": json.dumps(source_info)
            }

            logger.info(
                "About to send init request",
                post_info_keys=list(post_info.keys()),
                source_info_keys=list(source_info.keys()),
                title_repr=repr(post_info['title'][:50] if post_info.get('title') else '')
            )

            init_response = self._api_request(
                'POST',
                f'{self.API_VERSION}/post/publish/video/init/',
                data=form_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            upload_url = init_response.get('data', {}).get('upload_url')
            publish_id = init_response.get('data', {}).get('publish_id')
            
            if not upload_url or not publish_id:
                raise Exception("Failed to get upload URL from TikTok")
            
            logger.info(
                "Got upload URL",
                publish_id=publish_id
            )
            
            # Шаг 2: Загрузка видео
            logger.info("Uploading video to TikTok", size=file_size, upload_url=upload_url)
            
            with open(video_path, 'rb') as video_file:
                # TikTok upload требует Content-Range при загрузке файла
                content_range = f"bytes 0-{file_size - 1}/{file_size}"
                upload_headers = {
                    'Content-Type': 'video/mp4',
                    'Content-Length': str(file_size),
                    'Content-Range': content_range
                }
                logger.info("PUT upload start", content_range=content_range)
                upload_response = requests.put(
                    upload_url,
                    data=video_file,
                    headers=upload_headers,
                    timeout=600  # 10 минут на загрузку
                )
                logger.info("PUT upload finished", status_code=upload_response.status_code)
                upload_response.raise_for_status()
            
            logger.info("Video uploaded successfully", publish_id=publish_id)
            
            # Шаг 3: Проверка статуса публикации
            # TikTok обрабатывает видео асинхронно
            # Можно сразу вернуть результат или подождать обработки
            
            # Формируем URL (TikTok не возвращает прямую ссылку сразу)
            # Ссылка будет доступна после обработки через creator center
            public_url = f"https://www.tiktok.com/@me/video/{publish_id}"  # Примерный формат
            
            logger.info(
                "TikTok upload completed",
                publish_id=publish_id,
                status="processing"
            )
            
            return {
                'platform_job_id': publish_id,
                'public_url': public_url,
                'status': 'processing'  # TikTok обрабатывает асинхронно
            }
            
        except requests.RequestException as e:
            logger.error(
                "Upload request error",
                error=str(e)
            )
            raise Exception(f"TikTok upload request error: {str(e)}")
            
        except Exception as e:
            logger.error(
                "Upload error",
                error=str(e),
                error_type=type(e).__name__
            )
            raise
    
    def get_video_status(self, publish_id: str) -> Dict:
        """
        Получить статус видео
        
        Args:
            publish_id: ID публикации на TikTok
            
        Returns:
            Dict со статусом обработки
        """
        try:
            endpoint = f'{self.API_VERSION}/post/publish/status/{publish_id}/'
            
            response = self._api_request('POST', endpoint)
            
            data = response.get('data', {})
            
            status = data.get('status', 'unknown')
            
            # TikTok статусы: PROCESSING_UPLOAD, PUBLISH_COMPLETE, FAILED, etc.
            
            return {
                'status': status,
                'publish_id': publish_id,
                'fail_reason': data.get('fail_reason'),
                'publicaly_available_post_id': data.get('publicaly_available_post_id', [])
            }
            
        except Exception as e:
            logger.error(
                "Error getting video status",
                publish_id=publish_id,
                error=str(e)
            )
            return {'status': 'error', 'error': str(e)}
    
    def get_creator_info(self) -> Dict:
        """
        Получить информацию о creator аккаунте
        
        Returns:
            Dict с информацией о пользователе
        """
        try:
            endpoint = f'{self.API_VERSION}/user/info/'
            
            response = self._api_request('GET', endpoint, data={'fields': 'open_id,union_id,avatar_url,display_name'})
            
            data = response.get('data', {}).get('user', {})
            
            return {
                'open_id': data.get('open_id'),
                'display_name': data.get('display_name'),
                'avatar_url': data.get('avatar_url')
            }
            
        except Exception as e:
            logger.error("Error getting creator info", error=str(e))
            return {'error': str(e)}



