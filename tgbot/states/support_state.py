from aiogram.dispatcher.fsm.state import StatesGroup, State


class SupportState(StatesGroup):
    enter_date = State()
    enter_time = State()
    confirm = State()
