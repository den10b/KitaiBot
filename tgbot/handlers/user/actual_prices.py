import asyncio

from aiogram import Router, F, types
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from tgbot.filters.user_filter import IsRegistered
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, ActionCallbackFactory, MetalSortCallbackFactory, \
    MetalCallbackFactory, BackButtonCallbackFactory, ShopActionCallbackFactory, ActualPricesCallbackFactory
from tgbot.keyboards.inline import back_button, main_menu_buttons, metal_choice_buttons, \
    sort_choice_buttons, actual_city_choice_buttons, actual_price_page, actual_manager_page, \
    actual_metal_choice_buttons, actual_payment_choice_buttons, actual_proba_choice_buttons
from database.models import MetalToBuy, Sales, Basket, TgUser, CityInfo, MetalToSale, MetalToSalePrice,CityPhoneNumbers
from tgbot.states.actual_prices_state import ActualPricesState

actual_prices_router = Router()
actual_prices_router.message.filter(IsRegistered())
actual_prices_router.callback_query.filter(IsRegistered())


@actual_prices_router.callback_query(ActualPricesState.metal_choice,
                                     BackButtonCallbackFactory.filter(F.to == "city_choice"))
@actual_prices_router.callback_query(MainMenuCallbackFactory.filter(F.type == "actual_prices"), state='*')
async def metal_choice(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text("Выберите город", reply_markup=await actual_city_choice_buttons())
    except Exception as e:
        logger.warning(e)
        await call.message.answer("Выберите город", reply_markup=await actual_city_choice_buttons())
    await state.set_state(ActualPricesState.city_choice)


@actual_prices_router.callback_query(ActualPricesState.sort_choice,
                                     BackButtonCallbackFactory.filter(F.to == "metal_choice"))
@actual_prices_router.callback_query(ActualPricesState.city_choice, ActualPricesCallbackFactory.filter())
async def metal_choice(call: types.CallbackQuery, state: FSMContext, callback_data: ActualPricesCallbackFactory):
    try:
        await state.update_data({"city": callback_data.action})
        city = callback_data.action
    except:
        city = (await state.get_data()).get("city")
    city_object = CityInfo.objects.get(city=city)
    try:
        await call.message.edit_text("Выберите металл", reply_markup=await actual_metal_choice_buttons(city_object))
    except Exception as e:
        logger.warning(e)
        await call.message.answer("Выберите металл", reply_markup=await actual_metal_choice_buttons(city_object))
    await state.set_state(ActualPricesState.metal_choice)


@actual_prices_router.callback_query(ActualPricesState.pay_choice,
                                     BackButtonCallbackFactory.filter(F.to == "sort_choice"))
@actual_prices_router.callback_query(ActualPricesState.metal_choice, ActualPricesCallbackFactory.filter())
async def sort_choice(call: types.CallbackQuery, state: FSMContext, callback_data: ActualPricesCallbackFactory):
    try:
        await state.update_data({"metal": callback_data.action})
        metal = callback_data.action
    except:
        metal = (await state.get_data()).get("metal")
    city_object = CityInfo.objects.get(city=(await state.get_data()).get("city"))
    metal_object = MetalToSale.objects.get(city_id=city_object, metal=metal)
    try:
        await call.message.edit_text("Выберите пробу:",
                                     reply_markup=await actual_proba_choice_buttons(metal=metal_object))
    except Exception as e:
        logger.warning(e)
        await call.message.answer("Выберите пробу:", reply_markup=await actual_proba_choice_buttons(metal=metal_object))
    await state.set_state(ActualPricesState.sort_choice)


@actual_prices_router.callback_query(ActualPricesState.price_page,BackButtonCallbackFactory.filter(F.to == "pay_choice"))
@actual_prices_router.callback_query(ActualPricesState.sort_choice, ActualPricesCallbackFactory.filter())
async def metal_page(call: types.CallbackQuery, state: FSMContext, callback_data: ActualPricesCallbackFactory):
    try:
        await state.update_data({"probe": callback_data.action})
    except:
        pass
    city_object = CityInfo.objects.get(city=(await state.get_data()).get("city"))
    metal_object = MetalToSale.objects.get(city_id=city_object, metal=(await state.get_data()).get("metal"))
    try:
        await call.message.edit_text("Выберите способ оплаты:",
                                     reply_markup=await actual_payment_choice_buttons(metal_object))
    except Exception as e:
        logger.warning(e)
        await call.message.answer("Выберите способ оплаты:", reply_markup=await actual_payment_choice_buttons(metal_object))

    await state.set_state(ActualPricesState.pay_choice)

@actual_prices_router.callback_query(ActualPricesState.phone_page,BackButtonCallbackFactory.filter(F.to == "price_page"))
@actual_prices_router.callback_query(ActualPricesState.pay_choice,
                                     ActualPricesCallbackFactory.filter())
async def amount_choice(call: types.CallbackQuery, state: FSMContext, callback_data: ActualPricesCallbackFactory):
    try:
        await state.update_data({"payment": callback_data.action})
        payment = callback_data.action
    except:
        payment = (await state.get_data()).get("payment")
    city_object = CityInfo.objects.get(city=(await state.get_data()).get("city"))
    metal_object = MetalToSale.objects.get(city_id=city_object, metal=(await state.get_data()).get("metal"))
    probe = (await state.get_data()).get("probe")
    metal_price = getattr(MetalToSalePrice.objects.get(metal_id=metal_object,proba=probe),payment)
    if metal_price is None:
        metal_price = getattr(MetalToSalePrice.objects.get(metal_id=metal_object,proba=probe),"cash_price")
    comment = getattr(metal_object,f'{payment.split("_")[0]}_comment')
    if comment is None:
        comment = getattr(metal_object,"cash_comment")
    try:
        await call.message.edit_text(
            f"Город: {city_object.city}\nМеталл: {metal_object.metal}\n{probe}\n{comment}\nЦена: {metal_price} ₽\n",
            reply_markup=await actual_price_page())
    except Exception as e:
        logger.warning(e)
        await call.message.answer(
            f"Город: {city_object.city}\nМеталл: {metal_object.metal}\n{probe}\n{comment}\nЦена: {metal_price} ₽\n",
            reply_markup=await actual_price_page())
    await state.set_state(ActualPricesState.price_page)


@actual_prices_router.callback_query(ActualPricesState.price_page, ActualPricesCallbackFactory.filter())
async def metal_to_cart(call: types.CallbackQuery, state: FSMContext):
    city_object = CityInfo.objects.get(city=(await state.get_data()).get("city"))
    phone = CityPhoneNumbers.objects.get(city_info_id=city_object).phone_number
    try:
        await call.message.edit_text(
            f"Номер телефона:{phone}\n",
            reply_markup=await actual_manager_page())
    except Exception as e:
        logger.warning(e)
        await call.message.answer(
            f"Номер телефона:{phone}\n",
            reply_markup=await actual_manager_page())
    await state.set_state(ActualPricesState.phone_page)
