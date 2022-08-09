import asyncio

from aiogram import Router, types, F
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from database.models import GemToBuy, Sales, Basket, TgUser
from tgbot.filters.user_filter import IsRegistered
from tgbot.keyboards.callback_factory import FilterCallbackFactory, BackButtonCallbackFactory, ActionCallbackFactory, \
    NavigationCallbackFactory, MainMenuCallbackFactory
from tgbot.keyboards.inline import size_filter_buttons, form_filter_buttons, navigation_buttons, main_menu_buttons, \
    def_filter_buttons, product_confirm_buttons
from tgbot.states.stones_shop_state import StonesShopState

stones_shop_router = Router()
stones_shop_router.message.filter(IsRegistered())
stones_shop_router.callback_query.filter(IsRegistered())


@stones_shop_router.callback_query(MainMenuCallbackFactory.filter(F.type == "buy_stone"))
async def start_shopping(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_size_filters: list = data.get("selected_size_filters", [])
    markup = await size_filter_buttons(selected_size_filters)
    await call.message.edit_text("Выберите размеры камней", reply_markup=markup)
    await state.set_state(StonesShopState.size_choice)


@stones_shop_router.callback_query(FilterCallbackFactory.filter(F.filter_type == "size"), StonesShopState.size_choice)
async def get_size_filter_choices(call: types.CallbackQuery, state: FSMContext, callback_data: FilterCallbackFactory):
    data = await state.get_data()
    selected_size_filters: list = data.get("selected_size_filters", [])
    if callback_data.filter_description in selected_size_filters:
        selected_size_filters.remove(callback_data.filter_description)
    else:
        selected_size_filters.append(callback_data.filter_description)
    markup = await size_filter_buttons(selected_size_filters)
    await call.message.edit_text("Выберите размеры камней", reply_markup=markup)
    await state.update_data({"selected_size_filters": selected_size_filters})


@stones_shop_router.callback_query(ActionCallbackFactory.filter(F.action == "complete"), StonesShopState.size_choice)
async def complete_size_filter_choice(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_form_filters: list = data.get("selected_form_filters", [])
    markup = await form_filter_buttons(selected_form_filters)
    await call.message.edit_text("Выберите формы камней", reply_markup=markup)
    await state.set_state(StonesShopState.form_choice)


@stones_shop_router.callback_query(FilterCallbackFactory.filter(F.filter_type == "form"), StonesShopState.form_choice)
async def get_form_filter_choices(call: types.CallbackQuery, state: FSMContext, callback_data: FilterCallbackFactory):
    data = await state.get_data()
    selected_form_filters: list = data.get("selected_form_filters", [])
    if callback_data.filter_description in selected_form_filters:
        selected_form_filters.remove(callback_data.filter_description)
    else:
        selected_form_filters.append(callback_data.filter_description)
    selected_form_filters.append(callback_data.filter_description)
    markup = await form_filter_buttons(selected_form_filters)
    await call.message.edit_text("Выберите формы", reply_markup=markup)
    await state.update_data({"selected_form_filters": selected_form_filters})


@stones_shop_router.callback_query(BackButtonCallbackFactory.filter(F.to == "size_filters_menu"),
                                   StonesShopState.form_choice)
async def back_form_filter_choice(call: types.CallbackQuery, state: FSMContext):
    await start_shopping(call, state)


@stones_shop_router.callback_query(ActionCallbackFactory.filter(F.action == "complete"), StonesShopState.form_choice)
async def complete_form_filter_choice(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_def_filters: list = data.get("selected_def_filters", [])
    markup = await def_filter_buttons(selected_def_filters)
    await call.message.edit_text("Выберите DEF камней", reply_markup=markup)
    await state.set_state(StonesShopState.def_choice)


@stones_shop_router.callback_query(FilterCallbackFactory.filter(F.filter_type == "def"), StonesShopState.def_choice)
async def get_def_filter_choices(call: types.CallbackQuery, state: FSMContext, callback_data: FilterCallbackFactory):
    data = await state.get_data()
    selected_def_filters: list = data.get("selected_def_filters", [])
    if callback_data.filter_description in selected_def_filters:
        selected_def_filters.remove(callback_data.filter_description)
    else:
        selected_def_filters.append(callback_data.filter_description)
    selected_def_filters.append(callback_data.filter_description)
    markup = await def_filter_buttons(selected_def_filters)
    await call.message.edit_text("Выберите DEF камней", reply_markup=markup)
    await state.update_data({"selected_def_filters": selected_def_filters})


@stones_shop_router.callback_query(BackButtonCallbackFactory.filter(F.to == "form_filters_menu"),
                                   StonesShopState.def_choice)
async def back_def_filter_choice(call: types.CallbackQuery, state: FSMContext):
    await complete_size_filter_choice(call, state)


async def get_stones(data: dict):
    size_filters = data.get('selected_size_filters', [])
    form_filters = data.get('selected_form_filters', [])
    def_filters = data.get('selected_def_filters', [])
    stones: list[GemToBuy] = GemToBuy.objects.all()

    return [stone for stone in stones if stone.form in (form_filters or [stone.form]) and stone.size in (size_filters or [stone.size]) and stone.def_gia in (def_filters or [stone.def_gia])]


@stones_shop_router.callback_query(ActionCallbackFactory.filter(F.action == "complete"), StonesShopState.def_choice)
async def complete_def_filter_choice(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    filtered_stones: list[GemToBuy] = await get_stones(data)
    await state.update_data({"list_number": 1})
    if filtered_stones:
        markup = await navigation_buttons(len(filtered_stones))
        caption = f"Форма: {filtered_stones[0].form}\n" \
                  f"Размер: {filtered_stones[0].size}\n" \
                  f"DEF: {filtered_stones[0].def_gia}\n\n" \
                  f"Цена: {filtered_stones[0].price}$\n"
        await call.message.delete()
        await call.message.answer_photo(photo=filtered_stones[0].image, caption=caption, reply_markup=markup)
        await state.set_state(StonesShopState.stone_choice)
    else:
        await call.answer("По ващему запросу ничего не найдено", show_alert=True)


@stones_shop_router.callback_query(BackButtonCallbackFactory.filter(F.to == "def_gia_filters_menu"),
                                   StonesShopState.stone_choice)
async def back_products_list(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    selected_def_filters: list = data.get("selected_def_filters", [])
    markup = await def_filter_buttons(selected_def_filters)
    await call.message.answer("Выберите DEF камней", reply_markup=markup)
    await state.set_state(StonesShopState.def_choice)


@stones_shop_router.callback_query(NavigationCallbackFactory.filter(F.navigation_type == "next"), StonesShopState.stone_choice)
async def navigate_to_next(call: types.CallbackQuery, state: FSMContext, callback_data: NavigationCallbackFactory):
    data = await state.get_data()
    filtered_stones: list[GemToBuy] = await get_stones(data)
    markup = await navigation_buttons(len(filtered_stones), callback_data.list_number + 1)
    caption = f"Форма: {filtered_stones[callback_data.list_number].form}\n" \
              f"Размер: {filtered_stones[callback_data.list_number].size}\n" \
              f"DEF: {filtered_stones[callback_data.list_number].def_gia}\n\n" \
              f"Цена: {filtered_stones[callback_data.list_number].price}$\n"
    await state.update_data({"list_number": callback_data.list_number + 1})
    await call.message.delete()
    await call.message.answer_photo(photo=filtered_stones[callback_data.list_number].image, caption=caption, reply_markup=markup)


@stones_shop_router.callback_query(NavigationCallbackFactory.filter(F.navigation_type == "previous"), StonesShopState.stone_choice)
async def navigate_to_previous(call: types.CallbackQuery, state: FSMContext, callback_data: NavigationCallbackFactory):
    data = await state.get_data()
    filtered_stones: list[GemToBuy] = await get_stones(data)
    caption = f"Форма: {filtered_stones[callback_data.list_number - 2].form}\n" \
              f"Размер: {filtered_stones[callback_data.list_number - 2].size}\n" \
              f"DEF: {filtered_stones[callback_data.list_number - 2].def_gia}\n\n" \
              f"Цена: {filtered_stones[callback_data.list_number - 2].price}$\n"
    markup = await navigation_buttons(len(filtered_stones), callback_data.list_number - 1)
    await state.update_data({"list_number": callback_data.list_number - 2})
    await call.message.delete()
    await call.message.answer_photo(photo=filtered_stones[callback_data.list_number - 2].image, caption=caption, reply_markup=markup)


@stones_shop_router.callback_query(ActionCallbackFactory.filter(F.action == "add_to_backet"), StonesShopState.stone_choice)
async def add_to_backet(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите количество товара:")
    await state.set_state(StonesShopState.amount_choice)


@stones_shop_router.message(StonesShopState.amount_choice, ContentTypesFilter(content_types=types.ContentType.TEXT))
async def stone_check(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        list_number = int(data["list_number"]) - 1
        amount = int(message.text)
        await state.update_data({"amount": amount})
        filtered_stones: list[GemToBuy] = await get_stones(data)
        text = f"Форма: {filtered_stones[list_number].form}\n" \
               f"Размер: {filtered_stones[list_number].size}\n" \
               f"DEF: {filtered_stones[list_number].def_gia}\n"\
               f"Количество: {amount}\n\n"\
               f"Цена: $ {amount*filtered_stones[list_number].price}\n"

        await message.answer_photo(photo=filtered_stones[list_number].image, caption=text, reply_markup=product_confirm_buttons)
        await state.set_state(StonesShopState.complete_shopping)
    except Exception as e:
        logger.warning(e)
        err_msg = await message.answer('Неверный формат!\n'
                                       'Отправляйте целое число!')
        await asyncio.sleep(2)
        await err_msg.delete()


@stones_shop_router.message(StonesShopState.amount_choice, ContentTypesFilter(content_types=[types.ContentType.ANY]))
async def amount_wrong(message: types.Message):
    await message.delete()
    msg = await message.answer('Неверный формат!\n'
                               'Отправляйте целое число!')
    await asyncio.sleep(2)
    await msg.delete()


@stones_shop_router.callback_query(StonesShopState.complete_shopping, ActionCallbackFactory.filter(F.action == "confirm"))
async def stone_to_cart(call: types.CallbackQuery, state: FSMContext, user: TgUser):
    current_sale, _ = Sales.objects.get_or_create(user_id=user, status=Sales.Status.NEW)
    data = await state.get_data()
    list_number = int(data["list_number"]) - 1
    stone = await get_stones(data)
    Basket(sales_id=current_sale, gem_id=stone[list_number], count=data.get("amount")).save()
    text = 'Товар успешно добавлен в корзину!\n' \
           'Выберите действие: '
    key = main_menu_buttons
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
