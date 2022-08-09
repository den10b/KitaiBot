from aiogram.utils.keyboard import ReplyKeyboardBuilder


phone_keyboard = ReplyKeyboardBuilder()
phone_keyboard.button(text='Отправить номер телефона', request_contact=True)
phone_keyboard = phone_keyboard.as_markup()
phone_keyboard.resize_keyboard = True
