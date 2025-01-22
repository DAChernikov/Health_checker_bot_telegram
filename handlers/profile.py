from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Dispatcher

from data.users_data import users
# Импорт сервисов
from services.weather import get_temperature
from services.calculations import calc_water_goal, calc_calorie_goal

# Импортируем нашу команду help, чтобы вызвать её в /start:
from .help import cmd_help


class ProfileStatesGroup(StatesGroup):
    waiting_for_weight = State()
    waiting_for_height = State()
    waiting_for_age = State()
    waiting_for_activity = State()
    waiting_for_city = State()

async def cmd_start(message: Message):
    """
    /start – приветствие + сразу выдаём /help
    """
    await message.answer("Привет! Я бот для расчёта нормы воды и калорий.")
    # Сразу вызываем cmd_help, передав текущий message
    await cmd_help(message)

async def cmd_set_profile(message: Message, state: FSMContext):
    await message.answer("Введите ваш вес (в кг):")
    await state.set_state(ProfileStatesGroup.waiting_for_weight)

async def profile_weight_entered(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Пожалуйста, введите число, например 70 или 70.5")
        return

    await state.update_data(weight=weight)
    await message.answer("Введите ваш рост (в см):")
    await state.set_state(ProfileStatesGroup.waiting_for_height)

async def profile_height_entered(message: Message, state: FSMContext):
    try:
        height = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Пожалуйста, введите число (например 180).")
        return

    await state.update_data(height=height)
    await message.answer("Введите ваш возраст (полных лет):")
    await state.set_state(ProfileStatesGroup.waiting_for_age)

async def profile_age_entered(message: Message, state: FSMContext):
    try:
        age = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите целое число (например 25).")
        return

    await state.update_data(age=age)
    await message.answer("Сколько минут активности у вас в день?")
    await state.set_state(ProfileStatesGroup.waiting_for_activity)

async def profile_activity_entered(message: Message, state: FSMContext):
    try:
        activity = int(message.text)
    except ValueError:
        await message.answer("Введите целое число (например 30).")
        return

    await state.update_data(activity=activity)
    await message.answer("В каком городе вы находитесь?")
    await state.set_state(ProfileStatesGroup.waiting_for_city)

async def profile_city_entered(message: Message, state: FSMContext):
    city = message.text.strip()
    await state.update_data(city=city)

    user_data = await state.get_data()
    weight = user_data["weight"]
    height = user_data["height"]
    age = user_data["age"]
    activity = user_data["activity"]
    user_id = message.from_user.id

    # Получаем температуру
    temperature = get_temperature(city)

    # Считаем норму воды и калорий
    water_goal = calc_water_goal(weight, activity, temperature)
    calorie_goal = calc_calorie_goal(weight, height, age, activity, temperature)

    # Сохраняем профиль
    users[user_id] = {
        "weight": weight,
        "height": height,
        "age": age,
        "activity": activity,
        "city": city,
        "water_goal": water_goal,
        "calorie_goal": calorie_goal,
        "logged_water": 0,
        "logged_calories": 0,
        "burned_calories": 0,
        "log_history": []
    }

    text_profile = (
        f"Профиль настроен!\n"
        f"Вес: {weight} кг\n"
        f"Рост: {height} см\n"
        f"Возраст: {age} лет\n"
        f"Активность: {activity} мин/день\n"
        f"Город: {city}\n\n"
    )
    if temperature is not None:
        text_profile += f"Текущая температура: {temperature:.1f} °C\n"
    else:
        text_profile += f"Не удалось получить температуру для «{city}».\n"

    text_profile += (
        f"\nВаша дневная норма воды: {water_goal} мл\n"
        f"Ваша дневная норма калорий: {calorie_goal} ккал\n"
    )

    await message.answer(text_profile)
    await state.clear()

def register_profile_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_set_profile, Command(commands=["set_profile"]))

    dp.message.register(profile_weight_entered, ProfileStatesGroup.waiting_for_weight)
    dp.message.register(profile_height_entered, ProfileStatesGroup.waiting_for_height)
    dp.message.register(profile_age_entered, ProfileStatesGroup.waiting_for_age)
    dp.message.register(profile_activity_entered, ProfileStatesGroup.waiting_for_activity)
    dp.message.register(profile_city_entered, ProfileStatesGroup.waiting_for_city)