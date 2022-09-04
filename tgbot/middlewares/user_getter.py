import httpx
from aiogram import BaseMiddleware
from aiogram import types

from database import schemas
from database.models import UserModel


class UserGetter(BaseMiddleware):
    """
    Добавляем в **kwargs пользователя
    """

    async def __call__(self, handler, event: types.Message | types.CallbackQuery, data: dict):

        async with httpx.AsyncClient() as client:
            r = await client.get(f'http://127.0.0.1:8000/user/{event.from_user.id}')
        try:
            user = schemas.User.parse_raw(r.content)
        except:
            user = None
        data['user'] = user
        await handler(event, data)
