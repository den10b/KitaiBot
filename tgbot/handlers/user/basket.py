import asyncio

from aiogram import Router, F, types
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from database.models import TgUser, Sales, Basket, CityInfo
from tgbot.filters.user_filter import IsRegistered
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, ActionCallbackFactory, BackButtonCallbackFactory, \
    CityInfoCallbackFactory, BasketValueCallbackFactory
from tgbot.keyboards.inline import profile_buttons, back_button, basket_buttons, city_info_buttons, main_menu_buttons, \
    basket_sale_buttons, basket_value_action, confirmation
from tgbot.keyboards.reply import phone_keyboard
from tgbot.states.basket_state import BasketState
from tgbot.states.profile_state import ProfileState

basket_router = Router()
basket_router.message.filter(IsRegistered())
basket_router.callback_query.filter(IsRegistered())


@basket_router.callback_query(MainMenuCallbackFactory.filter(F.type == "basket"), state='*')
@basket_router.callback_query(BackButtonCallbackFactory.filter(F.to == "basket_main"), state=BasketState.city_choice)
@basket_router.callback_query(BackButtonCallbackFactory.filter(F.to == "basket_main"), state=BasketState.change)
async def basket_main_call(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(BasketState.main)
    sale = Sales.objects.filter(user_id=call.from_user.id,
                                status=Sales.Status.NEW).first()
    await state.update_data({'sale': sale})
    if sale:
        metal_basket = Basket.objects.filter(sales_id=sale, metal_id__isnull=False)
        gem_basket = Basket.objects.filter(sales_id=sale, gem_id__isnull=False)
        text = '\n'
        if metal_basket.count() > 0:
            text += 'Корзина металлов: \n======================\n'
            for metal in metal_basket:
                text += f'Металл: {metal.metal_id.name}\nВид: {metal.metal_id.sort} \nКоличество: {metal.count}\nЦена: {metal.count*metal.metal_id.price_with_nds} ₽\n'
                text += "----------------------\n"
        if gem_basket.count() > 0:
            text += '\nКорзина камней: \n======================\n'
            for gem in gem_basket:
                text += f'Размер GIA: {gem.gem_id.size}\nФорма GIA: {gem.gem_id.form}\nДеф. GIA: {gem.gem_id.def_gia}\nКоличество: {gem.count}\nЦена: $ {gem.count*gem.gem_id.price}\n'
                text += "----------------------\n"

        key = await basket_buttons(sale)
        try:
            await call.message.edit_text(text, reply_markup=key)
        except Exception as e:
            logger.warning(e)
            await call.message.answer(text, reply_markup=key)
        return
    text = 'Ваша корзина пуста!'
    key = await back_button('menu')
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)


@basket_router.callback_query(ActionCallbackFactory.filter(F.action == 'checkout'),
                              state=BasketState.main)
@basket_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'city_choice'), BasketState.phone_number)
async def city_choice(call: types.CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    msg_to_delete = current_data.get('msg_to_delete', None)
    if msg_to_delete:
        await msg_to_delete.delete()
    text = 'Выберите нужный город: '
    key = await city_info_buttons('basket_main',is_basket=True)
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
    await state.set_state(BasketState.city_choice)


@basket_router.callback_query(CityInfoCallbackFactory.filter(), BasketState.city_choice)
async def waiting_phone_number(call: types.CallbackQuery, state: FSMContext, callback_data: CityInfoCallbackFactory):
    city = CityInfo.objects.filter(pk=callback_data.city).first()
    text = 'Отправьте номер телефона: '
    key = await back_button('city_choice')
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
    msg = await call.message.answer('Отправьте номер телефона: ', reply_markup=phone_keyboard)
    await state.set_state(BasketState.phone_number)
    await state.update_data({'msg_to_delete': msg,
                             'city': city})


@basket_router.message(BasketState.phone_number, F.content_type == 'contact')
async def get_phone_number(message: types.Message, state: FSMContext):
    if message.contact.phone_number and message.contact.user_id == message.from_user.id:
        number = message.contact.phone_number.replace('+', '')
        current_data = await state.get_data()
        msg_to_delete = current_data.get('msg_to_delete', None)
        sale: Sales = current_data.get('sale')
        city: CityInfo = current_data.get('city')
        sale.city = city
        sale.phone_number = number
        sale.status = Sales.Status.CREATED
        sale.save()
        if msg_to_delete:
            await msg_to_delete.delete()
        await state.clear()
        await message.answer('Ваша заявка успешно оформлена!', reply_markup=main_menu_buttons)
    else:
        await message.delete()
        msg = await message.answer('Вы отправили не свой номер телефона...')
        await asyncio.sleep(2)
        await msg.delete()


@basket_router.callback_query(ActionCallbackFactory.filter(F.action == 'change_basket'),
                              state=BasketState.main)
@basket_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'basket_pagination'),
                              state=BasketState.change)
async def basket_change_main(call: types.CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    sale = current_data.get('sale')
    text = 'Выбирайте'
    key = await basket_sale_buttons(sale)
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
    await state.set_state(BasketState.change)
    await state.update_data({'page_index': 1})


@basket_router.callback_query(ActionCallbackFactory.filter(F.action == 'basket_next_page'), BasketState.change)
@basket_router.callback_query(ActionCallbackFactory.filter(F.action == 'basket_prev_page'), BasketState.change)
async def basket_change_page(call: types.CallbackQuery, state: FSMContext, callback_data: ActionCallbackFactory):
    current_data = await state.get_data()
    sale = current_data.get('sale')
    page_index = current_data.get('page_index', 1)
    page_index += 1 if callback_data.action == 'basket_next_page' else -1
    text = 'Выбирайте'
    key = await basket_sale_buttons(sale, page_index)
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
    await state.set_state(BasketState.change)
    await state.update_data({'page_index': page_index})


@basket_router.callback_query(BasketValueCallbackFactory.filter(), BasketState.change)
@basket_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'basket_value'), BasketState.change_amount)
@basket_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'basket_value'), BasketState.delete)
async def basket_value_menu(call: types.CallbackQuery, state: FSMContext, callback_data: BasketValueCallbackFactory):
    current_data = await state.get_data()
    if isinstance(callback_data, BasketValueCallbackFactory):
        basket = Basket.objects.get(pk=callback_data.pk)
    else:
        basket = current_data.get('basket', None)
    if basket.metal_id:
        text = f'{basket.metal_id.name} | {basket.metal_id.sort}\nКоличество:  {basket.count}'
    else:
        text = f'{basket.gem_id.size} | {basket.gem_id.form} |{basket.gem_id.def_gia}\nКоличество:  {basket.count}'

    key = await basket_value_action()
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
    await state.set_state(BasketState.change)
    await state.update_data({'basket': basket})


@basket_router.callback_query(ActionCallbackFactory.filter(F.action == 'change_amount'), BasketState.change)
async def change_basket_amount(call: types.CallbackQuery, state: FSMContext):
    text = 'Введите новое кол-во: '
    key = await back_button('basket_value')
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
    await state.set_state(BasketState.change_amount)


@basket_router.message(BasketState.change_amount)
async def change_basket_amount_msg(message: types.Message, state: FSMContext):
    current_data = await state.get_data()
    basket: Basket = current_data.get('basket')
    if message.text.isdigit():
        basket.count = int(message.text)
        basket.save()
        if basket.metal_id:
            text = f'{basket.metal_id.name} | {basket.metal_id.sort}\nКоличество: {basket.count}'
        else:
            text = f'{basket.gem_id.size} | {basket.gem_id.form} |{basket.gem_id.def_gia}\nКоличество:  {basket.count}'

        key = await basket_value_action()
        await message.answer(text, reply_markup=key)
        await state.set_state(BasketState.change)
        await state.update_data({'basket': basket})
    else:
        await message.delete()
        msg = await message.answer('неверный ввод! Введите число')
        await asyncio.sleep(2)
        await msg.delete()


@basket_router.callback_query(ActionCallbackFactory.filter(F.action == 'delete_from_basket'), BasketState.change)
async def delete_from_basket(call: types.CallbackQuery, state: FSMContext):
    text = 'Вы уверены, что хотите удалить?'
    key = await confirmation('basket_value')
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
    await state.set_state(BasketState.delete)


@basket_router.callback_query(ActionCallbackFactory.filter(F.action == 'confirm'), BasketState.delete)
async def confirm_delete_from_basket(call: types.CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    basket: Basket = current_data.get('basket')
    basket.delete()
    await basket_change_main(call, state)








