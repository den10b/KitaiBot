from aiogram.dispatcher.fsm.state import StatesGroup, State


class StonesShopState(StatesGroup):
    size_choice = State()
    form_choice = State()
    def_choice = State()
    stone_choice = State()
    amount_choice = State()
    complete_shopping = State()
