from aiogram import Dispatcher

from .help import register_help_handlers
from .profile import register_profile_handlers
from .log_water import register_log_water_handlers
from .log_food import register_log_food_handlers
from .log_workout import register_log_workout_handlers
from .check_progress import register_check_progress_handlers


def register_all_handlers(dp: Dispatcher):
    """
    Собираем и инициализируем воедино все хендлеры боты
    """
    register_help_handlers(dp)
    register_profile_handlers(dp)
    register_log_water_handlers(dp)
    register_log_food_handlers(dp)
    register_log_workout_handlers(dp)
    register_check_progress_handlers(dp)