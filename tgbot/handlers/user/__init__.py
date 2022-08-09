from aiogram import Dispatcher

from .news import news_router
from .profile import profile_router
from .register import reg_router
from .start_cmd import registration_router
from .reviews import reviews_router
from .contacts import contacts_router
from .metal_shop import metal_shop_router
from .stones_shop import stones_shop_router
from .actual_prices import actual_prices_router
from .support import support_router
from .menu import menu_router
from .contacts import contacts_router
from .basket import basket_router
from .calculate_prices import calculate_router


def setup(main_dp: Dispatcher):
    main_dp.include_router(reg_router)
    main_dp.include_router(registration_router)
    main_dp.include_router(reviews_router)
    main_dp.include_router(profile_router)
    main_dp.include_router(support_router)
    main_dp.include_router(menu_router)
    main_dp.include_router(metal_shop_router)
    main_dp.include_router(stones_shop_router)
    main_dp.include_router(contacts_router)
    main_dp.include_router(basket_router)
    main_dp.include_router(actual_prices_router)
    main_dp.include_router(calculate_router)
    main_dp.include_router(news_router)
