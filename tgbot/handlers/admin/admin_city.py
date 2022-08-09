import asyncio
from dataclasses import dataclass
import datetime

from aiogram import Router, F, types, exceptions
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from tgbot.filters.user_filter import IsAdmin
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, ActionCallbackFactory, BackButtonCallbackFactory
from tgbot.keyboards.inline import support_buttons, back_button, support_confirmation, admin_city, pass_or_back
from tgbot.config import Config
from tgbot.states.admin_city_state import AdminCityState
from database.models import TgUser, BackCall, TgAdmin, FAQ, CityInfo, CityAddress, CityPhoneNumbers
from tgbot.services.broadcaster import broadcast
from tgbot.services.simple_calendar import calendar_callback, SimpleCalendar

admin_city_router = Router()
admin_city_router.message.filter(IsAdmin())
admin_city_router.callback_query.filter(IsAdmin())


@dataclass
class AdminCityNumber:
    number: str
    comment: str


@admin_city_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'admin_city'), state=AdminCityState)
@admin_city_router.callback_query(MainMenuCallbackFactory.filter(F.type == "admin_city"), state='*')
async def admin_city_main(call: types.CallbackQuery, state: FSMContext):
    text = 'Меню городов'
    key = await admin_city()
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
    await state.set_state(AdminCityState.main)


@admin_city_router.callback_query(ActionCallbackFactory.filter(F.action == 'admin_city_add'), AdminCityState.main)
async def admin_city_add_main(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text('Введите название города: ',
                                           reply_markup=await back_button('admin_city'))
        msg = call.message
    except Exception as e:
        logger.warning(e)
        msg = await call.message.answer('Введите название города: ',
                                        reply_markup=await back_button('admin_city'))
    await state.set_state(AdminCityState.add)
    await state.set_data({'main_msg': msg})


@admin_city_router.message(AdminCityState.add)
async def admin_city_add_name(message: types.Message, state: FSMContext):
    city = CityInfo.objects.filter(city=message.text).first()
    await message.delete()
    if city:
        msg = await message.answer('Такой город есть в бд! Введите другой!')
        await asyncio.sleep(2)
        await msg.delete()
    else:
        data = await state.get_data()
        main_msg: types.Message = data.get('main_msg')
        text = 'Введите ссылку на сайт города либо жмите на кнопку: '
        key = await pass_or_back('admin_city')
        await state.update_data({'city': message.text})
        await state.set_state(AdminCityState.add_link)
        try:
            await main_msg.edit_text(text, reply_markup=key)

        except Exception as e:
            logger.warning(e)


@admin_city_router.message(AdminCityState.add_link)
async def admin_city_add_link(message: types.Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    main_msg: types.Message = data.get('main_msg')
    await state.update_data({'link': message.text})
    text = 'Введите адрес для города: '
    key = await back_button('admin_city')
    try:
        await main_msg.edit_text(text, reply_markup=key)\

    except Exception as e:
        logger.warning(e)
    await state.set_state(AdminCityState.add_address)


@admin_city_router.callback_query(ActionCallbackFactory.filter(F.action == 'pass'), AdminCityState.add_link)
async def admin_city_skip_link(call: types.CallbackQuery, state: FSMContext):
    text = 'Введите адрес для города: '
    key = await back_button('admin_city')
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
    await state.set_state(AdminCityState.add_address)


@admin_city_router.message(AdminCityState.add_address)
async def admin_city_add_address(message: types.Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    address = data.get('address', [])
    if message.text not in address:
        address.append(message.text)
    main_msg = data.get('main_msg')
    await state.update_data({'address': address})
    text = 'Введите еще адрес для города либо жмите на кнопку: '
    key = await pass_or_back('admin_city')
    try:
        await main_msg.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)


@admin_city_router.callback_query(ActionCallbackFactory.filter(F.action == 'pass'), AdminCityState.add_address)
async def admin_city_skip_address(call: types.CallbackQuery, state: FSMContext):
    text = 'Введите номер телефона: '
    key = await back_button('admin_city')
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
    await state.set_state(AdminCityState.add_number)


@admin_city_router.message(AdminCityState.add_number)
async def admin_city_add_number(message: types.Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    main_msg: types.Message = data.get('main_msg')
    text = 'Введите комментарий к номеру телефона: '
    key = await back_button('admin_city')
    try:
        await main_msg.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
    await state.set_state(AdminCityState.add_comment)
    await state.update_data({'number': message.text})


@admin_city_router.message(AdminCityState.add_comment)
async def admin_city_add_comment(message: types.Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    number = data.get('number')
    contacts = data.get('contacts', [])
    contacts.append(AdminCityNumber(number=number, comment=message.text))
    main_msg = data.get('main_msg')
    key = await pass_or_back('admin_city')
    text = 'Введите еще адрес либо жмите на кнопку: '
    try:
        await main_msg.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
    await state.set_state(AdminCityState.add_number)
    await state.update_data({'contacts': contacts})


@admin_city_router.callback_query(ActionCallbackFactory.filter(F.action == 'pass'), AdminCityState.add_number)
async def finish_add_city(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    city = data.get('city')
    link = data.get('link', None)
    address = data.get('address')   # list
    contacts = data.get('contacts')
    if link:
        city = CityInfo.objects.create(city=city, link=link)
    else:
        city = CityInfo.objects.create(city=city)
    for city_address in address:
        CityAddress.objects.create(city_id=city, address=city_address)
    for contact in contacts:
        CityPhoneNumbers.objects.create(city_info_id=city,
                                        phone_number=contact.number,
                                        comment=contact.comment)
    text = 'Меню городов: '
    key = await admin_city()
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)

