from aiogram import Router, types, F
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from loguru import logger

from tgbot.keyboards.callback_factory import BackButtonCallbackFactory
from tgbot.keyboards.inline import main_menu_buttons
from tgbot.filters.user_filter import IsLogined

registration_router = Router()
registration_router.message.filter(IsLogined())


@registration_router.message(CommandStart())
async def user_start(message: types.Message):
    text= "Здравствуйте!\nЯ - бот 1"
    await message.answer_photo(photo="https://i.ibb.co/hWDN6Xb/wwzk0-n-YH50.jpg",caption=text,
                         reply_markup=main_menu_buttons)


@registration_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'main_menu'),
                                    state='*')
async def back_to_main_menu(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = "Вы вернулмсь в главное меню"
    await call.message.answer_photo(photo="https://i.ibb.co/hWDN6Xb/wwzk0-n-YH50.jpg", caption=text,
                               reply_markup=main_menu_buttons)
