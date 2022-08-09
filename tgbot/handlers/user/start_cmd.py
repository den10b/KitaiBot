from aiogram import Router, types, F
from aiogram.dispatcher.filters.command import CommandStart
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from tgbot.keyboards.callback_factory import BackButtonCallbackFactory
from tgbot.keyboards.inline import main_menu_buttons
from tgbot.filters.user_filter import IsRegistered

registration_router = Router()
registration_router.message.filter(IsRegistered())


@registration_router.message(CommandStart())
async def user_start(message: types.Message):
    await message.answer("Здравствуйте!\n"
                         "Я - бот Регион Золото, чем я могу помочь?",
                         reply_markup=main_menu_buttons)


@registration_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'main_menu'),
                                    state='*')
async def back_to_main_menu(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.edit_text('Вы вернулись в главное меню',
                                     reply_markup=main_menu_buttons)
    except Exception as e:
        logger.warning(e)
        await call.message.answer('Вы вернулись в главное меню',
                                  reply_markup=main_menu_buttons)
