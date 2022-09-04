import httpx
from aiogram.filters import BaseFilter
from aiogram import types

from database import schemas
from database.models import UserModel


class IsLogined(BaseFilter):
    """
    Зарегистрирован ли пользователь в боте.
    """
    is_logined: bool = True

    async def __call__(self, update: types.Message | types.CallbackQuery) -> bool:
        async with httpx.AsyncClient() as client:
            r = await client.get(f'http://127.0.0.1:8000/user/{update.from_user.id}')
        try:
            user = schemas.User.parse_raw(r.content)
            return user.is_logined is self.is_logined
        except:
            return False is self.is_logined




class IsAdmin(BaseFilter):
    """
    Является ли пользователь администратором бота.
    """
    is_admin: bool = True

    async def __call__(self, update: types.Message | types.CallbackQuery) -> bool:
        user = TgUser.objects.filter(user_id=update.from_user.id).first()
        if user:
            if user.is_admin():
                return True is self.is_admin
        return False is self.is_admin
