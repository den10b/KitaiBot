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
from tgbot.states.calculate_prices_state import CalculatePricesState

calculate_router = Router()
calculate_router.message.filter(IsRegistered())
calculate_router.callback_query.filter(IsRegistered())


@calculate_router.callback_query(CalculatePricesState.metal_choice,
                                     BackButtonCallbackFactory.filter(F.to == "city_choice"))
@calculate_router.callback_query(MainMenuCallbackFactory.filter(F.type == "calculate_prices"), state='*')
async def metal_choice(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text("Выберите город", reply_markup=await actual_city_choice_buttons())
    except Exception as e:
        logger.warning(e)
        await call.message.answer("Выберите город", reply_markup=await actual_city_choice_buttons())
    await state.set_state(CalculatePricesState.city_choice)


@calculate_router.callback_query(CalculatePricesState.sort_choice,
                                     BackButtonCallbackFactory.filter(F.to == "metal_choice"))
@calculate_router.callback_query(CalculatePricesState.city_choice, ActualPricesCallbackFactory.filter())
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
    await state.set_state(CalculatePricesState.metal_choice)


@calculate_router.callback_query(CalculatePricesState.pay_choice,
                                     BackButtonCallbackFactory.filter(F.to == "sort_choice"))
@calculate_router.callback_query(CalculatePricesState.metal_choice, ActualPricesCallbackFactory.filter())
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
    await state.set_state(CalculatePricesState.sort_choice)


@calculate_router.callback_query(CalculatePricesState.price_page,BackButtonCallbackFactory.filter(F.to == "pay_choice"))
@calculate_router.callback_query(CalculatePricesState.amount,BackButtonCallbackFactory.filter(F.to == "pay_choice"))
@calculate_router.callback_query(CalculatePricesState.sort_choice, ActualPricesCallbackFactory.filter())
async def metal_page(call: types.CallbackQuery, state: FSMContext, callback_data: ActualPricesCallbackFactory):
    try:
        await state.update_data({"probe": callback_data.action})
    except:
        pass
    try:
        await call.message.edit_text("Выберите способ оплаты:",
                                     reply_markup=await actual_payment_choice_buttons())
    except Exception as e:
        logger.warning(e)
        await call.message.answer("Выберите способ оплаты:", reply_markup=await actual_payment_choice_buttons())

    await state.set_state(CalculatePricesState.pay_choice)

@calculate_router.callback_query(CalculatePricesState.phone_page,BackButtonCallbackFactory.filter(F.to == "price_page"))
@calculate_router.callback_query(CalculatePricesState.pay_choice,
                                     ActualPricesCallbackFactory.filter())
async def amount_choice(call: types.CallbackQuery, state: FSMContext, callback_data: ActualPricesCallbackFactory):
    try:
        await state.update_data({"payment": callback_data.action})
        payment = callback_data.action
    except:
        payment = (await state.get_data()).get("payment")
    try:
        await call.message.edit_text('Введите кол-во: ',
                                     reply_markup=await back_button('pay_choice'))
    except Exception as e:
        logger.warning(e)
        await call.message.answer('Введите кол-во: ',
                                  reply_markup=await back_button('pay_choice'))
    await state.set_state(CalculatePricesState.amount)


@calculate_router.message(CalculatePricesState.amount)
async def enter_amount(message: types.Message, state: FSMContext):
    payment = (await state.get_data()).get("payment")
    if message.text.isdigit():
        city_object = CityInfo.objects.get(city=(await state.get_data()).get("city"))
        metal_object = MetalToSale.objects.get(city_id=city_object, metal=(await state.get_data()).get("metal"))
        probe = (await state.get_data()).get("probe")
        metal_price = getattr(MetalToSalePrice.objects.get(metal_id=metal_object, proba=probe), payment)
        if metal_price is None:
            metal_price = getattr(MetalToSalePrice.objects.get(metal_id=metal_object, proba=probe), "cash_price")
        comment = getattr(metal_object, f'{payment.split("_")[0]}_comment')
        if comment is None:
            comment = getattr(metal_object, "cash_comment")
        await message.answer(
            f"Город:{city_object.city}\nМеталл:{metal_object.metal}\nПроба:{probe}\n{comment}\nЦена:{metal_price}\n"
            f"Общая стоимость: {int(message.text) * metal_price}",
            reply_markup=await actual_price_page())
        await state.set_state(CalculatePricesState.price_page)
    else:
        await message.delete()
        msg = await message.answer('Неверный ввод! Введите число!')
        await asyncio.sleep(2)
        await msg.delete()


@calculate_router.callback_query(CalculatePricesState.price_page, ActualPricesCallbackFactory.filter())
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
    await state.set_state(CalculatePricesState.phone_page)
