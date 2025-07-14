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

def get_task_priority_keyboard():
    """Клавиатура для выбора приоритета задачи"""
    buttons = [
        [KeyboardButton(text="🔴 Срочная"), KeyboardButton(text="🟡 Обычная")],
        [KeyboardButton(text="🟢 Не очень срочная"), KeyboardButton(text="❌ Отмена")]
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