from aiogram.dispatcher.fsm.state import StatesGroup, State


class NewsState(StatesGroup):
    get_word = State()
