import asyncio

from aiogram import Router, types, F
from aiogram.dispatcher.filters import Command, ContentTypesFilter

from tgbot.filters.user_filter import IsRegistered
from tgbot.keyboards.reply import phone_keyboard
from tgbot.keyboards.inline import main_menu_buttons
from database.models import TgUser, TgAdmin


reg_router = Router()
reg_router.message.filter(IsRegistered(is_registered=False))


@reg_router.message(Command(commands='start'), state='*')
async def register_start_cmd(message: types.Message):
    await message.answer(text=f'Приветствую, {message.from_user.first_name}!\n'
                              f'Для регистрации в боте отправьте номер телефона, нажав '
                              f'на клавиатуру!',
                         reply_markup=phone_keyboard)


@reg_router.message(F.content_type == 'contact')
async def registration_get_number(message: types.Message):
    """
    Ловим сообщения с контактом. Проверяем, принадлежит ли контакт юзеру или нет.

    :param message: Message
    :return: None
    """
    if message.contact.phone_number and message.contact.user_id == message.from_user.id:
        number = message.contact.phone_number.replace('+', '')
        new_user: TgUser = TgUser()
        new_user.user_id = message.from_user.id
        new_user.phone_number = number
        new_user.username = message.from_user.username
        new_user.save()
        if TgAdmin.objects.all().count() == 0:
            TgAdmin(user_id=new_user).save()
        text = f'{message.from_user.first_name}, вы успешно прошли регистрацию в боте!\n'
        await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
        await message.answer('Главное меню: ', reply_markup=main_menu_buttons)
    else:
        await message.delete()
        msg = await message.answer('Вы отправили не свой номер телефона...')
        await asyncio.sleep(3)
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
