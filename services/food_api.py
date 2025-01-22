import requests

def get_food_kcal(product_name: str) -> float:
    """
    Получает примерную калорийность (ккал на 100 г) продукта по названию
    через OpenFoodFacts (очень приблизительно).
    Если ничего не найдено, возвращаем 0.
    """
    base_url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "action": "process",
        "search_terms": product_name,
        "json": True,
        "page_size": 1,
    }
    try:
        resp = requests.get(base_url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("products", [])
        if not products:
            return 0.0
        nutriments = products[0].get("nutriments", {})
        kcal_100g = nutriments.get("energy-kcal_100g", 0.0)
        return float(kcal_100g)
    except Exception as e:
        print(f"Ошибка при запросе калорийности: {e}")
        return 0.0