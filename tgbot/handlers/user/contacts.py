from aiogram import Router, F, types
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from tgbot.filters.user_filter import IsRegistered
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, CityInfoCallbackFactory, BackButtonCallbackFactory
from tgbot.keyboards.inline import city_info_buttons, back_button
from database.models import CityInfo, CityPhoneNumbers, CityAddress
from tgbot.states.contacts import ContactsState


contacts_router = Router()
contacts_router.message.filter(IsRegistered())
contacts_router.callback_query.filter(IsRegistered())


@contacts_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'menu_contacts'), ContactsState.main)
@contacts_router.callback_query(MainMenuCallbackFactory.filter(F.type == 'contacts'), state='*')
async def menu_contacts(call: types.CallbackQuery, state: FSMContext):
    text = 'Выберите нужный вам город: '
    key = await city_info_buttons()
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
    await state.set_state(ContactsState.main)


@contacts_router.callback_query(CityInfoCallbackFactory.filter(), state=ContactsState.main)
async def city_info_call(call: types.CallbackQuery, callback_data: CityInfoCallbackFactory):
    city_id = callback_data.city
    city = CityInfo.objects.filter(pk=city_id).first()
    city_address = CityAddress.objects.filter(city_id=city)
    contacts = CityPhoneNumbers.objects.filter(city_info_id=city)
    text = f'Город:\n<b>{city.city}</b>\n\n'
    if city_address.count() > 0:
        text += 'Адрес:\n'
        for address in city_address:
            text += f'<b>{address.address}</b>\n\n'
    if contacts.count() > 0:
        text += '\nТелефон:\n'
        for contact in contacts:
            text += f'<b>{contact.phone_number} ({contact.comment})</b>\n'
    try:
        await call.message.edit_text(text, reply_markup=await back_button(to='menu_contacts'))
    except Exception as e:
        logger.warning(e)

