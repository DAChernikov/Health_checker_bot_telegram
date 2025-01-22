from aiogram import Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime

from data.users_data import users

class LogWorkoutStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_time = State()


async def cmd_log_workout(message: Message, command: CommandObject, state: FSMContext):
    """
    /log_workout
    /log_workout <тип>
    /log_workout <тип> <минуты>
    """
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль через /set_profile.")
        return

    if not command.args:
        # Вообще нет аргументов -> Выводим подсказку
        # Важно: экранируем < и > => &lt; / &gt;
        await message.answer(
            "Использование:\n"
            "<b>/log_workout &lt;тип&gt; &lt;время_мин&gt;</b>\n"
            "Например: <b>/log_workout бег 30</b>\n\n"
            "Либо введите <b>/log_workout &lt;тип&gt;</b> и бот спросит, сколько минут.\n"
            "Список доступных активностей: бег, ходьба, плавание, велопрогулка, тренажерный зал и т.п."
        )
        return
    else:
        parts = command.args.split(maxsplit=1)
        if len(parts) == 1:
            # /log_workout бег
            workout_type = parts[0]
            await state.update_data(workout_type=workout_type)
            await message.answer(
                f"Вы выбрали '{workout_type}'. Сколько минут занимались?"
            )
            await state.set_state(LogWorkoutStates.waiting_for_time)
        else:
            # /log_workout бег 30
            workout_type, minutes_str = parts
            try:
                minutes = float(minutes_str.replace(",", "."))
            except ValueError:
                await message.answer("Неверный формат. Пример: /log_workout бег 30")
                return
            await handle_workout_log(message, workout_type, minutes)

async def workout_time_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    workout_type = data["workout_type"]
    try:
        minutes = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Неверный формат. Укажите число (пример 30).")
        return

    await handle_workout_log(message, workout_type, minutes)
    await state.clear()


async def handle_workout_log(message: Message, workout_type: str, minutes: float):
    user_id = message.from_user.id

    # Условная логика
    if workout_type.lower() == "бег":
        cals_per_min = 10
    elif workout_type.lower() == "ходьба":
        cals_per_min = 5
    elif workout_type.lower() == "плавание":
        cals_per_min = 8
    else:
        cals_per_min = 7

    burned = cals_per_min * minutes
    users[user_id]["burned_calories"] += burned

    add_water = 200 * (minutes // 30)
    users[user_id]["water_goal"] += add_water

    from datetime import datetime
    users[user_id]["log_history"].append({
        "timestamp": datetime.now(),
        "type": "workout",
        "workout_type": workout_type,
        "minutes": minutes,
        "kcal": burned
    })

    await message.answer(
        f"Тренировка: {workout_type}, {minutes} мин.\n"
        f"Сожжено ~ {burned:.1f} ккал.\n"
        f"Итого сожжённых калорий: {users[user_id]['burned_calories']:.1f}.\n"
        + (f"Учтите, что норма воды увеличилась на {add_water} мл." if add_water else "")
    )


def register_log_workout_handlers(dp: Dispatcher):
    dp.message.register(cmd_log_workout, Command(commands=["log_workout"]))
    dp.message.register(workout_time_entered, LogWorkoutStates.waiting_for_time)
