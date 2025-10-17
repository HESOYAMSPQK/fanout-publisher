# 🗺️ Roadmap интеграции платформ

После успешной реализации YouTube Shorts, следующие платформы будут интегрированы в систему.

---

## ✅ Milestone 1: YouTube Shorts (РЕАЛИЗОВАНО)

**Статус:** ✅ Готово  
**API:** YouTube Data API v3  
**Тип авторизации:** OAuth2  
**Лимиты:** 10,000 units/day (можно увеличить по запросу)

### Требования к видео:
- Формат: MP4, WebM, MOV
- Вертикальное: 9:16 (1080×1920)
- Длительность: до 60 секунд для Shorts
- Размер: до 256 ГБ (практически до 2 ГБ по умолчанию)

---

## 📋 Milestone 2: Instagram Reels & TikTok

### 📸 Instagram Reels

**Приоритет:** Высокий  
**Статус:** 🔄 В планах  
**API:** Instagram Graph API (Meta)

#### Официальный способ (рекомендуется):

**Требования:**
- Meta App в Facebook for Developers
- Instagram Business или Creator аккаунт
- Facebook Page, связанная с Instagram
- Access Token с permissions:
  - `instagram_content_publish`
  - `instagram_basic`
  - `pages_read_engagement`

**Шаги интеграции:**
1. Создать Meta App: https://developers.facebook.com/apps/
2. Добавить продукт "Instagram Graph API"
3. Настроить OAuth и получить долгосрочный токен
4. Получить Instagram Business Account ID
5. Использовать Container API для загрузки Reels

**Endpoints:**
```
POST /{ig-user-id}/media
  ?media_type=REELS
  &video_url={public_video_url}
  &caption={caption}
  &share_to_feed=true

POST /{ig-user-id}/media_publish
  ?creation_id={container_id}
```

**Лимиты:**
- До 25 постов в сутки на аккаунт
- Видео: 3-90 секунд
- Размер: до 100 МБ
- Формат: 9:16 рекомендуется (мин. 1.91:1, макс. 9:16)
- Разрешение: минимум 500×888 пикселей

**Альтернативы (неофициальные):**
- `instagrapi` - Python библиотека для Instagram Private API
  - ⚠️ Риск блокировки аккаунта
  - Требует логин/пароль
  - Обход 2FA сложен

**План реализации:**
```python
# platforms/instagram.py

class InstagramPublisher:
    def __init__(self, access_token, instagram_account_id):
        self.access_token = access_token
        self.account_id = instagram_account_id
        
    def publish_reel(self, video_url, caption, cover_url=None):
        # 1. Создать container
        container_id = self._create_container(video_url, caption, cover_url)
        
        # 2. Дождаться обработки
        self._wait_for_processing(container_id)
        
        # 3. Опубликовать
        media_id = self._publish_container(container_id)
        
        return {
            'platform_job_id': media_id,
            'public_url': f'https://www.instagram.com/reel/{media_id}/'
        }
```

---

### 🎵 TikTok

**Приоритет:** Высокий  
**Статус:** 🔄 В планах  
**API:** TikTok for Developers - Content Posting API

#### Официальный способ (рекомендуется):

**Требования:**
- TikTok Developer аккаунт: https://developers.tiktok.com/
- Создать приложение
- Пройти ревью приложения (может занять несколько дней)
- Получить одобрение для Content Posting API
- OAuth 2.0 авторизация пользователей

**Шаги интеграции:**
1. Зарегистрироваться на https://developers.tiktok.com/
2. Создать приложение
3. Запросить доступ к "Content Posting API"
4. Настроить OAuth redirect URL
5. Реализовать OAuth flow
6. Использовать Upload API

**Endpoints:**
```
POST /v2/post/publish/video/init/
  - Инициализация загрузки

PUT {upload_url}
  - Загрузка видео

POST /v2/post/publish/status/fetch/
  - Проверка статуса
```

**Лимиты:**
- Лимиты зависят от уровня доступа (обычно до 5-10 постов/день на пользователя)
- Видео: 3 секунды - 10 минут
- Размер: до 287.6 МБ (может меняться)
- Форматы: MP4, MOV, MPEG, AVI, WebM
- Разрешение: 720p или выше (рекомендуется 1080p)
- Соотношение: 9:16 для вертикальных (рекомендуется)

**Альтернативы (неофициальные):**
- `TikTokApi` - Python библиотека
  - ⚠️ Требует запуск браузера (Selenium/Playwright)
  - Нестабильно из-за изменений API
  - Риск блокировки

**План реализации:**
```python
# platforms/tiktok.py

class TikTokPublisher:
    def __init__(self, access_token):
        self.access_token = access_token
        
    def publish_video(self, video_path, title, privacy_level='PUBLIC_TO_EVERYONE'):
        # 1. Инициализация загрузки
        init_response = self._init_upload()
        
        # 2. Загрузка видео chunks
        self._upload_video(init_response['upload_url'], video_path)
        
        # 3. Публикация
        publish_response = self._publish(
            init_response['publish_id'],
            title,
            privacy_level
        )
        
        return {
            'platform_job_id': publish_response['video_id'],
            'public_url': f'https://www.tiktok.com/@username/video/{publish_response["video_id"]}'
        }
```

---

## 📋 Milestone 3: Российские платформы

### 🔵 ВКонтакте (VK)

**Приоритет:** Высокий  
**Статус:** ✅ Реализовано (добавлено 2025-10-16)  
**API:** VK API v5.131

#### Официальный способ:

**Требования:**
- VK приложение через VK ID: https://id.vk.com/
- Access Token с scope `video,offline`
- Standalone приложение (создается через VK ID с 2024 года)

**Шаги интеграции:**
1. Создать Standalone-приложение на https://id.vk.com/
2. Получить ID приложения
3. Реализовать OAuth для получения Access Token
4. Использовать Video API

**Endpoints:**
```
POST /method/video.save
  ?name={title}
  &description={description}
  &is_private=0
  &wallpost=1
  
  → Возвращает upload_url

POST {upload_url}
  - Загрузка видеофайла
  
  → Возвращает video_id
```

**Лимиты:**
- До 1500 запросов в сутки (зависит от настроек приложения)
- Видео: до 5 ГБ
- Длительность: до 6 часов
- Форматы: MP4, AVI, MPG, 3GP, FLV, MOV, WMV, MKV, WebM

**Особенности:**
- Поддержка Stories через `stories.getVideoUploadServer`
- Можно публиковать на стену сообщества
- Можно добавлять в альбомы

**Реализация:**
```python
# platforms/vk.py - ✅ РЕАЛИЗОВАНО

class VKPublisher:
    def __init__(self, access_token, group_id=None):
        self.access_token = access_token
        self.group_id = group_id
    
    def publish_video(self, video_path, title, description, 
                     is_private=True, is_clip=False, wallpost=False):
        # 1. Получить upload URL через video.save
        upload_data = self._api_request('video.save', {
            'name': title,
            'description': description,
            'is_private': 1 if is_private else 0,
            'wallpost': 1 if wallpost else 0,
            'group_id': self.group_id if self.group_id else None
        })
        
        # 2. Загрузить видео на upload_url
        with open(video_path, 'rb') as f:
            upload_response = requests.post(upload_data['upload_url'], 
                                           files={'video_file': f})
        
        # 3. Опционально конвертировать в клип
        if is_clip:
            self._api_request('clips.add', {
                'video_id': upload_data['video_id'],
                'owner_id': upload_data['owner_id']
            })
        
        return {
            'platform_job_id': f"{upload_data['owner_id']}_{upload_data['video_id']}",
            'public_url': f"https://vk.com/video{upload_data['owner_id']}_{upload_data['video_id']}"
        }
```

**Документация:** См. `VK_SETUP_GUIDE.md` для детальной настройки.

---

### 🟠 Одноклассники (OK)

**Приоритет:** Низкий  
**Статус:** 🔄 В планах  
**API:** OK REST API

#### Официальный способ:

**Требования:**
- OK приложение: https://ok.ru/devaccess
- Application Key и Application Secret Key
- Access Token пользователя или группы

**Шаги интеграции:**
1. Создать приложение на https://ok.ru/devaccess
2. Получить Application Key, Public Key, Secret Key
3. Реализовать OAuth
4. Подписывать запросы через MD5

**Endpoints:**
```
POST /fb.do
  ?method=video.add
  &application_key={app_key}
  &session_key={access_token}
  &sig={signature}
  
  → Возвращает upload_url и video_id

POST {upload_url}
  - Загрузка видео
```

**Лимиты:**
- Зависят от типа приложения
- Видео: до 4 ГБ
- Форматы: MP4, AVI, 3GP, MOV, WMV, FLV, MKV

**Особенности:**
- Требуется вычисление signature для каждого запроса:
  ```
  sig = md5(sorted_params + secret_key)
  ```

**План реализации:**
```python
# platforms/odnoklassniki.py

class OKPublisher:
    def __init__(self, application_key, secret_key, access_token):
        self.app_key = application_key
        self.secret_key = secret_key
        self.access_token = access_token
        
    def _sign_request(self, params):
        # Сортировать параметры и подписать
        sorted_params = ''.join(f"{k}={v}" for k, v in sorted(params.items()))
        return hashlib.md5((sorted_params + self.secret_key).encode()).hexdigest()
    
    def publish_video(self, video_path, title, description):
        # 1. Получить upload URL
        upload_data = self._get_upload_url(title, description)
        
        # 2. Загрузить видео
        self._upload_video(upload_data['upload_url'], video_path)
        
        return {
            'platform_job_id': upload_data['video_id'],
            'public_url': f"https://ok.ru/video/{upload_data['video_id']}"
        }
```

---

## 📋 Milestone 4: Медиа-платформы

### 📰 Яндекс.Дзен

**Приоритет:** Средний  
**Статус:** 🔄 В планах  
**API:** Yandex Zen Platform API

#### Официальный способ:

**Требования:**
- Канал в Дзене: https://dzen.ru/
- OAuth токен через Yandex OAuth
- Партнерская программа (для некоторых функций)

**Шаги интеграции:**
1. Создать канал на https://dzen.ru/
2. Подать заявку на API доступ
3. Получить OAuth Client ID
4. Реализовать OAuth flow
5. Использовать Zen API

**Endpoints:**
```
POST /api/v3/publications
  {
    "content": {
      "video": {
        "url": "{upload_url}"
      }
    },
    "title": "...",
    "text": "..."
  }
```

**Лимиты:**
- Зависят от статуса канала
- Видео: до 10 ГБ
- Длительность: до 4 часов
- Форматы: MP4, AVI, MOV, WebM

**Особенности:**
- Поддержка отложенной публикации
- Можно добавлять в нарративы
- Монетизация через Дзен

---

### 🐦 Twitter/X

**Приоритет:** Средний  
**Статус:** 🔄 В планах  
**API:** Twitter API v2

#### Официальный способ:

**Требования:**
- Twitter Developer аккаунт: https://developer.twitter.com/
- Elevated access (для видео)
- OAuth 1.0a или OAuth 2.0

**Шаги интеграции:**
1. Зарегистрироваться на https://developer.twitter.com/
2. Создать приложение
3. Получить API Key, API Secret, Access Token, Access Token Secret
4. Реализовать Chunked Upload
5. Создать твит с медиа

**Endpoints:**
```
POST /1.1/media/upload.json (INIT)
POST /1.1/media/upload.json (APPEND)
POST /1.1/media/upload.json (FINALIZE)
POST /2/tweets
```

**Лимиты:**
- До 50 твитов в день (может меняться)
- Видео: до 512 МБ (до 2 ГБ для некоторых аккаунтов)
- Длительность: до 2:20 (до 10 минут для верифицированных)
- Форматы: MP4 (H264 + AAC)
- Разрешение: минимум 32×32, максимум 1920×1200 (или 1200×1900)

**Особенности:**
- Chunked upload обязателен для видео
- Асинхронная обработка
- Нужно ждать завершения обработки перед созданием твита

---

### 📺 Facebook

**Приоритет:** Низкий  
**Статус:** 🔄 В планах  
**API:** Facebook Graph API

#### Официальный способ:

**Требования:**
- Facebook App
- Page Access Token или User Access Token
- Permissions: `pages_manage_posts`, `pages_read_engagement`

**Endpoints:**
```
POST /{page-id}/videos
  ?file_url={public_video_url}
  &description={description}
  &title={title}
```

**Лимиты:**
- До 75 постов в день на страницу
- Видео: до 10 ГБ
- Длительность: до 240 минут
- Форматы: MP4, MOV

---

## 🛠️ Общий план реализации

### Архитектура адаптеров

Каждый адаптер платформы должен реализовывать единый интерфейс:

```python
# platforms/base.py

from abc import ABC, abstractmethod
from typing import Dict, Optional

class BasePlatformPublisher(ABC):
    """Базовый класс для всех адаптеров платформ"""
    
    @abstractmethod
    def publish_video(
        self,
        video_path: str,
        title: str,
        description: Optional[str] = None,
        tags: Optional[list] = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        Публикация видео на платформу
        
        Returns:
            {
                'platform_job_id': str,  # ID видео на платформе
                'public_url': str,        # Публичная ссылка
                'status': str             # Статус публикации
            }
        """
        pass
    
    @abstractmethod
    def get_video_status(self, video_id: str) -> Dict:
        """Получить статус видео"""
        pass
    
    @abstractmethod
    def delete_video(self, video_id: str) -> bool:
        """Удалить видео (опционально)"""
        pass
```

### Фабрика адаптеров

```python
# platforms/factory.py

from platforms.youtube import YouTubePublisher
from platforms.instagram import InstagramPublisher
from platforms.tiktok import TikTokPublisher
# ... другие

class PlatformFactory:
    """Фабрика для создания адаптеров платформ"""
    
    @staticmethod
    def create_publisher(platform: str, credentials: dict):
        """Создать publisher для указанной платформы"""
        
        publishers = {
            'youtube': YouTubePublisher,
            'instagram': InstagramPublisher,
            'tiktok': TikTokPublisher,
            'vk': VKPublisher,
            'ok': OKPublisher,
            'dzen': DzenPublisher,
            'twitter': TwitterPublisher,
            'facebook': FacebookPublisher,
        }
        
        publisher_class = publishers.get(platform)
        if not publisher_class:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return publisher_class(**credentials)
```

### Обновление worker

```python
# workers/tasks_publish.py

from platforms.factory import PlatformFactory

@celery_app.task(base=PublishTask, bind=True, max_retries=3)
def publish_submission(self, submission_id: str):
    # ... existing code ...
    
    # Получаем credentials для платформы
    credentials = get_platform_credentials(job.platform)
    
    # Создаем publisher
    publisher = PlatformFactory.create_publisher(
        platform=job.platform,
        credentials=credentials
    )
    
    # Публикуем
    result = publisher.publish_video(
        video_path=temp_file_path,
        title=job.title,
        description=job.description,
        tags=job.tags
    )
    
    # ... update job ...
```

---

## 📊 Матрица сравнения платформ

| Платформа | Приоритет | Сложность | API Качество | Лимиты | OAuth | Примечания |
|-----------|-----------|-----------|--------------|--------|-------|------------|
| YouTube | ✅ Готово | Средняя | Отличное | 10k units/day | Да | Стабильный, документирован |
| VK | ✅ Готово | Средняя | Хорошее | До 5 ГБ/видео | Да | Создание через VK ID с 2024 |
| Instagram | Высокий | Высокая | Хорошее | 25 постов/день | Да | Требует Business аккаунт |
| TikTok | Высокий | Высокая | Хорошее | ~5-10/день | Да | Требует ревью приложения |
| OK | Низкий | Средняя | Среднее | Зависит | Да | Требует подписи запросов |
| Дзен | Средний | Средняя | Среднее | Зависит | Да | Требует заявку на API |
| Twitter/X | Средний | Высокая | Хорошее | 50 твитов/день | Да | Chunked upload |
| Facebook | Низкий | Средняя | Хорошее | 75 постов/день | Да | Похож на Instagram |

---

## 🚀 Следующие шаги

1. **Milestone 2:**
   - [ ] Реализовать Instagram адаптер
   - [ ] Реализовать TikTok адаптер
   - [ ] Добавить мультиплатформенную публикацию (одно видео → все платформы)
   - [ ] Тесты для новых адаптеров

2. **Milestone 3:**
   - [x] VK адаптер ✅ **ГОТОВО**
   - [ ] OK адаптер
   - [ ] Stories для VK
   - [ ] VK клипы (вертикальные видео)

3. **Milestone 4:**
   - [ ] Дзен адаптер
   - [ ] Twitter адаптер
   - [ ] Facebook адаптер

4. **Улучшения:**
   - [ ] UI для управления публикациями (веб-интерфейс)
   - [ ] Планировщик публикаций (отложенные посты)
   - [ ] Аналитика (просмотры, лайки, комментарии)
   - [ ] Автоматическая адаптация видео под требования платформ
   - [ ] A/B тестирование заголовков и описаний

---

**Обновлено:** 2025-10-16 (добавлен VK адаптер ✅)


