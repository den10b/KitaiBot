from aiogram.dispatcher.fsm.state import StatesGroup, State


class ActualPricesState(StatesGroup):
    city_choice = State()
    metal_choice = State()
    sort_choice = State()
    pay_choice = State()
    price_page = State()
    phone_page = State()
