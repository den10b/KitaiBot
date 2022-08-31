from aiogram.filters import BaseFilter
from aiogram import types

from database.models import UserModel


class IsRegistered(BaseFilter):
    """
    Зарегистрирован ли пользователь в боте.
    """
    is_registered: bool = True

    async def __call__(self, update: types.Message | types.CallbackQuery) -> bool:
        user: UserModel | None = UserModel.objects.filter(user_id=update.from_user.id).first()
        if user:
            return True is self.is_registered
        return False is self.is_registered


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
