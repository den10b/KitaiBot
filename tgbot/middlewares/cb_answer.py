from aiogram import BaseMiddleware
from aiogram import types


class CBAnswer(BaseMiddleware):
    """
    Middleware для отправки callback.answer в случае, если в функции мы его не отправляли.
    """
    async def __call__(self, handler, call: types.CallbackQuery, data: dict):
        await handler(call, data)
        await call.answer()
