from aiogram.fsm.state import StatesGroup, State


class ShopState(StatesGroup):
    brand_choice = State()
    model_choice = State()
    product_choice = State()

