import asyncio

from aiogram import Dispatcher, Bot
import nest_asyncio
from loguru import logger

from tgbot.config import load_config

from tgbot import middlewares
from tgbot import handlers
from tgbot.middlewares.config_setter import ConfigSetter
from tgbot.services import broadcaster



nest_asyncio.apply()


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот успешно запущен!")


# @log.catch()
async def main():
    logger.add('logs/{time:DD-MM-YYYY}.log', level='INFO', encoding='utf-8', rotation="12:00", retention='7 days')
    config = load_config("tgbot/keks.env")

    main_dp = Dispatcher()
    logger.info('Регистрирую Middlewares.')
    main_dp.update.outer_middleware(ConfigSetter(config=config))
    middlewares.setup(main_dp)

    logger.info('Регистрирую Handlers.')
    handlers.setup(main_dp)

    logger.info('Запускаю бота.')

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    # start
    try:
        config.misc.scheduler.start()
        await bot.delete_webhook(drop_pending_updates=True)
        await on_startup(bot, config.tg_bot.admin_ids)
        await main_dp.start_polling(bot)
    finally:
        await bot.session.close()

    await bot.delete_webhook(drop_pending_updates=True)
    await main_dp.start_polling(bot)


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
