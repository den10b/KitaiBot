from aiogram.dispatcher.fsm.state import StatesGroup, State


class CalculatePricesState(StatesGroup):
    city_choice = State()
    metal_choice = State()
    sort_choice = State()
    pay_choice = State()
    amount = State()
    price_page = State()
    phone_page = State()
