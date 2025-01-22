from aiogram import Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime

from data.users_data import users
from services.food_api import get_food_kcal

class LogFoodStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_weight = State()

async def cmd_log_food(message: Message, command: CommandObject, state: FSMContext):
    """
    /log_food
    /log_food <продукт>
    /log_food <продукт> <граммы>
    """
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль через /set_profile.")
        return

    if not command.args:
        # Нет аргументов вообще
        await message.answer("Какой продукт вы съели? (пример: 'банан')")
        await state.set_state(LogFoodStates.waiting_for_name)
    else:
        # Есть аргументы -> парсим
        parts = command.args.split(maxsplit=1)
        if len(parts) == 1:
            # /log_food банан
            product_name = parts[0]
            await state.update_data(product_name=product_name)
            await message.answer(f"Вы выбрали продукт: {product_name}\nСколько грамм съели?")
            await state.set_state(LogFoodStates.waiting_for_weight)
        else:
            # /log_food банан 120
            product_name, weight_str = parts
            try:
                grams = float(weight_str.replace(",", "."))
            except ValueError:
                await message.answer("Неверный формат. Например: /log_food банан 120")
                return
            await handle_food_log(message, product_name, grams)

async def food_name_entered(message: Message, state: FSMContext):
    """
    Пользователь ввёл название продукта
    """
    product_name = message.text.strip()
    await state.update_data(product_name=product_name)
    await message.answer(f"Вы ввели продукт: {product_name}\nСколько грамм съели?")
    await state.set_state(LogFoodStates.waiting_for_weight)

async def food_weight_entered(message: Message, state: FSMContext):
    """
    Пользователь ввёл граммы
    """
    data = await state.get_data()
    product_name = data["product_name"]
    try:
        grams = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Пожалуйста, введите число (например 120).")
        return

    await handle_food_log(message, product_name, grams)
    await state.clear()

async def handle_food_log(message: Message, product_name: str, grams: float):
    user_id = message.from_user.id
    kcal_100g = get_food_kcal(product_name)
    consumed_kcal = (kcal_100g * grams) / 100.0

    users[user_id]["logged_calories"] += consumed_kcal
    users[user_id]["log_history"].append({
        "timestamp": datetime.now(),
        "type": "food",
        "product": product_name,
        "grams": grams,
        "kcal": consumed_kcal
    })

    total_cal = users[user_id]["logged_calories"]
    goal_cal = users[user_id]["calorie_goal"]

    await message.answer(
        f"Продукт: {product_name} ({kcal_100g} ккал/100г)\n"
        f"Вы съели: {grams} г → ~ {consumed_kcal:.1f} ккал.\n"
        f"Всего потреблено: {total_cal:.1f} / {goal_cal} ккал."
    )

def register_log_food_handlers(dp: Dispatcher):
    dp.message.register(cmd_log_food, Command(commands=["log_food"]))
    dp.message.register(food_name_entered, LogFoodStates.waiting_for_name)
    dp.message.register(food_weight_entered, LogFoodStates.waiting_for_weight)