from aiogram import Dispatcher

from .user import setup as user_setup
from .admin import setup as admin_setup


def setup(main_dp: Dispatcher):
    user_setup(main_dp)
    admin_setup(main_dp)
