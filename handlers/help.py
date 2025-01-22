from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

async def cmd_help(message: Message):
    """
    /help – выводит список всех доступных команд.
    Вызываем также из /start, чтобы пользователь сразу видел.
    """
    text = (
        "<b>Список команд бота:</b>\n\n"
        "/start - Запуск бота (приветствие + help)\n"
        "/set_profile - Настройка профиля (вес, рост, возраст, город)\n"
        "/log_water [кол-во] - Записать выпитую воду\n"
        "/log_food [продукт] [грамм] - Записать потреблённую еду\n"
        "/log_workout [тип] [время] - Записать тренировку\n"
        "/check_progress - Посмотреть прогресс (вода, калории, графики)\n"
        "/help - Справка по командам\n\n"
        "При вводе команд без аргументов бот попросит уточнить недостающие данные.\n"
    )
    await message.answer(text)

def register_help_handlers(dp: Dispatcher):
    dp.message.register(cmd_help, Command(commands=["help"]))