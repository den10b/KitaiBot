import asyncio

from aiogram import Router, F, types
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from database.models import TgUser
from tgbot.filters.user_filter import IsRegistered
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, ActionCallbackFactory, BackButtonCallbackFactory
from tgbot.keyboards.inline import profile_buttons, back_button
from tgbot.states.profile_state import ProfileState

profile_router = Router()
profile_router.message.filter(IsRegistered())
profile_router.callback_query.filter(IsRegistered())


@profile_router.callback_query(MainMenuCallbackFactory.filter(F.type == "profile"), state='*')
async def show_user_profile(call: types.CallbackQuery, user: TgUser, state: FSMContext):
    text = f"<b>Ф.И.О</b>: {user.name}\n" \
           f"<b>Номер телефона</b>: {user.phone_number}\n" \
           f"<b>Почта</b>: {user.email}"
    try:
        await call.message.edit_text(text, reply_markup=await profile_buttons())
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=await profile_buttons())
    await state.set_state(ProfileState.main)


@profile_router.callback_query(ActionCallbackFactory.filter(F.action == 'change_name'), state=ProfileState.main)
async def send_change_name_msg(call: types.CallbackQuery, state: FSMContext):
    text = 'Введите ваше ФИО: '
    key = await back_button('profile')
    await call.message.answer(text, reply_markup=key)
    await state.set_state(ProfileState.change_name)


@profile_router.callback_query(ActionCallbackFactory.filter(F.action == 'change_email'), state=ProfileState.main)
async def send_change_email_msg(call: types.CallbackQuery, state: FSMContext):
    text = 'Введите ваш email: '
    key = await back_button('profile')
    await call.message.answer(text, reply_markup=key)
    await state.set_state(ProfileState.change_email)


@profile_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'profile'), state=ProfileState)
async def cancel_change_profile_info(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.set_state(ProfileState.main)


@profile_router.message(ProfileState.change_name)
async def change_name_message(message: types.Message, state: FSMContext, user: TgUser):
    user.name = message.text
    user.save()
    text = f"<b>Ф.И.О</b>: {user.name}\n" \
           f"<b>Номер телефона</b>: {user.phone_number}\n" \
           f"<b>Почта</b>: {user.email}"
    await message.answer(text, reply_markup=await profile_buttons())
    await state.set_state(ProfileState.main)


@profile_router.message(ProfileState.change_email)
async def change_email_message(message: types.Message, state: FSMContext, user: TgUser):
    email = message.text
    try:
        validate_email(email)
    except ValidationError as e:
        logger.warning(e)
        await message.delete()
        msg = await message.answer('Неверный ввод! Повторите попытку!')
        await asyncio.sleep(2)
        return await msg.delete()
    user.email = message.text
    user.save()
    text = f"<b>Ф.И.О</b>: {user.name}\n" \
           f"<b>Номер телефона</b>: {user.phone_number}\n" \
           f"<b>Почта</b>: {user.email}"
    await message.answer(text, reply_markup=await profile_buttons())
    await state.set_state(ProfileState.main)
