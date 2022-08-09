from aiogram import Dispatcher

from .cb_answer import CBAnswer
from .user_getter import UserGetter


def setup(dp: Dispatcher):
    dp.callback_query.middleware(CBAnswer())
    dp.message.middleware(UserGetter())
    dp.callback_query.middleware(UserGetter())
