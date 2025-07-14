import os
import json
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
from database.connection import db_connection
from database.models import DatabaseManager
from handlers.start import register_start_handlers
from handlers.companies import register_company_handlers
from handlers.tasks import register_task_handlers

# Получение токена бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Создание экземпляров бота и диспетчера с хранилищем состояний
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

def init_database():
    """Инициализация базы данных"""
    try:
        # Подключение к базе
        if not db_connection.connect():
            raise Exception("Не удалось подключиться к базе данных")
        
        # DatabaseManager.create_tables() - закомментировано, таблицы созданы вручную
        print("База данных инициализирована успешно")
        
    except Exception as e:
        print(f"Ошибка инициализации базы данных: {e}")
        raise e

def register_handlers():
    """Регистрация всех обработчиков"""
    register_start_handlers(dp)
    register_company_handlers(dp)
    register_task_handlers(dp)

async def process_update(event, context):
    """Основная функция для обработки обновлений от Telegram"""
    try:
        print("=== Начало обработки обновления ===")
        
        # Инициализация базы данных при первом запуске
        init_database()
        
        # Регистрация обработчиков
        register_handlers()
        print("Обработчики зарегистрированы")
        
        # Парсинг входящего обновления
        update_data = json.loads(event['body'])
        print(f"Получены данные обновления: {update_data}")
        
        update = Update.model_validate(update_data, context={'bot': bot})
        print(f"Update создан, есть message: {update.message is not None}")
        
        # Асинхронная обработка обновления через aiogram
        await dp.feed_update(bot, update)
        
        print("=== Обработка завершена успешно ===")
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'ok'})
        }
        
    except Exception as e:
        print(f"Ошибка обработки обновления: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# Асинхронная точка входа для Yandex Functions
async def handler(event, context):
    """Входная точка для Yandex Cloud Functions"""
    return await process_update(event, context)