from aiogram import Dispatcher


from .register import reg_router
from .start_cmd import registration_router
from .menu import menu_router


def setup(main_dp: Dispatcher):
    main_dp.include_router(reg_router)
    main_dp.include_router(registration_router)
    main_dp.include_router(menu_router)
