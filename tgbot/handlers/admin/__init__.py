from aiogram import Dispatcher

from .admin_cmd import admin_cmd_router
# from .admin_city import admin_city_router


def setup(main_dp: Dispatcher):
    main_dp.include_router(admin_cmd_router)
    # main_dp.include_router(admin_city_router)
