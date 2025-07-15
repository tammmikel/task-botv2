from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from database.models import UserManager
from utils.keyboards import get_main_keyboard


async def start_command(message: Message):
    """Обработчик команды /start"""
    try:
        print("=== Вызван start_command ===")
        telegram_id = message.from_user.id

        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        
        print(f"Данные пользователя: ID={telegram_id}, username={username}, name={first_name} {last_name}")
        
        # Проверяем, существует ли пользователь
        print("Проверяем существование пользователя...")
        existing_user = UserManager.get_user_by_telegram_id(telegram_id)
        print(f"Результат поиска пользователя: {existing_user}")
        
        if existing_user:
            # Пользователь уже существует
            role = existing_user['role']
            print(f"Пользователь найден с ролью: {role}")
            
            if role == 'director':
                role_text = "Директор"
            elif role == 'manager':
                role_text = "Менеджер"
            else:
                role_text = "Системный администратор"
            
            response_text = f"Добро пожаловать обратно!\nВаша роль: {role_text}"
            print(f"Отправляем ответ: {response_text}")
            
            await message.answer(
                response_text,
                reply_markup=get_main_keyboard(role)
            )
        else:
            print("Пользователь не найден, создаем нового...")
            # Создаем нового пользователя
            users_count = UserManager.get_users_count()
            print(f"Общее количество пользователей: {users_count}")
            
            # Первый пользователь становится директором
            if users_count == 0:
                role = 'director'
                role_text = "Директор"
                welcome_text = (
                    f"Добро пожаловать в систему управления задачами!\n\n"
                    f"Вы первый пользователь и получили роль: {role_text}\n\n"
                    f"Вы можете:\n"
                    f"• Создавать компании\n"
                    f"• Ставить задачи\n"
                    f"• Управлять ролями сотрудников\n"
                    f"• Просматривать аналитику"
                )
            else:
                role = 'admin'
                role_text = "Системный администратор"
                welcome_text = (
                    f"Добро пожаловать в систему управления задачами!\n\n"
                    f"Ваша роль: {role_text}\n\n"
                    f"Вы можете:\n"
                    f"• Просматривать свои задачи\n"
                    f"• Изменять статус задач\n"
                    f"• Добавлять комментарии к задачам"
                )
            
            print(f"Назначенная роль: {role}")
            
            # Создаем пользователя в базе
            print("Создаем пользователя в базе данных...")
            user_id = UserManager.create_user(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            print(f"Результат создания пользователя: {user_id}")
            
            if user_id:
                print(f"Отправляем приветственное сообщение: {welcome_text}")
                await message.answer(
                    welcome_text,
                    reply_markup=get_main_keyboard(role)
                )
            else:
                print("Ошибка создания пользователя, отправляем сообщение об ошибке")
                await message.answer(
                    "Произошла ошибка при регистрации. Попробуйте позже."
                )
        
        print("=== start_command завершен ===")
                
    except Exception as e:
        print(f"Ошибка в start_command: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        await message.answer(
            "Произошла ошибка. Попробуйте позже."
        )

def register_start_handlers(dp: Dispatcher):
    """Регистрация обработчиков команды start"""
    dp.message.register(start_command, Command("start"))