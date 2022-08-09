import calendar
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ButtonType
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery


# setting callback_data prefix and parts
class calendar_callback(CallbackData, prefix='simple_calendar'):
    act: str
    year :int
    month :int
    day :int

class SimpleCalendar:
    import locale
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    async def start_calendar(
        self,
        year: int = datetime.now().year,
        month: int = datetime.now().month
    ) -> InlineKeyboardMarkup:
        """
        Creates an inline keyboard with the provided year and month
        :param int year: Year to use in the calendar, if None the current year is used.
        :param int month: Month to use in the calendar, if None the current month is used.
        :return: Returns InlineKeyboardMarkup object with the calendar.
        """
        inline_kb = InlineKeyboardBuilder()
        # inline_kb = InlineKeyboardMarkup(row_width=7)
        ignore_callback = calendar_callback(act="IGNORE", year=year, month=month, day=0)  # for buttons with no answer
        # First row - Month and Year

        inline_kb.button(
            text="<<",
            callback_data=calendar_callback(act="PREV-YEAR", year=year, month=month, day=1)
        ),
        inline_kb.button(
            text=f'{calendar.month_name[month]} {str(year)}',
            callback_data=ignore_callback
        ),
        inline_kb.button(
            text=">>",
            callback_data=calendar_callback(act="NEXT-YEAR", year=year, month=month, day=1)
        )

        # Second row - Week Days

        for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
            inline_kb.button(text=day, callback_data=ignore_callback)

        # Calendar rows - Days of month
        month_calendar = calendar.monthcalendar(year, month)

        for week in month_calendar:
            for day in week:
                if(day == 0):
                    inline_kb.button(text=" ", callback_data=ignore_callback)
                    continue
                inline_kb.button(
                    text=str(day), callback_data=calendar_callback(act="DAY", year=year, month=month,day=day)
                )

        # Last row - Buttons

        inline_kb.button(
            text="<", callback_data=calendar_callback(act="PREV-MONTH", year=year, month=month, day=day)
        )
        inline_kb.button(text=" ", callback_data=ignore_callback)
        inline_kb.button(
            text=">", callback_data=calendar_callback(act="NEXT-MONTH", year=year, month=month, day=day)
        )
        match len(month_calendar):
            case 4:
                inline_kb.adjust(3, 7, 7, 7, 7, 7,  3)
            case 5:
                inline_kb.adjust(3, 7,7,7,7,7,7,3)
            case 6:
                inline_kb.adjust(3, 7,7,7,7,7,7,7,3)

        return inline_kb.as_markup()

    async def process_selection(self, query: CallbackQuery, data: CallbackData) -> tuple:
        """
        Process the callback_query. This method generates a new calendar if forward or
        backward is pressed. This method should be called inside a CallbackQueryHandler.
        :param query: callback_query, as provided by the CallbackQueryHandler
        :param data: callback_data, dictionary, set by calendar_callback
        :return: Returns a tuple (Boolean,datetime), indicating if a date is selected
                    and returning the date if so.
        """
        data=data.dict()
        return_data = (False, None)
        temp_date = datetime(int(data['year']), int(data['month']), 1)
        # processing empty buttons, answering with no action
        if data['act'] == "IGNORE":
            await query.answer(cache_time=60)
        # user picked a day button, return date
        if data['act'] == "DAY":
            await query.message.delete_reply_markup()   # removing inline keyboard
            return_data = True, datetime(int(data['year']), int(data['month']), int(data['day']))
        # user navigates to previous year, editing message with new calendar
        if data['act'] == "PREV-YEAR":
            prev_date = temp_date - timedelta(days=365)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next year, editing message with new calendar
        if data['act'] == "NEXT-YEAR":
            next_date = temp_date + timedelta(days=365)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        # user navigates to previous month, editing message with new calendar
        if data['act'] == "PREV-MONTH":
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next month, editing message with new calendar
        if data['act'] == "NEXT-MONTH":
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        # at some point user clicks DAY button, returning date
        return return_data
