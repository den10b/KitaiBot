from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ButtonType
from django.db.models import Q
from database.models import MetalToBuy, CityInfo, Sales, Basket, MetalToSale, MetalToSalePrice, TgUser
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, ActionCallbackFactory, BackButtonCallbackFactory, \
    MetalSortCallbackFactory, ShopActionCallbackFactory, MetalCallbackFactory, FilterCallbackFactory, \
    NavigationCallbackFactory, CityInfoCallbackFactory, BasketValueCallbackFactory, ActualPricesCallbackFactory, \
    AdminCityCallbackFactory,MetalNdsCallbackFactory

main_menu_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Купить", callback_data=MainMenuCallbackFactory(type="buy").pack())
        ],
        [
            InlineKeyboardButton(text="Продать", callback_data=MainMenuCallbackFactory(type="sell").pack())
        ],
        [
            InlineKeyboardButton(text="Корзина", callback_data=MainMenuCallbackFactory(type="basket").pack())
        ],
        [
            InlineKeyboardButton(text="Контакты филиалов",
                                 callback_data=MainMenuCallbackFactory(type="contacts").pack())
        ],
        [
            InlineKeyboardButton(text="📋 Меню", callback_data=MainMenuCallbackFactory(type="menu").pack())
        ],
        [
            InlineKeyboardButton(text="Профиль", callback_data=MainMenuCallbackFactory(type="profile").pack())
        ],

    ]
)



async def back_button(to: str = "main_menu"):
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to=to))
    return inline_keyboard.as_markup()


async def review_action_buttons(action: str):
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(
        text="Пропустить" if action == "skip" else "Завершить",
        callback_data=ActionCallbackFactory(action=action)
    )
    inline_keyboard.adjust(1)
    inline_keyboard.button(text="Отмена", callback_data=BackButtonCallbackFactory(to="main_menu"))
    return inline_keyboard.as_markup()


async def metal_choice_buttons():
    inline_keyboard = InlineKeyboardBuilder()
    metals = list(dict.fromkeys((MetalToBuy.objects.all().values_list("name", flat=True)))) # Берем DISTINCT
    # значения, но оставляем исходный порядок
    for metal in metals:
        inline_keyboard.button(
            text=metal,
            callback_data=MetalCallbackFactory(metal=metal)
        )
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="main_menu"))
    inline_keyboard.adjust(*[2 for _ in range(len(metals) // 2)], 1, 1)
    return inline_keyboard.as_markup()

async def nds_choice_buttons():
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(
                text="НДС",
                callback_data=MetalNdsCallbackFactory(is_nds=True)
            )
    inline_keyboard.button(
                text="УНЛ",
                callback_data=MetalNdsCallbackFactory(is_nds=False)
    )

    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="metal_choice").pack())
    inline_keyboard.adjust(2)
    return inline_keyboard.as_markup()

async def sort_choice_buttons(metal: str):
    inline_keyboard = InlineKeyboardBuilder()
    isPrint = True
    for sort in MetalToBuy.objects.filter(name=metal).values_list("sort", flat=True).distinct():
        if not sort.__contains__("слиток"):
            inline_keyboard.button(
                text=sort,
                callback_data=MetalSortCallbackFactory(metal_sort=sort, sort_index=0)
            )
        elif isPrint:
            inline_keyboard.button(
                text="Слитки",
                callback_data=MetalSortCallbackFactory(metal_sort="Слиток", sort_index=0)
            )
            isPrint = False
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="nds_choice").pack())
    inline_keyboard.adjust(1)
    return inline_keyboard.as_markup()



async def metal_shop_action_buttons(current: int, amount: int):
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(
        text="Добавить в корзину",
        callback_data=ActionCallbackFactory(action="to_metal_amount")
    )
    if amount > 1:
        row_size = 0
        if current + 1 < amount:
            inline_keyboard.button(
                text="Следующий➡",
                callback_data=MetalSortCallbackFactory(metal_sort="Слиток", sort_index=current + 1)
            )
            row_size += 1

        if current > 0:
            inline_keyboard.button(
                text="️Предыдущий⬅️",
                callback_data=MetalSortCallbackFactory(metal_sort="Слиток", sort_index=current - 1)
            )
            row_size += 1
    else:
        row_size = 1
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="sort_choice").pack())
    inline_keyboard.adjust(1, row_size, 1)
    return inline_keyboard.as_markup()


async def metal_shop_check_buttons():
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(
        text="Подтвердить",
        callback_data=ActionCallbackFactory(action="add_to_cart")
    )
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="metal_page").pack())
    inline_keyboard.adjust(1)
    return inline_keyboard.as_markup()


async def size_filter_buttons(selected_filters: list[str] = None):
    inline_keyboard = InlineKeyboardBuilder()
    size_filters = ["1.00-1.49", "1.50-1.99", "2.00-2.99", "3.00-3.99", "5.00-5.99"]
    for s_filter in size_filters:
        prefix = ("✅" if s_filter in selected_filters else "") if selected_filters else ""
        inline_keyboard.button(text=prefix + s_filter,
                               callback_data=FilterCallbackFactory(filter_type="size", filter_description=s_filter))
    inline_keyboard.button(text="◀️ Назад", callback_data=MainMenuCallbackFactory(type="buy"))
    inline_keyboard.button(text="Подтвердить", callback_data=ActionCallbackFactory(action="complete"))
    inline_keyboard.adjust(*[1 for _ in size_filters], 2)
    return inline_keyboard.as_markup()


async def form_filter_buttons(selected_filters: list[str] = None):
    inline_keyboard = InlineKeyboardBuilder()
    form_filters = ["Круглый", "Кушон", "Маркиз", "Овал", "Груша"]
    for f_filter in form_filters:
        prefix = ("✅" if f_filter in selected_filters else "") if selected_filters else ""
        inline_keyboard.button(text=prefix + f_filter,
                               callback_data=FilterCallbackFactory(filter_type="form", filter_description=f_filter))
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="size_filters_menu"))
    inline_keyboard.button(text="Подтвердить", callback_data=ActionCallbackFactory(action="complete"))
    inline_keyboard.adjust(*[1 for _ in form_filters], 2)
    return inline_keyboard.as_markup()


async def def_filter_buttons(selected_filters: list[str] = None):
    inline_keyboard = InlineKeyboardBuilder()
    def_filters = ["VS1", "VVS1", "SI1", "SI2"]
    for d_filter in def_filters:
        prefix = ("✅" if d_filter in selected_filters else "") if selected_filters else ""
        inline_keyboard.button(text=prefix + d_filter,
                               callback_data=FilterCallbackFactory(filter_type="def", filter_description=d_filter))
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="form_filters_menu"))
    inline_keyboard.button(text="Подтвердить", callback_data=ActionCallbackFactory(action="complete"))
    inline_keyboard.adjust(*[1 for _ in def_filters], 2)
    return inline_keyboard.as_markup()


product_confirm_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Подтвердить заказ", callback_data=ActionCallbackFactory(action="confirm").pack())
        ],
        [
            InlineKeyboardButton(text="Отменить", callback_data=MainMenuCallbackFactory(type="buy").pack())
        ]
    ]
)


async def navigation_buttons(items_count: int, list_number: int = 1):
    inline_keyboard = InlineKeyboardBuilder()
    # inline_keyboard.button(
    #     text="Назад",
    #     callback_data=BackButtonCallbackFactory(to="def_gia_filters_menu")
    #     if list_number == 1 else NavigationCallbackFactory(navigation_type="previous", list_number=list_number)
    # )
    if list_number < items_count:
        inline_keyboard.button(
            text="Следующий➡️",
            callback_data=NavigationCallbackFactory(navigation_type="next", list_number=list_number)
        )
    elif list_number != 1:
        inline_keyboard.button(
            text="Предыдущий⬅️",
            callback_data=NavigationCallbackFactory(navigation_type="previous", list_number=list_number)
        )
    inline_keyboard.button(
        text="Добавить в корзину",
        callback_data=ActionCallbackFactory(action="add_to_backet")
    )
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="def_gia_filters_menu"))
    inline_keyboard.adjust(2 if items_count > 2 else 1, 1)
    return inline_keyboard.as_markup()


async def profile_buttons():
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(
        text='Изменить ФИО',
        callback_data=ActionCallbackFactory(action='change_name')
    )
    inline_keyboard.button(
        text='Изменить email',
        callback_data=ActionCallbackFactory(action='change_email')
    )
    inline_keyboard.button(
        text='◀️ Назад',
        callback_data=BackButtonCallbackFactory(to="main_menu")
    )
    inline_keyboard.adjust(1)
    return inline_keyboard.as_markup()


async def support_buttons():
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(
        text='FAQ',
        switch_inline_query_current_chat='FAQ '
    )
    inline_keyboard.button(
        text='Заказать обратный звонок',
        callback_data=ActionCallbackFactory(action='back_call')
    )
    inline_keyboard.button(
        text='Написать на почту',
        callback_data=ActionCallbackFactory(action='get_admin_email')
    )
    inline_keyboard.button(
        text='◀️ Назад',
        callback_data=BackButtonCallbackFactory(to='main_menu')
    )
    inline_keyboard.adjust(1)
    return inline_keyboard.as_markup()


async def support_confirmation():
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(
        text='Подтвердить',
        callback_data=ActionCallbackFactory(action='confirm')
    )
    inline_keyboard.button(
        text='◀️ Назад',
        callback_data=BackButtonCallbackFactory(to='support')
    )
    inline_keyboard.adjust(1)
    return inline_keyboard.as_markup()


async def city_info_buttons(back_to: str = 'menu',is_basket:bool=False):
    if is_basket:
        city_list = CityInfo.objects.filter(Q(city="Москва")|Q(city="Санкт-Петербруг"))
    else:
        city_list = CityInfo.objects.all()
    inline_keyboard = InlineKeyboardBuilder()
    for city in city_list:
        inline_keyboard.button(
            text=f'{city.city}',
            callback_data=CityInfoCallbackFactory(city=city.pk)
        )
    inline_keyboard.button(
        text='◀️ Назад',
        callback_data=BackButtonCallbackFactory(to=back_to)
    )
    inline_keyboard.adjust(*[2 for _ in range(city_list.count() // 2)], 1, 1)
    return inline_keyboard.as_markup()


async def basket_buttons(sale: Sales or None):
    inline_keyboard = InlineKeyboardBuilder()
    if sale:
        if Basket.objects.filter(sales_id=sale).count() > 0:
            inline_keyboard.button(
                text='Изменить',
                callback_data=ActionCallbackFactory(action='change_basket')
            )
            inline_keyboard.button(
                text='Оформить заказ',
                callback_data=ActionCallbackFactory(action='checkout')
            )
    inline_keyboard.button(
        text='◀️ Назад',
        callback_data=BackButtonCallbackFactory(to='menu')
    )
    inline_keyboard.adjust(1)
    return inline_keyboard.as_markup()


async def actual_city_choice_buttons():
    inline_keyboard = InlineKeyboardBuilder()
    cities = CityInfo.objects.filter(Q(city="Москва")|Q(city="Санкт-Петербруг")|Q(city="Кострома")).values_list("city", flat=True)
    for city in cities:
        inline_keyboard.button(
            text=city,
            callback_data=ActualPricesCallbackFactory(action=city)
        )
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="main_menu"))
    inline_keyboard.adjust(*[3 for _ in range(len(cities) // 3)], 1, 1)
    return inline_keyboard.as_markup()


async def actual_metal_choice_buttons(city: CityInfo):
    inline_keyboard = InlineKeyboardBuilder()
    for metal in MetalToSale.objects.filter(city_id=city).values_list("metal", flat=True):
        inline_keyboard.button(
            text=metal,
            callback_data=ActualPricesCallbackFactory(action=metal)
        )
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="city_choice"))
    inline_keyboard.adjust(2)
    return inline_keyboard.as_markup()


async def actual_proba_choice_buttons(metal: MetalToSale):
    inline_keyboard = InlineKeyboardBuilder()
    probes = MetalToSalePrice.objects.filter(metal_id=metal).values_list("proba", flat=True).distinct()
    for proba in probes:
        inline_keyboard.button(
            text=proba,
            callback_data=ActualPricesCallbackFactory(action=proba)
        )
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="metal_choice").pack())
    inline_keyboard.adjust(*[3 for _ in range(len(probes) // 3)], 1, 1)
    return inline_keyboard.as_markup()


async def actual_payment_choice_buttons(metal_object: MetalToSale):
    inline_keyboard = InlineKeyboardBuilder()
    if metal_object.cash_comment is not None:
        inline_keyboard.button(
            text=metal_object.cash_comment,
            callback_data=ActualPricesCallbackFactory(action="cash_price")
        )
    if metal_object.card_comment is not None:
        inline_keyboard.button(
            text=metal_object.card_comment,
            callback_data=ActualPricesCallbackFactory(action="card_price")
        )
    if metal_object.transfer_comment is not None:
        inline_keyboard.button(
            text=metal_object.transfer_comment,
            callback_data=ActualPricesCallbackFactory(action="transfer_price")
        )

    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="sort_choice").pack())
    inline_keyboard.adjust(1)
    return inline_keyboard.as_markup()


async def actual_price_page():
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(
        text="Связаться с менеджером",
        callback_data=ActualPricesCallbackFactory(action="call_manager")
    )
    inline_keyboard.button(text="Главное меню", callback_data=BackButtonCallbackFactory(to="main_menu"))
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="pay_choice").pack())
    inline_keyboard.adjust(1)
    return inline_keyboard.as_markup()


async def actual_manager_page():
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(text="Главное меню", callback_data=BackButtonCallbackFactory(to="main_menu"))
    inline_keyboard.button(text="◀️ Назад", callback_data=BackButtonCallbackFactory(to="price_page").pack())
    inline_keyboard.adjust(1)
    return inline_keyboard.as_markup()


async def basket_sale_buttons(sale: Sales, index: int = 1, count: int = 10):
    start_slice = (index - 1) * count
    end_slice = index * count
    basket = Basket.objects.filter(sales_id=sale)
    inline_keyboard = InlineKeyboardBuilder()
    for basket_value in basket[start_slice:end_slice]:
        if basket_value.metal_id:
            text = f'{basket_value.metal_id.name} | {basket_value.metal_id.sort}'
        else:
            text = f'{basket_value.gem_id.form} | {basket_value.gem_id.size} | {basket_value.gem_id.def_gia}'
        inline_keyboard.button(
            text=text,
            callback_data=BasketValueCallbackFactory(pk=basket_value.pk)
        )
    pages = basket.count() // count
    pages += 1 if basket.count() % count > 0 else 0
    pagination = 1

    if index == 1 and pages > 1:
        inline_keyboard.button(
            text='->',
            callback_data=ActionCallbackFactory(action='basket_next_page')
        )
    elif index > 1 and index != pages:
        pagination = 2
        inline_keyboard.button(
            text='<-',
            callback_data=ActionCallbackFactory(action='basket_prev_page')
        )
        inline_keyboard.button(
            text='->',
            callback_data=ActionCallbackFactory(action='basket_next_page')
        )
    elif index != 1 and index == pages:
        inline_keyboard.button(
            text='<-',
            callback_data=ActionCallbackFactory(action='basket_prev_page')
        )
    inline_keyboard.button(
        text='◀️ Назад',
        callback_data=BackButtonCallbackFactory(to='basket_main')
    )
    inline_keyboard.adjust(*[1 for _ in range(count)], pagination, 1)
    return inline_keyboard.as_markup()


async def basket_value_action():
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(text='Изменить кол-во',
                           callback_data=ActionCallbackFactory(action='change_amount'))
    inline_keyboard.button(text='Удалить',
                           callback_data=ActionCallbackFactory(action='delete_from_basket'))
    inline_keyboard.button(text='◀️ Назад',
                           callback_data=BackButtonCallbackFactory(to='basket_pagination'))
    inline_keyboard.adjust(1)
    return inline_keyboard.as_markup()


async def confirmation(back_to: str = 'support'):
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(
        text='Подтвердить',
        callback_data=ActionCallbackFactory(action='confirm')
    )
    inline_keyboard.button(
        text='◀️ Назад',
        callback_data=BackButtonCallbackFactory(to=back_to)
    )
    inline_keyboard.adjust(1)
    return inline_keyboard.as_markup()


admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Города", callback_data=MainMenuCallbackFactory(type="admin_city").pack())
        ],
    ]
)


async def admin_city(index: int = 1, count: int = 10):
    start_slice = (index - 1) * count
    end_slice = index * count
    city_list = CityInfo.objects.all()
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(text='Добавить город',
                           callback_data=ActionCallbackFactory(action='admin_city_add'))
    for city in city_list[start_slice:end_slice]:
        inline_keyboard.button(
            text=f'{city.city}',
            callback_data=AdminCityCallbackFactory(pk=city.pk)
        )
    pages = city_list.count() // count
    pages += 1 if city_list.count() % count > 0 else 0
    pagination = 1

    if index == 1 and pages > 1:
        inline_keyboard.button(
            text='⏩',
            callback_data=ActionCallbackFactory(action='admin_city_next')
        )
    elif index > 1 and index != pages:
        pagination = 2
        inline_keyboard.button(
            text='⏪',
            callback_data=ActionCallbackFactory(action='admin_city_prev')
        )
        inline_keyboard.button(
            text='⏩',
            callback_data=ActionCallbackFactory(action='admin_city_next')
        )
    elif index != 1 and index == pages:
        inline_keyboard.button(
            text='⏪',
            callback_data=ActionCallbackFactory(action='admin_city_prev')
        )
    inline_keyboard.button(
        text='◀️Назад',
        callback_data=BackButtonCallbackFactory(to='admin_menu')
    )
    inline_keyboard.adjust(1, *[1 for _ in range(count)], pagination, 1)
    return inline_keyboard.as_markup()


async def pass_or_back(to=''):
    key = InlineKeyboardBuilder()
    key.button(text='Пропустить',
               callback_data=ActionCallbackFactory(action='pass'))
    key.button(text='◀️Назад',
               callback_data=BackButtonCallbackFactory(to=to))
    key.adjust(1)
    return key.as_markup()


async def user_news(user: TgUser):
    key = InlineKeyboardBuilder()
    text = 'Отписаться от новостей' if user.news else 'Подписаться на новости'
    key.button(text=text, callback_data=ActionCallbackFactory(action='user_news'))
    key.button(text='◀️Назад',
               callback_data=BackButtonCallbackFactory(to='main_menu'))
    key.adjust(1)
    return key.as_markup()
