import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import register_all_handlers

BOT_TOKEN = os.getenv("BOT_TOKEN", "8020383973:AAFwjNHZWpI0IdG47N2Z6wbLWGOf3O61qR0")

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    register_all_handlers(dp)

    logging.info("Бот запускается... Нажмите Ctrl+C для остановки.")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())