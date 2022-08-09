from aiogram.dispatcher.fsm.state import StatesGroup, State


class MetalShopState(StatesGroup):
    metal_choice = State()
    nds_choice=State()
    sort_choice = State()
    item_page = State()
    amount_choice = State()
    cart_check = State()
