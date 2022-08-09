from aiogram import BaseMiddleware
from aiogram import types

from database.models import TgUser


class UserGetter(BaseMiddleware):
    """
    Добавляем в **kwargs пользователя
    """
    async def __call__(self, handler, event: types.Message | types.CallbackQuery, data: dict):
        user: TgUser | None = TgUser.objects.filter(user_id=event.from_user.id).first()
        data['user'] = user
        await handler(event, data)
