from aiogram.dispatcher.fsm.state import StatesGroup, State


class BasketState(StatesGroup):
    main = State()
    change = State()
    basket_choice = State()
    change_amount = State()
    delete = State()
    city_choice = State()
    phone_number = State()
    confirm = State()
