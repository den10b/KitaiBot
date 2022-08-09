import asyncio

from aiogram import Router, F, types
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from tgbot.filters.user_filter import IsRegistered
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, ActionCallbackFactory, MetalSortCallbackFactory, \
    MetalCallbackFactory, BackButtonCallbackFactory, ShopActionCallbackFactory,MetalNdsCallbackFactory
from tgbot.keyboards.inline import back_button, main_menu_buttons, metal_choice_buttons, \
    sort_choice_buttons, metal_shop_action_buttons, metal_shop_check_buttons, nds_choice_buttons
from database.models import MetalToBuy, Sales, Basket, TgUser
from tgbot.states.metal_shop_state import MetalShopState

metal_shop_router = Router()
metal_shop_router.message.filter(IsRegistered())
metal_shop_router.callback_query.filter(IsRegistered())


@metal_shop_router.callback_query(MetalShopState.nds_choice, BackButtonCallbackFactory.filter(F.to == "metal_choice"))
@metal_shop_router.callback_query(MainMenuCallbackFactory.filter(F.type == "buy_metal"), state='*')
async def metal_choice(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text("Выберите металл", reply_markup=await metal_choice_buttons())
    except Exception as e:
        logger.warning(e)
        await call.message.answer("Выберите металл", reply_markup=await metal_choice_buttons())
    await state.set_state(MetalShopState.metal_choice)


@metal_shop_router.callback_query(MetalShopState.sort_choice, BackButtonCallbackFactory.filter(F.to == "nds_choice"))
@metal_shop_router.callback_query(MetalShopState.metal_choice, MetalCallbackFactory.filter())
async def sort_choice(call: types.CallbackQuery, state: FSMContext, callback_data: MetalCallbackFactory):
    try:
        await state.update_data({"metal": callback_data.metal,
                                 "sort_index": 0})
    except:
        pass

    try:
        await call.message.edit_text("Выберите:", reply_markup=await nds_choice_buttons())
    except Exception as e:
        logger.warning(e)
        await call.message.answer("Выберите:", reply_markup=await nds_choice_buttons())
        await call.message.delete()
    await state.set_state(MetalShopState.nds_choice)


@metal_shop_router.callback_query(MetalShopState.item_page, BackButtonCallbackFactory.filter(F.to == "sort_choice"))
@metal_shop_router.callback_query(MetalShopState.nds_choice, MetalNdsCallbackFactory.filter())
async def sort_choice(call: types.CallbackQuery, state: FSMContext, callback_data: MetalNdsCallbackFactory):
    try:
        await state.update_data({"nds": callback_data.is_nds})
    except:
        pass
    metal = (await state.get_data()).get("metal")
    try:
        await call.message.edit_text("Выберите форму:", reply_markup=await sort_choice_buttons(metal=metal))
    except Exception as e:
        logger.warning(e)
        await call.message.answer("Выберите форму:", reply_markup=await sort_choice_buttons(metal=metal))
        await call.message.delete()
    await state.set_state(MetalShopState.sort_choice)


@metal_shop_router.callback_query(MetalShopState.cart_check, BackButtonCallbackFactory.filter(F.to == "metal_page"))
@metal_shop_router.callback_query(MetalShopState.sort_choice, MetalSortCallbackFactory.filter())
@metal_shop_router.callback_query(MetalShopState.item_page, MetalSortCallbackFactory.filter())
async def metal_page(call: types.CallbackQuery, state: FSMContext, callback_data: MetalSortCallbackFactory):
    try:
        await state.update_data({"sort": callback_data.metal_sort})
        sort = callback_data.metal_sort
    except:
        sort = (await state.get_data()).get("sort")
    try:
        await state.update_data({"sort_index": callback_data.sort_index})
        sort_index = callback_data.sort_index
    except:
        sort_index = (await state.get_data()).get("sort_index")
    if sort == "Слиток":
        items = MetalToBuy.objects.filter(sort__contains=sort.lower(), name=(await state.get_data()).get("metal"))
        amount = len(items)
        item = items[sort_index]

    else:
        item = MetalToBuy.objects.get(name=(await state.get_data()).get("metal"), sort=sort)
        amount = 1

    await state.update_data({"true_sort": item.sort})

    description_text = f"{item.description}\n"
    if item.price_with_nds == item.price_without_nds:
        price_text = f"Цена: {str(item.price_without_nds)}₽"
        description_text += price_text
        await state.update_data({"prices": price_text,
                                 "price_int": item.price_without_nds})
    else:
        price_text = f"Цена с НДС: {str(item.price_with_nds)} ₽\nЦена без НДС: {str(item.price_without_nds)} ₽"
        await state.update_data({"prices": price_text,
                                 "price_int": item.price_with_nds})
        description_text += price_text
    await call.message.answer_photo(photo=item.image, caption=description_text,
                                    reply_markup=await metal_shop_action_buttons(current=sort_index, amount=amount))
    await call.message.delete()
    await state.set_state(MetalShopState.item_page)


@metal_shop_router.callback_query(MetalShopState.item_page, ActionCallbackFactory.filter(F.action == "to_metal_amount"))
async def amount_choice(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text("Введите количество:")
    except Exception as e:
        logger.warning(e)
        await call.message.answer("Введите количество:")
    await state.set_state(MetalShopState.amount_choice)


@metal_shop_router.message(MetalShopState.amount_choice,
                           ContentTypesFilter(content_types=types.ContentType.TEXT))
async def metal_check(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        await state.update_data({"amount": amount})
        current_data = await state.get_data()
        text = f"Проверьте детали заказа:\nМеталл: {current_data.get('metal')}\nВид: {current_data.get('true_sort')}\n{current_data.get('prices')}\nКоличество: {str(amount)}\n\nИтоговая стоимость: {str(amount * current_data.get('price_int'))} ₽"
        await message.answer(text, reply_markup=await metal_shop_check_buttons())
        await state.set_state(MetalShopState.cart_check)
    except Exception as e:
        logger.warning(e)
        err_msg = await message.answer('Неверный формат!\n'
                                       'Отправляйте целое число!')
        await message.delete()
        await asyncio.sleep(2)
        await err_msg.delete()


@metal_shop_router.message(MetalShopState.amount_choice,
                           ContentTypesFilter(content_types=[types.ContentType.ANY]))
async def amount_wrong(message: types.Message):
    msg = await message.answer('Неверный формат!\n'
                               'Отправляйте целое число!')
    await message.delete()
    await asyncio.sleep(3)
    await msg.delete()


@metal_shop_router.callback_query(MetalShopState.cart_check, ActionCallbackFactory.filter(F.action == "add_to_cart"))
async def metal_to_cart(call: types.CallbackQuery, state: FSMContext):
    current_sale, _ = Sales.objects.get_or_create(user_id=TgUser.objects.get(user_id=call.from_user.id),
                                                  status=Sales.Status.NEW)
    current_data = await state.get_data()
    metal = MetalToBuy.objects.get(name=current_data.get("metal"), sort=current_data.get("true_sort"))
    Basket(sales_id=current_sale, metal_id=metal, count=current_data.get("amount")).save()
    text = 'Товар успешно добавлен в корзину!\n' \
           'Выберите действие: '
    key = main_menu_buttons
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
