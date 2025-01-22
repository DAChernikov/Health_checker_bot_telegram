import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def generate_progress_plot(user_data: dict) -> str:
    """
    Строит графики динамики воды и калорий за сегодня (или вообще за все время),
    сохраняет во временный PNG и возвращает путь к файлу.
    """

    # Извлекаем историю (list of dict: {"timestamp": dt, "type": "water"/"food"/"workout", ...})
    history = user_data.get("log_history", [])
    # Отфильтруем события за сегодня (по желанию)
    # Для простоты берем все события
    # (Можно сделать if event["timestamp"].date() == datetime.now().date(): ...)

    # Разделим события по типам
    water_points = []
    cals_consumed_points = []
    cals_burned_points = []

    cumulative_water = 0
    cumulative_cal_consumed = 0
    cumulative_cal_burned = 0

    # Будем хранить (time, cumulative_value)
    # time - в формате HH:MM (string) или datetime
    for e in sorted(history, key=lambda x: x["timestamp"]):
        t = e["timestamp"]
        time_str = t.strftime("%H:%M")
        etype = e["type"]

        if etype == "water":
            cumulative_water += e["amount"]  # мл
            water_points.append((time_str, cumulative_water))

        elif etype == "food":
            cumulative_cal_consumed += e["kcal"]
            cals_consumed_points.append((time_str, cumulative_cal_consumed))

        elif etype == "workout":
            cumulative_cal_burned += e["kcal"]
            cals_burned_points.append((time_str, cumulative_cal_burned))

    # Если нет данных - нарисуем пустой график
    if not water_points and not cals_consumed_points and not cals_burned_points:
        return draw_empty_plot()

    # Создадим figure и два subplot'а
    fig = plt.figure(figsize=(8, 6))
    ax1 = fig.add_subplot(2, 1, 1)  # верхний
    ax2 = fig.add_subplot(2, 1, 2)  # нижний

    # ------ График воды ------
    if water_points:
        times_w, values_w = zip(*water_points)
        ax1.plot(times_w, values_w, marker='o', label='Выпито воды (мл)')

    # Линия цели воды
    water_goal = user_data["water_goal"]
    ax1.axhline(water_goal, color='r', linestyle='--', label='Цель (Water Goal)')

    ax1.set_title("Динамика воды (ml)")
    ax1.set_xlabel("Время")
    ax1.set_ylabel("мл (cumulative)")
    ax1.legend()
    ax1.grid(True)

    # ------ График калорий ------
    # Хотим на одной диаграмме две линии: потреблено, сожжено
    # cals_consumed_points -> "consumed"
    if cals_consumed_points:
        times_c, vals_c = zip(*cals_consumed_points)
        ax2.plot(times_c, vals_c, marker='o', color='blue', label='Потреблено ккал')

    if cals_burned_points:
        times_b, vals_b = zip(*cals_burned_points)
        ax2.plot(times_b, vals_b, marker='x', color='green', label='Сожжено ккал')

    # Линия цели калорий
    cal_goal = user_data["calorie_goal"]
    ax2.axhline(cal_goal, color='r', linestyle='--', label='Цель (Cal Goal)')

    ax2.set_title("Динамика калорий")
    ax2.set_xlabel("Время")
    ax2.set_ylabel("ккал (cumulative)")
    ax2.legend()
    ax2.grid(True)

    # Сохраним в файл
    filename = f"progress_{datetime.now().strftime('%H%M%S')}.png"
    fig.tight_layout()

    fig.savefig(filename)
    plt.close(fig)

    return filename

def draw_empty_plot() -> str:
    """
    Если нет данных для графика, нарисуем заглушку.
    """
    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(1,1,1)
    ax.text(0.5, 0.5, "Нет данных для графиков", ha='center', va='center', fontsize=12)
    ax.axis('off')
    filename = f"progress_empty_{datetime.now().strftime('%H%M%S')}.png"
    fig.savefig(filename)
    plt.close(fig)
    return filename