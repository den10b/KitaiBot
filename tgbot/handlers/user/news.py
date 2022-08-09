import asyncio

from aiogram import Router, types, F
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from database.models import UserNews, TgUser
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, ActionCallbackFactory
from tgbot.keyboards.inline import main_menu_buttons, user_news
from tgbot.states.news_state import NewsState

news_router = Router()


@news_router.callback_query(MainMenuCallbackFactory.filter(F.type == "news"))
async def news_start(call: types.CallbackQuery, state: FSMContext, user):
    text = 'Выберите подписку на новости: '
    key = await user_news(user)
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)


@news_router.callback_query(ActionCallbackFactory.filter(F.action == 'user_news'), state='*')
async def change_user_news(call: types.CallbackQuery, state: FSMContext, user: TgUser):
    text = 'Вы отписались от новостей' if user.news else 'Вы подписались на новости!'
    user.news = False if user.news else True
    user.save()
    key = await user_news(user)
    await call.answer(text, show_alert=True)
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
