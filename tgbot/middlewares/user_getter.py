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
        user = None
        async with httpx.AsyncClient() as client:
            r = await client.get('http://127.0.0.1:8000/user')
        for user_json in r.json():
            if user_json.get("tg_id") == event.from_user.id:
                user = schemas.User.parse_raw(str(user_json).replace("'", '"'))
        data['user'] = user
        await handler(event, data)
