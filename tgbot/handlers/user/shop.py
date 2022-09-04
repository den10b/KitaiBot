import asyncio
import datetime

from aiogram import Router, F, types, exceptions
from aiogram.fsm.context import FSMContext
from loguru import logger

from tgbot.filters.user_filter import IsRegistered
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, ActionCallbackFactory, BackButtonCallbackFactory
from tgbot.keyboards.inline import *
from tgbot.states.shop import ShopState


shop_router = Router()
shop_router.message.filter(IsRegistered())
shop_router.callback_query.filter(IsRegistered())


@shop_router.callback_query(MainMenuCallbackFactory.filter(F.type == "shop_brand"), state='*')
@shop_router.callback_query(BackButtonCallbackFactory.filter(F.to == "shop_brand"), state=ShopState.model_choice)
async def brand_choice(call: types.CallbackQuery, state: FSMContext):
    text = 'Выберите бренд: '
    key = shop_brand_buttons
    await call.message.answer_photo("https://i.ibb.co/fMnLwtf/NZWtb-DBUUMI.jpg",text, reply_markup=await key())
    await state.set_state(ShopState.brand_choice)


@shop_router.callback_query(ShopCallbackFactory.filter(), state=ShopState.brand_choice)
@shop_router.callback_query(BackButtonCallbackFactory.filter(F.to == "shop_model"), state=ShopState.product_choice)
async def model_choice(call: types.CallbackQuery, state: FSMContext, callback_data: ShopCallbackFactory):
    try:
        await state.update_data({"brand": callback_data.action})
        brand = callback_data.action
    except:
        brand = (await state.get_data()).get("brand")

    text = 'Выберите модель: '
    key = shop_model_buttons
    try:
        await call.message.edit_text(text, reply_markup=await key(brand))
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=await key(brand))
    await state.set_state(ShopState.model_choice)
@shop_router.callback_query(ShopCallbackFactory.filter(), state=ShopState.model_choice)
# @shop_router.callback_query(BackButtonCallbackFactory.filter(F.to == "shop_product"), state="*")
async def model_choice(call: types.CallbackQuery, state: FSMContext, callback_data: ShopCallbackFactory):
    try:
        await state.update_data({"model": callback_data.action})
        model = callback_data.action
    except:
        model = (await state.get_data()).get("model")

    text = 'Выберите продукт: '
    key = shop_product_buttons
    try:
        await call.message.edit_text(text, reply_markup=await key(model))
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=await key(model))
    await state.set_state(ShopState.product_choice)

# @menu_router.callback_query(MainMenuCallbackFactory.filter(F.type == 'sell'), state='*')
# async def menu_sell_call(call: types.CallbackQuery, state: FSMContext):
#     await state.clear()
#     text = 'Меню продажи: '
#     key = sell_menu_buttons
#     try:
#         await call.message.edit_text(text, reply_markup=key)
#     except Exception as e:
#         logger.warning(e)
#         await call.message.answer(text, reply_markup=key)
