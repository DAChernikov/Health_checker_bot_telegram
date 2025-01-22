from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from data.users_data import users
from services.plots import generate_progress_plot

async def cmd_check_progress(message: Message):
    """
    /check_progress
    Отправляет текстовый отчёт и график (png)
    """
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль через /set_profile.")
        return

    u = users[user_id]
    water_goal = u["water_goal"]
    logged_water = u["logged_water"]
    cal_goal = u["calorie_goal"]
    cal_logged = u["logged_calories"]
    cal_burned = u["burned_calories"]

    text = (f"<b>Ваш прогресс:</b>\n\n"
            f"💧 Вода:\n"
            f"Выпито: {logged_water} мл из {water_goal} мл.\n"
            f"Осталось: {max(0, water_goal - logged_water)} мл.\n\n"

            f"🍔 Калории:\n"
            f"Потреблено: {cal_logged:.1f} из {cal_goal} ккал.\n"
            f"Сожжено тренировками: {cal_burned:.1f} ккал.\n"
            f"Баланс (потреблено - сожжено): {(cal_logged - cal_burned):.1f} ккал.\n\n"
            f"Ниже — графики за сегодня:"
            )

    await message.answer(text)

    # Генерируем график
    plot_path = generate_progress_plot(u)
    # Отправляем картинку
    await message.answer_photo(photo=FSInputFile(plot_path))

def register_check_progress_handlers(dp: Dispatcher):
    dp.message.register(cmd_check_progress, Command(commands=["check_progress"]))