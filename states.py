from aiogram.fsm.state import State, StatesGroup

class TaskStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_time = State()

class DealStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_amount = State()
    waiting_for_status = State()

class EditDealStates(StatesGroup):
    waiting_for_new_status = State()