from aiogram.dispatcher.fsm.state import StatesGroup, State


class ReviewsState(StatesGroup):
    get_review_text = State()
    get_review_document = State()
