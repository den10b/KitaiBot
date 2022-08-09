import asyncio
import datetime

from aiogram import Router, F, types, exceptions
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from tgbot.filters.user_filter import IsRegistered
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, ActionCallbackFactory, BackButtonCallbackFactory
from tgbot.keyboards.inline import support_buttons, back_button, support_confirmation
from tgbot.config import Config
from tgbot.states.support_state import SupportState
from database.models import TgUser, BackCall, TgAdmin, FAQ
from tgbot.services.broadcaster import broadcast
from tgbot.services.simple_calendar import calendar_callback, SimpleCalendar
from tgbot.services.simple_clock import clock_callback, SimpleClock

support_router = Router()
support_router.message.filter(IsRegistered())
support_router.callback_query.filter(IsRegistered())


@support_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'support'), state=SupportState)
@support_router.callback_query(BackButtonCallbackFactory.filter(F.to == 'support'), state='*')
@support_router.callback_query(MainMenuCallbackFactory.filter(F.type == "support"), state='*')
async def support_main(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = 'Вы можете написать нам на почту, заказать обратный звонок или просмотреть частые вопросы и ответы на них:'
    key = await support_buttons()
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)


# support get admin email
@support_router.callback_query(ActionCallbackFactory.filter(F.action == 'get_admin_email'), state='*')
async def get_admin_email_call(call: types.CallbackQuery, config: Config):
    text = f'Для связи с администрацией, напишите на почту: \n<b>{config.misc.admin_email}</b>\n\n'
    key = await back_button('support')
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)


# support get back call
@support_router.callback_query(ActionCallbackFactory.filter(F.action == 'back_call'), state='*')
async def back_call_main(call: types.CallbackQuery, state: FSMContext):
    text = 'Укажите дату для обратного звонка: \n'
    try:
        await call.message.edit_text(text, reply_markup=await SimpleCalendar().start_calendar())
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=await SimpleCalendar().start_calendar())
    await state.set_state(SupportState.enter_date)


@support_router.callback_query(calendar_callback.filter())
@support_router.message(SupportState.enter_date)
async def entering_date(
        # message: types.Message
        call: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    is_date, date = await SimpleCalendar().process_selection(call, callback_data)
    now = datetime.datetime.now()
    if is_date:
        if date > now:
            await call.message.answer('Выберите время для обратной связи',
                                      reply_markup=await SimpleClock().start_clock())
            await state.set_state(SupportState.enter_time)
            await state.update_data({'date': date})
        else:
            msg = await call.answer('Указанная дата уже прошла!',show_alert=True)
            await back_call_main(call,state)


@support_router.callback_query(clock_callback.filter())
@support_router.message(SupportState.enter_time)
async def entering_time(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    is_time, time = await SimpleClock().process_selection(call, callback_data)
    if is_time:
        user_time = datetime.datetime.strptime(f"{time['hour']}:{time['minute']}", '%H:%M')
        data = await state.get_data()
        user_date: datetime.datetime = data.get('date')

        back_call_datetime = datetime.datetime(user_date.year, user_date.month, user_date.day,
                                               user_time.hour, user_time.minute)
        text = f'Вы хотите заказать обратный звонок на:\n' \
               f'<b>{datetime.datetime.strftime(back_call_datetime, "%d.%m.%Y %H:%M")}</b>\n\n' \
               f'Если все верно, жмите на кнопку <i>Подтвердить</i>'
        await call.message.answer(text, reply_markup=await support_confirmation())
        await state.set_state(SupportState.confirm)
        await state.set_data({'datetime': back_call_datetime})


@support_router.callback_query(ActionCallbackFactory.filter(F.action == 'confirm'), state=SupportState.confirm)
async def confirm_back_call(call: types.CallbackQuery, state: FSMContext, user: TgUser, bot):
    data = await state.get_data()
    back_call_datetime = data.get('datetime')
    text = 'Выбирайте: '
    key = await support_buttons()
    try:
        await call.message.edit_text(text, reply_markup=key)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text, reply_markup=key)
    await state.clear()
    await call.answer('Обратный звонок успешно заказан!', show_alert=True)
    if back_call_datetime >= datetime.datetime.now():
        BackCall.objects.create(user_id=user,
                                phone_number=user.phone_number,
                                datetime_call=back_call_datetime)
        admins = [admin.user_id.user_id for admin in TgAdmin.objects.all()]
        await broadcast(bot, admins,
                        'Новая заявка на обратный звонок!')


@support_router.inline_query(F.query.startswith('FAQ'), state='*')
async def faq_inline(query: types.InlineQuery):
    query_data = query.query.replace('FAQ ', '')

    data = FAQ.objects.filter(question__icontains=query_data)
    results = []
    if data.count() == 0:
        results.append(types.InlineQueryResultArticle(
            id=1,
            title=f'{query_data}',
            input_message_content=types.InputMessageContent(
                message_text=f'Ничего не нашел...'),
            description=f'Ничего не нашел...',

        ))
        return await query.answer(results)
    else:
        for answer in data:
            results.append(types.InlineQueryResultArticle(
                id=answer.pk,
                title=f'{answer.question}',
                input_message_content=types.InputMessageContent(
                    message_text=f'-{answer.question}\n-{answer.answer}'),
                description=f'{answer.answer}',

            ))

    await query.answer(results)
