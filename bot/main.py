"""Главный модуль Telegram бота"""
import asyncio
import hashlib
import structlog
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from minio import Minio
import httpx
from datetime import datetime

from bot.config import config

# Настройка логирования
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Состояния разговора
WAITING_FOR_DESCRIPTION = 1

# Инициализация MinIO клиента
minio_client = Minio(
    config.MINIO_ENDPOINT,
    access_key=config.MINIO_ACCESS_KEY,
    secret_key=config.MINIO_SECRET_KEY,
    secure=config.MINIO_SECURE
)

# Проверка и создание bucket
try:
    if not minio_client.bucket_exists(config.MINIO_BUCKET):
        minio_client.make_bucket(config.MINIO_BUCKET)
        logger.info("Created MinIO bucket", bucket=config.MINIO_BUCKET)
except Exception as e:
    logger.error("Error checking/creating MinIO bucket", error=str(e))


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info("User started bot", user_id=user.id, username=user.username)
    
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        "Я помогу тебе автоматически публиковать короткие видео на YouTube Shorts "
        "и другие платформы.\n\n"
        "📹 Просто отправь мне видео (до 2 ГБ), и я опубликую его!\n\n"
        "Доступные команды:\n"
        "/start - Начать работу\n"
        "/help - Помощь\n"
        "/cancel - Отменить текущую операцию"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "🤖 *Как пользоваться ботом:*\n\n"
        "1️⃣ Отправь мне видео (файлом или как видеосообщение)\n"
        "2️⃣ Я попрошу тебя написать описание\n"
        "3️⃣ Подтверди публикацию\n"
        "4️⃣ Я загружу видео и опубликую на YouTube Shorts\n\n"
        "💡 *Требования к видео:*\n"
        "• Вертикальный формат 9:16 (1080×1920)\n"
        "• Размер до 2 ГБ\n"
        "• Длительность до 60 секунд для Shorts\n\n"
        "❓ *Поддержка:* напиши /start чтобы начать заново",
        parse_mode="Markdown"
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /cancel"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Операция отменена. Отправь /start для начала."
    )
    return ConversationHandler.END


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик получения видео"""
    user = update.effective_user
    message = update.message
    
    # Определяем тип видео
    video = None
    if message.video:
        video = message.video
        video_type = "video"
    elif message.video_note:
        video = message.video_note
        video_type = "video_note"
    elif message.document and message.document.mime_type and message.document.mime_type.startswith("video/"):
        video = message.document
        video_type = "document"
    else:
        await message.reply_text("❌ Пожалуйста, отправь видеофайл.")
        return ConversationHandler.END
    
    logger.info(
        "Received video",
        user_id=user.id,
        video_type=video_type,
        file_size=video.file_size,
        file_id=video.file_id
    )
    
    # Проверка размера файла (2 ГБ)
    if video.file_size > 2 * 1024 * 1024 * 1024:
        await message.reply_text(
            "❌ Видео слишком большое! Максимальный размер: 2 ГБ"
        )
        return ConversationHandler.END
    
    await message.reply_text("⏳ Загружаю видео...")
    
    try:
        # Скачиваем файл через локальный Bot API
        file = await context.bot.get_file(video.file_id)
        file_path = file.file_path
        
        # Загружаем файл
        file_bytes = await file.download_as_bytearray()
        
        # Вычисляем хеш
        video_hash = hashlib.sha256(file_bytes).hexdigest()
        
        # Генерируем S3 ключ
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        s3_key = f"videos/{user.id}/{timestamp}_{video_hash[:16]}.mp4"
        
        # Загружаем в MinIO
        from io import BytesIO
        minio_client.put_object(
            config.MINIO_BUCKET,
            s3_key,
            BytesIO(file_bytes),
            length=len(file_bytes),
            content_type="video/mp4"
        )
        
        logger.info(
            "Video uploaded to MinIO",
            user_id=user.id,
            s3_key=s3_key,
            video_hash=video_hash
        )
        
        # Сохраняем данные в контексте
        context.user_data['video_data'] = {
            'file_id': video.file_id,
            'file_size': video.file_size,
            'video_hash': video_hash,
            's3_key': s3_key,
            'duration': getattr(video, 'duration', None),
            'telegram_message_id': str(message.message_id)
        }
        
        await message.reply_text(
            "✅ Видео загружено!\n\n"
            "📝 Теперь напиши *название и описание* для видео.\n"
            "Например:\n\n"
            "*Мой крутой видос*\n"
            "Это описание моего видео для YouTube Shorts #shorts #видео",
            parse_mode="Markdown"
        )
        
        return WAITING_FOR_DESCRIPTION
        
    except Exception as e:
        logger.error(
            "Error processing video",
            user_id=user.id,
            error=str(e),
            error_type=type(e).__name__
        )
        await message.reply_text(
            f"❌ Ошибка при обработке видео: {str(e)}\n\n"
            "Попробуй еще раз или обратись к администратору."
        )
        return ConversationHandler.END


async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик получения описания"""
    user = update.effective_user
    message = update.message
    description_text = message.text.strip()
    
    if not description_text:
        await message.reply_text("❌ Описание не может быть пустым. Попробуй еще раз.")
        return WAITING_FOR_DESCRIPTION
    
    # Разбиваем на заголовок и описание
    lines = description_text.split('\n', 1)
    title = lines[0].strip()
    description = lines[1].strip() if len(lines) > 1 else title
    
    video_data = context.user_data.get('video_data')
    if not video_data:
        await message.reply_text("❌ Ошибка: видео не найдено. Начни заново с /start")
        return ConversationHandler.END
    
    logger.info(
        "Received description",
        user_id=user.id,
        title=title
    )
    
    await message.reply_text("📤 Отправляю видео на публикацию...")
    
    try:
        # Отправляем в API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{config.API_BASE_URL}/ingest",
                json={
                    "video_hash": video_data['video_hash'],
                    "s3_key": video_data['s3_key'],
                    "file_size": video_data['file_size'],
                    "duration": video_data.get('duration'),
                    "platform": "youtube",
                    "title": title,
                    "description": description,
                    "tags": ["shorts"],
                    "telegram_user_id": str(user.id),
                    "telegram_message_id": video_data['telegram_message_id']
                },
                headers={
                    "X-Service-Token": config.SERVICE_TOKEN,
                    "Content-Type": "application/json"
                }
            )
        
        if response.status_code == 200:
            data = response.json()
            
            # Проверка на null (для отладки)
            if data is None:
                logger.error("API returned 200 but null body", user_id=user.id)
                await message.reply_text(
                    "⚠️ Получен некорректный ответ от сервера (200 но null). "
                    "Обратись к администратору."
                )
                return ConversationHandler.END
            
            submission_id = data.get('submission_id')
            
            logger.info(
                "Video submitted successfully",
                user_id=user.id,
                submission_id=submission_id
            )
            
            await message.reply_text(
                f"✅ *Видео принято на публикацию!*\n\n"
                f"🆔 ID заявки: `{submission_id}`\n"
                f"📺 Платформа: YouTube Shorts\n"
                f"📋 Заголовок: {title}\n\n"
                f"⏳ Публикация займет несколько минут.\n"
                f"Я уведомлю тебя, когда видео будет опубликовано!",
                parse_mode="Markdown"
            )
            
            # Планируем проверку статуса
            context.job_queue.run_once(
                check_status_callback,
                when=30,
                data={
                    'submission_id': submission_id,
                    'chat_id': message.chat_id,
                    'user_id': user.id
                }
            )
            
        else:
            logger.error(
                "API error",
                user_id=user.id,
                status_code=response.status_code,
                response=response.text
            )
            await message.reply_text(
                f"❌ Ошибка API ({response.status_code}):\n{response.text}\n\n"
                "Попробуй позже или обратись к администратору."
            )
    
    except Exception as e:
        logger.error(
            "Error submitting video",
            user_id=user.id,
            error=str(e),
            error_type=type(e).__name__
        )
        await message.reply_text(
            f"❌ Ошибка при отправке видео: {str(e)}\n\n"
            "Попробуй еще раз или обратись к администратору."
        )
    
    # Очищаем данные пользователя
    context.user_data.clear()
    return ConversationHandler.END


async def check_status_callback(context: ContextTypes.DEFAULT_TYPE):
    """Callback для проверки статуса публикации"""
    job_data = context.job.data
    submission_id = job_data['submission_id']
    chat_id = job_data['chat_id']
    user_id = job_data['user_id']
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{config.API_BASE_URL}/status/{submission_id}",
                headers={"X-Service-Token": config.SERVICE_TOKEN}
            )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            
            logger.info(
                "Status check",
                user_id=user_id,
                submission_id=submission_id,
                status=status
            )
            
            if status == "COMPLETED":
                public_url = data.get('public_url', 'N/A')
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🎉 *Видео успешно опубликовано!*\n\n"
                         f"🆔 ID: `{submission_id}`\n"
                         f"🔗 Ссылка: {public_url}\n\n"
                         f"Поздравляю! 🚀",
                    parse_mode="Markdown"
                )
            elif status == "FAILED":
                error_msg = data.get('error_message', 'Unknown error')
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ *Ошибка при публикации*\n\n"
                         f"🆔 ID: `{submission_id}`\n"
                         f"⚠️ Ошибка: {error_msg}\n\n"
                         f"Попробуй еще раз или обратись к администратору.",
                    parse_mode="Markdown"
                )
            else:
                # Ещё обрабатывается, проверим позже
                context.job_queue.run_once(
                    check_status_callback,
                    when=30,
                    data=job_data
                )
    
    except Exception as e:
        logger.error(
            "Error checking status",
            user_id=user_id,
            submission_id=submission_id,
            error=str(e)
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error("Exception while handling an update", exc_info=context.error)
    
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Произошла непредвиденная ошибка. Попробуй еще раз или обратись к администратору."
        )


def main():
    """Запуск бота"""
    logger.info("Starting Telegram bot")
    
    # Создание приложения
    app_builder = Application.builder().token(config.BOT_TOKEN)
    
    # Используем локальный Bot API если указан
    if config.LOCAL_API_URL:
        app_builder = (
            app_builder
            .base_url(f"{config.LOCAL_API_URL}/bot")
            .base_file_url(f"{config.LOCAL_API_URL}/file/bot")
        )
    
    application = app_builder.build()
    
    # Conversation handler для работы с видео
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.VIDEO | filters.VIDEO_NOTE | filters.Document.VIDEO,
                handle_video
            )
        ],
        states={
            WAITING_FOR_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)]
    )
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    # Запуск бота
    logger.info("Bot started successfully")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


