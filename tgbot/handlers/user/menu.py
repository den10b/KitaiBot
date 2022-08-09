import asyncio
import datetime

from aiogram import Router, F, types, exceptions
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from tgbot.filters.user_filter import IsRegistered
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, ActionCallbackFactory, BackButtonCallbackFactory
from tgbot.keyboards.inline import back_button, shop_menu_buttons, buy_menu_buttons, sell_menu_buttons



menu_router = Router()
menu_router.message.filter(IsRegistered())
menu_router.callback_query.filter(IsRegistered())


@menu_router.callback_query(MainMenuCallbackFactory.filter(F.type == "menu"), state='*')
@menu_router.callback_query(BackButtonCallbackFactory.filter(F.to == "menu"), state='*')
async def menu_main(call: types.CallbackQuery, state: FSMContext):
    text = 'Здесь можно что-нибудь купить/продать: '
    key = shop_menu_buttons
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
    await state.clear()


@menu_router.callback_query(MainMenuCallbackFactory.filter(F.type == 'buy'), state='*')
async def menu_buy_call(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = 'Меню покупки: '
    key = buy_menu_buttons
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)


@menu_router.callback_query(MainMenuCallbackFactory.filter(F.type == 'sell'), state='*')
async def menu_sell_call(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = 'Меню продажи: '
    key = sell_menu_buttons
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
