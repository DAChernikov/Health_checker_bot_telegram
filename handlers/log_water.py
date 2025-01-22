from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from data.users_data import users
from datetime import datetime

class LogWaterStates(StatesGroup):
    waiting_for_amount = State()

async def cmd_log_water(message: Message, command: CommandObject, state: FSMContext):
    """
    /log_water (без аргументов) -> бот спрашивает "Сколько воды выпили?"
    /log_water <кол-во> -> сразу записывает
    """
    user_id = message.from_user.id

    if user_id not in users:
        await message.answer("Сначала настройте профиль через /set_profile.")
        return

    if not command.args:
        # Если нет аргументов, спрашиваем у пользователя "Сколько воды?"
        await message.answer("Сколько воды (мл) вы выпили?")
        await state.set_state(LogWaterStates.waiting_for_amount)
    else:
        # Если есть аргумент, пытаемся сразу сохранить
        try:
            amount = int(command.args)
        except ValueError:
            await message.answer("Неверный формат. Введите число, например: /log_water 250")
            return

        await log_water_and_reply(message, amount)

async def water_amount_entered(message: Message, state: FSMContext):
    """
    Пользователь ответил на вопрос "Сколько мл?"
    """
    user_id = message.from_user.id
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Неверный формат. Введите число, например 250.")
        return

    await log_water_and_reply(message, amount)
    await state.clear()

async def log_water_and_reply(message: Message, amount: int):
    user_id = message.from_user.id
    users[user_id]["logged_water"] += amount

    # Запишем событие в историю
    users[user_id]["log_history"].append({
        "timestamp": datetime.now(),
        "type": "water",
        "amount": amount  # мл
    })

    current = users[user_id]["logged_water"]
    goal = users[user_id]["water_goal"]

    text = (
        f"Записано: {amount} мл воды.\n"
        f"Всего выпито: {current} мл из {goal} мл."
    )
    if current >= goal:
        text += "\nПоздравляю! Вы выполнили дневную норму воды. 🏆"
    else:
        left = goal - current
        text += f"\nОсталось {left} мл до цели."

    await message.answer(text)

def register_log_water_handlers(dp: Dispatcher):
    dp.message.register(cmd_log_water, Command(commands=["log_water"]))
    dp.message.register(water_amount_entered, LogWaterStates.waiting_for_amount)