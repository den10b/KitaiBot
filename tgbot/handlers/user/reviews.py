import asyncio

from aiogram import Router, F, types
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from tgbot.filters.user_filter import IsRegistered
from tgbot.keyboards.callback_factory import MainMenuCallbackFactory, ActionCallbackFactory
from tgbot.keyboards.inline import back_button, review_action_buttons, main_menu_buttons
from tgbot.states.reviews_state import ReviewsState
from database.models import TgUser, Review, ReviewData, TgAdmin
from tgbot.services.broadcaster import broadcast


reviews_router = Router()
reviews_router.message.filter(IsRegistered())
reviews_router.callback_query.filter(IsRegistered())


@reviews_router.callback_query(MainMenuCallbackFactory.filter(F.type == "reviews_ideas"), state='*')
async def create_review(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Если хотите оставить отзыв или предложить крутую идею для бота, "
                                 "напишите сообщение.",
                                 reply_markup=await back_button())
    await state.set_state(ReviewsState.get_review_text)


@reviews_router.message(ReviewsState.get_review_text, ContentTypesFilter(content_types=types.ContentType.TEXT))
async def get_review_text(message: types.Message, state: FSMContext):
    await message.answer("Прикрепите документ, если нужно",
                         reply_markup=await review_action_buttons(action="skip"))
    await state.update_data({"review_text": message.text})
    await state.set_state(ReviewsState.get_review_document)


@reviews_router.message(ReviewsState.get_review_document, ContentTypesFilter(content_types=types.ContentType.DOCUMENT))
async def get_review_document(message: types.Message, state: FSMContext):
    document_id = message.document.file_id
    data = await state.get_data()
    documents = data.get("documents", [])
    documents.append(document_id)
    await message.answer(
        "Добавьте еще документ либо жмите на кнопку!",
        reply_markup=await review_action_buttons(action="complete")
    )
    await state.update_data({"documents": documents})


@reviews_router.message(ReviewsState.get_review_document,
                        ContentTypesFilter(content_types=[types.ContentType.ANY]))
async def review_document_wrong_format(message: types.Message):
    await message.delete()
    msg = await message.answer('Неверный формат!\n'
                               'Отправляйте как документ!')
    await asyncio.sleep(2)
    await msg.delete()


@reviews_router.callback_query(
    ActionCallbackFactory.filter(F.action == "skip"),
    state=ReviewsState.get_review_document)
@reviews_router.callback_query(
    ActionCallbackFactory.filter(F.action == "complete"),
    state=ReviewsState.get_review_document)
async def validate_review(call: types.CallbackQuery, state: FSMContext, user: TgUser,
                          bot):
    data = await state.get_data()
    review_text: str = data.get('review_text')
    documents: list = data.get('documents', [])
    review: Review = Review.objects.create(user_id=user, text=review_text)
    for document_id in documents:
        ReviewData(review_id=review, file_id=document_id).save()
    text = 'Ваш отзыв(идея) успешно отправлен администрации.\n' \
           'Вы вернулись в главное меню!'
    try:
        await call.message.edit_text(text,
                                     reply_markup=main_menu_buttons)
    except Exception as e:
        logger.warning(e)
        await call.message.answer(text,
                                  reply_markup=main_menu_buttons)
    admins = [admin.user_id.user_id for admin in TgAdmin.objects.all()]
    await broadcast(bot, admins, 'Новый отзыв!')
    await state.clear()
