from aiogram.dispatcher.fsm.state import StatesGroup, State


class ProfileState(StatesGroup):
    main = State()
    change_name = State()
    change_email = State()
