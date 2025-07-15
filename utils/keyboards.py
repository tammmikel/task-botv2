from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard(role):
    """Главная клавиатура в зависимости от роли пользователя"""
    
    if role == 'director':
        buttons = [
            [KeyboardButton(text="📋 Создать задачу"), KeyboardButton(text="🏢 Управление компаниями")],
            [KeyboardButton(text="👥 Управление сотрудниками"), KeyboardButton(text="📊 Аналитика")],
            [KeyboardButton(text="📝 Мои задачи")]
        ]
    
    elif role == 'manager':
        buttons = [
            [KeyboardButton(text="📋 Создать задачу"), KeyboardButton(text="🏢 Управление компаниями")],
            [KeyboardButton(text="📝 Мои задачи")]
        ]
    
    else:  # admin
        buttons = [
            [KeyboardButton(text="📝 Мои задачи")]
        ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_company_management_keyboard():
    """Клавиатура для управления компаниями"""
    buttons = [
        [KeyboardButton(text="➕ Добавить компанию"), KeyboardButton(text="📋 Список компаний")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_staff_management_keyboard():
    """Клавиатура для управления сотрудниками (только для директора)"""
    buttons = [
        [KeyboardButton(text="👤 Изменить роль сотрудника"), KeyboardButton(text="📋 Список сотрудников")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_task_urgent_keyboard():
    """Клавиатура для выбора срочности задачи"""
    buttons = [
        [KeyboardButton(text="🔥 Срочная"), KeyboardButton(text="📝 Обычная")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_task_deadline_keyboard():
    """Клавиатура для выбора дедлайна задачи"""
    buttons = [
        [KeyboardButton(text="📅 Сегодня"), KeyboardButton(text="📅 Завтра")],
        [KeyboardButton(text="📅 Через 3 дня"), KeyboardButton(text="📅 Выбрать дату")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_back_keyboard():
    """Простая клавиатура с кнопкой назад"""
    buttons = [
        [KeyboardButton(text="🔙 Назад")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_skip_keyboard():
    """Клавиатура с кнопками 'Пропустить' и 'Назад'"""
    buttons = [
        [KeyboardButton(text="⏭️ Пропустить")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )


async def clear_previous_messages(bot, chat_id, count=10):
    """
    Удаляет предыдущие сообщения бота
    bot: экземпляр бота
    chat_id: ID чата  
    count: количество сообщений для проверки
    """
    try:
        # Отправляем временное сообщение для получения текущего message_id
        temp_msg = await bot.send_message(chat_id, ".")
        current_msg_id = temp_msg.message_id
        
        # Удаляем временное сообщение
        await bot.delete_message(chat_id, current_msg_id)
        
        # Проверяем предыдущие сообщения и удаляем
        for msg_id in range(current_msg_id - 1, max(0, current_msg_id - count), -1):
            try:
                await bot.delete_message(chat_id, msg_id)
            except:
                continue
                
    except Exception as e:
        print(f"Ошибка очистки сообщений: {e}")