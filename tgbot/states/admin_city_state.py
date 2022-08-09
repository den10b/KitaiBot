from aiogram.dispatcher.fsm.state import StatesGroup, State


class AdminCityState(StatesGroup):
    main = State()
    add = State()
    add_link = State()
    add_address = State()
    add_number = State()
    add_comment = State()
