from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# setting callback_data prefix and parts
class clock_callback(CallbackData, prefix='simple_clock'):
    act: str
    hour: int
    minute: int


class SimpleClock:

    async def start_clock(
            self,
            hour: int = 12,
            minute: int = 0
    ) -> InlineKeyboardMarkup:

        inline_kb = InlineKeyboardBuilder()

        ignore_callback = clock_callback(act="IGNORE", hour=hour, minute=minute)  # for buttons with no answer

        inline_kb.button(
            text="↑",
            callback_data=clock_callback(act="hour+", hour=hour, minute=minute)
        ),
        inline_kb.button(
            text="↑",
            callback_data=clock_callback(act="minute+", hour=hour, minute=minute)
        )
        if hour < 10:
            hour_text = f"0{str(hour)}"
        else:
            hour_text = f"{str(hour)}"
        inline_kb.button(
            text=hour_text,
            callback_data=ignore_callback
        ),
        if minute < 10:
            minute_text = f"0{str(minute)}"
        else:
            minute_text = f"{str(minute)}"
        inline_kb.button(
            text=minute_text,
            callback_data=ignore_callback
        ),
        inline_kb.button(
            text="↓",
            callback_data=clock_callback(act="hour-", hour=hour, minute=minute)
        ),
        inline_kb.button(
            text="↓",
            callback_data=clock_callback(act="minute-", hour=hour, minute=minute)
        )
        inline_kb.button(
            text="Выбрать",
            callback_data=clock_callback(act="confirm", hour=hour, minute=minute)
        )

        inline_kb.adjust(2, 2, 2, 1)

        return inline_kb.as_markup()

    async def process_selection(self, query: CallbackQuery, time: CallbackData) -> tuple:
        """
        Process the callback_query.
        """
        time = time.dict()
        return_time = (False, None)
        temp_time = {"hour": int(time['hour']),
                     "minute": int(time['minute'])}
        # processing empty buttons, answering with no action
        if time['act'] == "IGNORE":
            await query.answer(cache_time=60)

        if time['act'] == "hour+":
            next_hour = temp_time["hour"] + 1
            if next_hour < 24:
                await query.message.edit_reply_markup(await self.start_clock(next_hour, temp_time["minute"]))
            else:
                await query.answer(cache_time=60)
        if time['act'] == "hour-":
            prev_hour = temp_time["hour"] - 1
            if prev_hour >= 0:
                await query.message.edit_reply_markup(await self.start_clock(prev_hour, temp_time["minute"]))
            else:
                await query.answer(cache_time=60)
        if time['act'] == "minute+":
            next_minute = temp_time["minute"] + 5
            if next_minute < 60:
                await query.message.edit_reply_markup(await self.start_clock(temp_time["hour"], next_minute))
            else:
                await query.message.edit_reply_markup(await self.start_clock(temp_time["hour"] + 1, 00))
        if time['act'] == "minute-":
            prev_minute = temp_time["minute"] - 5
            if prev_minute >= 0:
                await query.message.edit_reply_markup(await self.start_clock(temp_time["hour"], prev_minute))
            else:
                await query.message.edit_reply_markup(await self.start_clock(temp_time["hour"] - 1, 55))
        if time['act'] == "confirm":
            await query.message.delete_reply_markup()
            return_time = True, temp_time
        return return_time
