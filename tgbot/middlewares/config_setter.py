from aiogram import BaseMiddleware
from aiogram import types

from tgbot.config import Config


class ConfigSetter(BaseMiddleware):
    """
    Добавляем в **kwargs главный конфиг.
    """
    def __init__(self, config: Config):
        self.config = config

    async def __call__(self, handler, event: types.Message | types.CallbackQuery, data: dict):
        data['config'] = self.config
        await handler(event, data)
