import os
from dotenv import load_dotenv

import json
import http.client
import requests

from python_scripts.config.endpoints import (
    AMBEE_URL,
    OPEN_WEATHER_URL,
    GEOMAGNETIC_URL,
    X_RAY_URL
)
from python_scripts.interpretations import (
    hpa_to_mmhg,
    wind_direction,
    interpret_solar_flare_data,
    interpret_geomagnetic_data
)

load_dotenv()

OPEN_WEATHER_API = os.getenv("OPEN_WEATHER")
AMBEE_API = os.getenv("AMBEE")
LAT = os.getenv("LAT")
LON = os.getenv("LON")

# Параметры запроса для OpenWeatherMap
params = {
    "lat": LAT,
    "lon": LON,
    "appid": OPEN_WEATHER_API,
    "exclude": "minutely,hourly,alerts",  # Исключаем ненужные секции
    "units": "metric",  # Градусы Цельсия
    "lang": "ru"        # Русский язык
}

# Заголовки для API Ambee
headers = {
    'x-api-key': AMBEE_API,
    'Content-type': "application/json"
}


def get_weather_info():
    """Получение текущей погоды от OpenWeatherMap."""
    data = dict()
    response = requests.get(OPEN_WEATHER_URL, params=params)
    if response.status_code == 200:
        weather = response.json()
        # Распаковка нужных данных
        main = weather['weather'][0]['description']
        direction = wind_direction(weather['wind']['deg'])  # Направление ветра
        speed = weather['wind']['speed']
        feels_like = weather['main']['feels_like']
        pressure = hpa_to_mmhg(weather['main']['pressure'])
        # Сохраняем информацию
        data['main'] = main
        data['feels_like'] = feels_like
        data['pressure'] = pressure
        data['wind'] = f"{direction} ветер, {speed} м/с"

        return data
    else:
        return f"Ошибка: {response.status_code}"


def get_pollen_info():
    """Получение данных о пыльце от Ambee."""
    conn = http.client.HTTPSConnection("api.ambeedata.com")
    url = AMBEE_URL.format(lat=LAT, lon=LON)
    data = dict()

    try:
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()

        if res.status != 200:
            return f"Ошибка: сервер вернул код {res.status} - {res.reason}"

        response = res.read().decode("utf-8")
        pollen_data = json.loads(response)['data'][0]

        # Сохраняем уровни риска и концентрации по типам пыльцы
        data["risk_grass"] = pollen_data["Risk"]["grass_pollen"]
        data["risk_tree"] = pollen_data["Risk"]["tree_pollen"]
        data["risk_weed"] = pollen_data["Risk"]["weed_pollen"]

        data["count_grass"] = pollen_data["Count"]["grass_pollen"]
        data["count_tree"] = pollen_data["Count"]["tree_pollen"]
        data["count_weed"] = pollen_data["Count"]["weed_pollen"]

        data["birch_count"] = pollen_data["Species"]["Tree"]["Birch"]
        data["oak_count"] = pollen_data["Species"]["Tree"]["Oak"]

        return data

    except Exception as e:
        return f"Ошибка при запросе данных: {e}"

    finally:
        conn.close()


def get_solar_flare_info():
    """Получение и интерпретация данных о солнечных вспышках."""
    try:
        response = requests.get(X_RAY_URL)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Ошибка запроса: {e}"

    x_ray = response.json()
    rows = x_ray[1:]  # Пропускаем заголовок
    latest_record = rows[-1]  # Последняя запись — самая свежая
    flux_value = latest_record[1]
    interpretation = interpret_solar_flare_data(flux_value)

    return {
        'value': flux_value,
        'interpretation': interpretation
    }


def get_geomagnetic_info():
    """Получение прогноза геомагнитной активности."""
    try:
        response = requests.get(GEOMAGNETIC_URL)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Ошибка запроса: {e}"
    geomagnetic_data = response.json()["1"]
    return {
        'prediction': interpret_geomagnetic_data(geomagnetic_data)
    }
