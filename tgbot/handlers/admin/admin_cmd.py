from aiogram import Router, types, F
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from tgbot.keyboards.callback_factory import BackButtonCallbackFactory
from tgbot.keyboards.inline import admin_menu
from tgbot.filters.user_filter import IsAdmin

admin_cmd_router = Router()
admin_cmd_router.message.filter(IsAdmin())
admin_cmd_router.callback_query.filter(IsAdmin())


@admin_cmd_router.message(Command(commands=['admin']))
async def admin_cmd(message: types.Message):
    await message.answer("Здравствуйте!\n"
                         "Вы попали в админ меню! ",
                         reply_markup=admin_menu)


@admin_cmd_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'admin_menu'), state='*')
async def back_to_admin_cmd(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.edit_text(text='Вы вернулись в админ меню: ',
                                     reply_markup=admin_menu)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text='Вы вернулись в админ меню: ',
                                  reply_markup=admin_menu)
