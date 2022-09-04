import asyncio

import httpx
from aiogram import Router, types, F
from aiogram.filters import Command, ContentTypesFilter
from aiogram.types import ContentType
from loguru import logger

from database import schemas
from tgbot.filters.user_filter import IsLogined
from tgbot.keyboards.inline import main_menu_buttons
from tgbot.keyboards.reply import phone_keyboard

reg_router = Router()
reg_router.message.filter(IsLogined(is_logined=False))


@reg_router.message(Command(commands='start'))
async def register_start_cmd(message: types.Message):
    await message.answer(text=f'Приветствую, {message.from_user.first_name}!\n'
                              f'Для авторизации в боте введите пароль!')


@reg_router.message(F.content_type == ContentType.TEXT)
async def registration_get_number(message: types.Message):
    """
    Ловим сообщения с паролем.

    :param message: Message
    :return: None
    """
    async with httpx.AsyncClient() as client:
        r = await client.get(url=f'http://127.0.0.1:8000/user/{message.from_user.id}')

    try:
        user = schemas.User.parse_raw(r.content)
    except Exception as e:
        logger.warning(e)
        await message.delete()
        msg = await message.answer('Вас нет в базе данных...')
        await asyncio.sleep(3)
        await msg.delete()
        return
    if message.text == user.password:
        text = f'{message.from_user.first_name}, вы успешно прошли авторизацию в боте!\n'
        await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
        await message.answer_photo("https://i.ibb.co/hWDN6Xb/wwzk0-n-YH50.jpg", 'Главное меню: ',
                                   reply_markup=main_menu_buttons)
        async with httpx.AsyncClient() as client:
            await client.put(url=f'http://127.0.0.1:8000/user/{message.from_user.id}',
                             headers={'content-type': 'application/json'}, json={"tg_tag": user.tg_tag,
                                                                                 "group_id": str(user.group_id),
                                                                                 "password": user.password,
                                                                                 "is_logined": True})
        await message.delete()
    else:

        msg = await message.answer('Вы отправили неверный пароль...')
        await asyncio.sleep(3)
        await message.delete()
        await msg.delete()


@reg_router.message(ContentTypesFilter(content_types=[types.ContentType.ANY]), state='*')
async def any_content_for_not_reg_user(message: types.Message):
    """
    Отвечаем на все сообщения незареганным юзерам!
    :param message: Message.
    :return: None
    """
    text = f'{message.from_user.first_name}, вы не прошли регистрацию!\n\n' \
           f'Для регистрации в боте отправьте номер телефона, нажав ' \
           f'на клавиатуру!'
    await message.answer(text, reply_markup=phone_keyboard)
