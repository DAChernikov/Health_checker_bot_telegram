import os
import requests

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "YOUR_API_FROM_OpenWeatherMap_HERE")

def get_temperature(city_name: str) -> float:
    """
    Возвращает текущую температуру (°C) в указанном городе с помощью OpenWeatherMap API.
    Если произошла ошибка, возвращает None.
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric",
        "lang": "ru"
    }
    try:
        resp = requests.get(base_url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        temperature = data["main"]["temp"]
        return float(temperature)
    except Exception as e:
        print(f"Ошибка при запросе погоды: {e}")
        return None