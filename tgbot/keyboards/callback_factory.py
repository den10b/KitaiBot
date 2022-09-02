from uuid import UUID

from aiogram.filters.callback_data import CallbackData


class MainMenuCallbackFactory(CallbackData, prefix='mainmenu'):
    type: str


class BackButtonCallbackFactory(CallbackData, prefix='back'):
    to: str


class ActionCallbackFactory(CallbackData, prefix='action'):
    action: str
class ShopCallbackFactory(CallbackData, prefix='shop'):
    action: UUID

