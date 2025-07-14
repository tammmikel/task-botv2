from aiogram.fsm.state import State, StatesGroup

class CompanyStates(StatesGroup):
    """Состояния для создания компании"""
    waiting_for_name = State()
    waiting_for_description = State()

class TaskStates(StatesGroup):
    """Состояния для создания задачи"""
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_company = State()
    waiting_for_initiator_name = State()
    waiting_for_initiator_phone = State()
    waiting_for_assignee = State()
    waiting_for_priority = State()
    waiting_for_deadline = State()