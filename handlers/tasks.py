from aiogram import Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
from aiogram.fsm.context import FSMContext
from database.models import UserManager, CompanyManager, TaskManager
from utils.keyboards import get_main_keyboard, get_back_keyboard, get_task_priority_keyboard, get_task_deadline_keyboard
from utils.states import TaskStates
from datetime import datetime, timedelta

async def create_task_handler(message: Message, state: FSMContext):
    """Обработчик кнопки 'Создать задачу'"""
    try:
        print("=== Вызван create_task_handler ===")
        telegram_id = message.from_user.id
        
        # Проверяем права пользователя
        user = UserManager.get_user_by_telegram_id(telegram_id)
        if not user or user['role'] not in ['director', 'manager']:
            await message.answer(
                "У вас нет прав для создания задач.",
                reply_markup=get_main_keyboard(user['role'] if user else 'admin')
            )
            return
        
        # Сохраняем данные пользователя в состоянии
        await state.update_data(created_by=user['user_id'])
        
        # Переходим в состояние ожидания названия
        await state.set_state(TaskStates.waiting_for_title)
        
        await message.answer(
            "📋 Создание новой задачи\n\n"
            "Шаг 1/5: Введите название задачи:",
            reply_markup=get_back_keyboard()
        )
        
    except Exception as e:
        print(f"Ошибка в create_task_handler: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

async def process_task_title(message: Message, state: FSMContext):
    """Обработчик ввода названия задачи"""
    try:
        print("=== Вызван process_task_title ===")
        
        # Проверяем корректность названия
        task_title = message.text.strip()
        if len(task_title) < 3:
            await message.answer(
                "❌ Название задачи слишком короткое!\n\n"
                "Введите название задачи (минимум 3 символа):",
                reply_markup=get_back_keyboard()
            )
            return
        
        if len(task_title) > 200:
            await message.answer(
                "❌ Название задачи слишком длинное!\n\n"
                "Введите название задачи (максимум 200 символов):",
                reply_markup=get_back_keyboard()
            )
            return
        
        # Сохраняем название
        await state.update_data(task_title=task_title)
        
        # Переходим к описанию
        await state.set_state(TaskStates.waiting_for_description)
        
        await message.answer(
            f"✅ Название: {task_title}\n\n"
            f"Шаг 2/5: Введите описание задачи:",
            reply_markup=get_back_keyboard()
        )
        
    except Exception as e:
        print(f"Ошибка в process_task_title: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

async def process_task_description(message: Message, state: FSMContext):
    """Обработчик ввода описания задачи"""
    try:
        print("=== Вызван process_task_description ===")
        
        task_description = message.text.strip()
        if len(task_description) > 1000:
            await message.answer(
                "❌ Описание задачи слишком длинное!\n\n"
                "Введите описание задачи (максимум 1000 символов):",
                reply_markup=get_back_keyboard()
            )
            return
        
        # Сохраняем описание
        await state.update_data(task_description=task_description)
        
        # Получаем список компаний для выбора
        companies = CompanyManager.get_all_companies()
        
        if not companies:
            await message.answer(
                "❌ В системе нет ни одной компании!\n\n"
                "Сначала создайте компанию через меню 'Управление компаниями'.",
                reply_markup=get_back_keyboard()
            )
            await state.clear()
            return
        
        # Создаем клавиатуру с компаниями
        company_keyboard = create_company_keyboard(companies)
        
        # Переходим к выбору компании
        await state.set_state(TaskStates.waiting_for_company)
        
        company_list = "Доступные компании:\n"
        for i, company in enumerate(companies, 1):
            company_list += f"{i}. {company['name']}\n"
        
        await message.answer(
            f"✅ Описание сохранено\n\n"
            f"Шаг 3/5: Выберите компанию для задачи:\n\n"
            f"{company_list}",
            reply_markup=company_keyboard
        )
        
    except Exception as e:
        print(f"Ошибка в process_task_description: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

async def process_company_selection(message: Message, state: FSMContext):
    """Обработчик выбора компании"""
    try:
        print("=== Вызван process_company_selection ===")
        
        # Получаем список компаний
        companies = CompanyManager.get_all_companies()
        selected_company = None
        
        # Ищем выбранную компанию
        for company in companies:
            if company['name'] == message.text:
                selected_company = company
                break
        
        if not selected_company:
            await message.answer(
                "❌ Компания не найдена! Выберите компанию из списка:",
                reply_markup=create_company_keyboard(companies)
            )
            return
        
        # Сохраняем выбранную компанию
        await state.update_data(
            company_id=selected_company['company_id'],
            company_name=selected_company['name']
        )
        
        # Переходим к вводу инициатора
        await state.set_state(TaskStates.waiting_for_initiator_name)
        
        await message.answer(
            f"✅ Компания: {selected_company['name']}\n\n"
            f"Шаг 4/5: Введите имя инициатора задачи:",
            reply_markup=get_back_keyboard()
        )
        
    except Exception as e:
        print(f"Ошибка в process_company_selection: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

async def process_initiator_name(message: Message, state: FSMContext):
    """Обработчик ввода имени инициатора"""
    try:
        print("=== Вызван process_initiator_name ===")
        
        initiator_name = message.text.strip()
        if len(initiator_name) < 2:
            await message.answer(
                "❌ Имя инициатора слишком короткое!\n\n"
                "Введите имя инициатора (минимум 2 символа):",
                reply_markup=get_back_keyboard()
            )
            return
        
        if len(initiator_name) > 100:
            await message.answer(
                "❌ Имя инициатора слишком длинное!\n\n"
                "Введите имя инициатора (максимум 100 символов):",
                reply_markup=get_back_keyboard()
            )
            return
        
        # Сохраняем имя инициатора
        await state.update_data(initiator_name=initiator_name)
        
        # Переходим к вводу телефона
        await state.set_state(TaskStates.waiting_for_initiator_phone)
        
        await message.answer(
            f"✅ Инициатор: {initiator_name}\n\n"
            f"Введите номер телефона инициатора:",
            reply_markup=get_back_keyboard()
        )
        
    except Exception as e:
        print(f"Ошибка в process_initiator_name: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

async def process_initiator_phone(message: Message, state: FSMContext):
    """Обработчик ввода телефона инициатора"""
    try:
        print("=== Вызван process_initiator_phone ===")
        
        phone = message.text.strip()
        
        # Простая валидация телефона
        if len(phone) < 10:
            await message.answer(
                "❌ Номер телефона слишком короткий!\n\n"
                "Введите корректный номер телефона:",
                reply_markup=get_back_keyboard()
            )
            return
        
        if len(phone) > 20:
            await message.answer(
                "❌ Номер телефона слишком длинный!\n\n"
                "Введите корректный номер телефона:",
                reply_markup=get_back_keyboard()
            )
            return
        
        # Сохраняем телефон
        await state.update_data(initiator_phone=phone)
        
        # Получаем список исполнителей (админы и главный админ)
        assignees = UserManager.get_assignees()
        
        if not assignees:
            await message.answer(
                "❌ В системе нет доступных исполнителей!\n\n"
                "Обратитесь к администратору.",
                reply_markup=get_back_keyboard()
            )
            await state.clear()
            return
        
        # Создаем клавиатуру с исполнителями
        assignee_keyboard = create_assignee_keyboard(assignees)
        
        # Переходим к выбору исполнителя
        await state.set_state(TaskStates.waiting_for_assignee)
        
        assignee_list = "Доступные исполнители:\n"
        for i, assignee in enumerate(assignees, 1):
            name = f"{assignee['first_name'] or ''} {assignee['last_name'] or ''}".strip()
            if not name:
                name = assignee['username'] or f"ID: {assignee['telegram_id']}"
            assignee_list += f"{i}. {name}\n"
        
        await message.answer(
            f"✅ Телефон: {phone}\n\n"
            f"Шаг 5/5: Выберите исполнителя задачи:\n\n"
            f"{assignee_list}",
            reply_markup=assignee_keyboard
        )
        
    except Exception as e:
        print(f"Ошибка в process_initiator_phone: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

def create_company_keyboard(companies):
    """Создает клавиатуру с компаниями"""
    buttons = []
    for company in companies:
        buttons.append([KeyboardButton(text=company['name'])])
    buttons.append([KeyboardButton(text="🔙 Назад")])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def create_assignee_keyboard(assignees):
    """Создает клавиатуру с исполнителями"""
    buttons = []
    for assignee in assignees:
        name = f"{assignee['first_name'] or ''} {assignee['last_name'] or ''}".strip()
        if not name:
            name = assignee['username'] or f"ID: {assignee['telegram_id']}"
        buttons.append([KeyboardButton(text=name)])
    buttons.append([KeyboardButton(text="🔙 Назад")])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def register_task_handlers(dp: Dispatcher):
    """Регистрация обработчиков для управления задачами"""
    # Основные обработчики
    dp.message.register(create_task_handler, F.text == "📋 Создать задачу")
    
    # Обработчики состояний FSM
    dp.message.register(process_task_title, TaskStates.waiting_for_title)
    dp.message.register(process_task_description, TaskStates.waiting_for_description)
    dp.message.register(process_company_selection, TaskStates.waiting_for_company)
    dp.message.register(process_initiator_name, TaskStates.waiting_for_initiator_name)
    dp.message.register(process_initiator_phone, TaskStates.waiting_for_initiator_phone)