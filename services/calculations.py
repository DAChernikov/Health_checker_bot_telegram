def calc_water_goal(weight, activity_minutes, temperature=None):
    base_water = weight * 30
    extra_activity = 500 * (activity_minutes // 30)
    extra_heat = 0
    if temperature is not None and temperature > 25:
        extra_heat = 500
    return round(base_water + extra_activity + extra_heat)

def calc_calorie_goal(weight, height, age, activity_minutes, temperature=None):
    base_calories = 10 * weight + 6.25 * height - 5 * age

    if activity_minutes < 30:
        activity_add = 100
    elif activity_minutes < 60:
        activity_add = 200
    else:
        activity_add = 300

    temp_add = 0
    if temperature is not None and temperature > 25:
        temp_add = 200

    total = base_calories + activity_add + temp_add
    return round(total)