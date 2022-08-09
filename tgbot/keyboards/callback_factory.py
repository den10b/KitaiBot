from aiogram.dispatcher.filters.callback_data import CallbackData


class MainMenuCallbackFactory(CallbackData, prefix='mainmenu'):
    type: str


class BackButtonCallbackFactory(CallbackData, prefix='back'):
    to: str


class ActionCallbackFactory(CallbackData, prefix='action'):
    action: str


class ShopActionCallbackFactory(CallbackData, prefix='shop_action'):
    action: str


class MetalCallbackFactory(CallbackData, prefix='metal'):
    metal: str
class MetalNdsCallbackFactory(CallbackData, prefix='metal_nds'):
    is_nds: bool

class MetalSortCallbackFactory(CallbackData, prefix='metal_sort'):
    metal_sort: str
    sort_index: int


class ActualPricesCallbackFactory(CallbackData, prefix='actual_prices'):
    action: str


class FilterCallbackFactory(CallbackData, prefix='filter'):
    filter_type: str
    filter_description: str


class NavigationCallbackFactory(CallbackData, prefix='navigation'):
    navigation_type: str
    list_number: int


class CityInfoCallbackFactory(CallbackData, prefix='city_info'):
    city: int


class BasketValueCallbackFactory(CallbackData, prefix='basket_value'):
    pk: int


class AdminCityCallbackFactory(CallbackData, prefix='admin_city'):
    pk: int
