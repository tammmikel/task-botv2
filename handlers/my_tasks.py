from aiogram import Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import F
from database.models import UserManager, TaskManager, FileManager
from utils.keyboards import get_main_keyboard
from utils.file_storage import file_storage
from datetime import datetime

async def my_tasks_handler(message: Message):
    """Обработчик кнопки 'Мои задачи'"""
    try:
        print("=== Вызван my_tasks_handler ===")
        telegram_id = message.from_user.id
        
        # Получаем пользователя
        user = UserManager.get_user_by_telegram_id(telegram_id)
        if not user:
            await message.answer("Пользователь не найден.")
            return
        
        # Получаем задачи пользователя
        tasks = TaskManager.get_user_tasks(user['user_id'], user['role'])
        
        if not tasks:
            await message.answer(
                "📝 У вас пока нет задач",
                reply_markup=get_main_keyboard(user['role'])
            )
            return
        
        # Формируем кнопки управления
        control_buttons = [
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_tasks"),
             InlineKeyboardButton(text="🏢 Фильтр по компаниям", callback_data="filter_companies")]
        ]
        
        # Формируем кнопки с задачами
        task_buttons = []
        for task in tasks[:15]:  # Показываем первые 15 задач
            # Формируем текст кнопки
            urgent_emoji = "🔥" if task.get('is_urgent', False) else ""
            status_names = {
                'new': 'Новая',
                'in_progress': 'В процессе', 
                'completed': 'Выполнена',
                'overdue': 'Просрочена',
                'cancelled': 'Отменена'
            }
            
            status_name = status_names.get(task['status'], task['status'])
            button_text = f"{task['status_emoji']}{urgent_emoji} {status_name} | {task['title'][:25]}... | {task['company_name']} | {task.get('deadline_short', '')}"
            
            task_buttons.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"task_{task['task_id']}"
            )])
        
        # Объединяем все кнопки
        keyboard = control_buttons + task_buttons
        
        tasks_text = f"📝 Ваши задачи ({len(tasks)}):"
        if len(tasks) > 15:
            tasks_text += f"\n\nПоказано первые 15 из {len(tasks)} задач"
        
        # Отправляем список
        await message.answer(
            tasks_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        print(f"Ошибка в my_tasks_handler: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

async def process_task_callback(callback: CallbackQuery):
    """Обработчик нажатий на задачи"""
    try:
        data = callback.data
        
        if data.startswith("task_"):
            task_id = data.replace("task_", "")
            
            # Получаем детали задачи
            task = TaskManager.get_task_by_id(task_id)
            if not task:
                await callback.answer("Задача не найдена")
                return
            
            # Получаем файлы задачи
            files = FileManager.get_task_files(task_id)
            
            # Формируем детальное описание
            detail_text = f"📋 {task['title']}\n\n"
            detail_text += f"📝 Описание: {task['description']}\n"
            detail_text += f"🏢 Компания: {task['company_name']}\n"
            if task.get('is_urgent', False):
                detail_text += f"⚡ Приоритет: 🔥 Срочная\n"
            detail_text += f"📊 Статус: {task['status']}\n"
            detail_text += f"📅 Дедлайн: {task['deadline_str']}\n"
            detail_text += f"📞 Инициатор: {task['initiator_name']}\n"
            
            if files:
                detail_text += f"\n📎 Файлы ({len(files)}):\n"
                for file in files:
                    detail_text += f"• {file['file_name']}\n"
            
            await callback.message.edit_text(
                detail_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="back_to_tasks")]
                ])
            )
            
        elif data == "filter_companies":
            # Показываем фильтр по компаниям
            telegram_id = callback.from_user.id
            user = UserManager.get_user_by_telegram_id(telegram_id)
            companies = TaskManager.get_companies_with_tasks(user['user_id'], user['role'])
            
            keyboard = []
            for company in companies:
                keyboard.append([InlineKeyboardButton(
                    text=f"{company['name']} ({company['task_count']})",
                    callback_data=f"company_{company['company_id']}"
                )])
            
            keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_tasks")])
            
            await callback.message.edit_text(
                "🏢 Выберите компанию для фильтрации:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
            
        elif data == "back_to_tasks":
            # Возвращаемся к списку задач
            telegram_id = callback.from_user.id
            user = UserManager.get_user_by_telegram_id(telegram_id)
            tasks = TaskManager.get_user_tasks(user['user_id'], user['role'])
            
            if not tasks:
                await callback.message.edit_text("📝 У вас пока нет задач")
                return
            
            # Формируем кнопки как в основном обработчике
            control_buttons = [
                [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_tasks"),
                 InlineKeyboardButton(text="🏢 Фильтр по компаниям", callback_data="filter_companies")]
            ]
            
            task_buttons = []
            for task in tasks[:15]:
                urgent_emoji = "🔥" if task.get('is_urgent', False) else ""
                status_names = {
                    'new': 'Новая',
                    'in_progress': 'В процессе', 
                    'completed': 'Выполнена',
                    'overdue': 'Просрочена',
                    'cancelled': 'Отменена'
                }
                
                status_name = status_names.get(task['status'], task['status'])
                button_text = f"{task['status_emoji']}{urgent_emoji} {status_name} | {task['title'][:25]}... | {task['company_name']} | {task.get('deadline_short', '')}"
                
                task_buttons.append([InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"task_{task['task_id']}"
                )])
            
            keyboard = control_buttons + task_buttons
            
            tasks_text = f"📝 Ваши задачи ({len(tasks)}):"
            if len(tasks) > 15:
                tasks_text += f"\n\nПоказано первые 15 из {len(tasks)} задач"
            
            await callback.message.edit_text(
                tasks_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )

        elif data == "refresh_tasks":
            # Получаем обновленный список задач
            telegram_id = callback.from_user.id
            user = UserManager.get_user_by_telegram_id(telegram_id)
            tasks = TaskManager.get_user_tasks(user['user_id'], user['role'])
            
            if not tasks:
                await callback.message.edit_text("📝 У вас пока нет задач")
                await callback.answer("Список обновлен")
                return
            
            # Формируем новые кнопки
            control_buttons = [
                [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_tasks"),
                 InlineKeyboardButton(text="🏢 Фильтр по компаниям", callback_data="filter_companies")]
            ]
            
            task_buttons = []
            for task in tasks[:15]:
                urgent_emoji = "🔥" if task.get('is_urgent', False) else ""
                status_names = {
                    'new': 'Новая',
                    'in_progress': 'В процессе', 
                    'completed': 'Выполнена',
                    'overdue': 'Просрочена',
                    'cancelled': 'Отменена'
                }
                
                status_name = status_names.get(task['status'], task['status'])
                button_text = f"{task['status_emoji']}{urgent_emoji} {status_name} | {task['title'][:25]}... | {task['company_name']} | {task.get('deadline_short', '')}"
                
                task_buttons.append([InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"task_{task['task_id']}"
                )])
            
            keyboard = control_buttons + task_buttons
            
            # Добавляем временную метку
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            tasks_text = f"📝 Ваши задачи ({len(tasks)}) - обновлено {current_time}"
            if len(tasks) > 15:
                tasks_text += f"\n\nПоказано первые 15 из {len(tasks)} задач"
            
            await callback.message.edit_text(
                tasks_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
            
            await callback.answer("✅ Список обновлен")
        await callback.answer()
    except Exception as e:
        print(f"Ошибка в process_task_callback: {e}")
        await callback.answer("Произошла ошибка")

def register_my_tasks_handlers(dp: Dispatcher):
    """Регистрация обработчиков просмотра задач"""
    dp.message.register(my_tasks_handler, F.text == "📝 Мои задачи")
    dp.callback_query.register(process_task_callback, F.data.startswith("task_"))
    dp.callback_query.register(process_task_callback, F.data == "filter_companies")
    dp.callback_query.register(process_task_callback, F.data == "back_to_tasks")
    dp.callback_query.register(process_task_callback, F.data.startswith("company_"))
    dp.callback_query.register(process_task_callback, F.data == "refresh_tasks")