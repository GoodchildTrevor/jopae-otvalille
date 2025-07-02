from python_scripts.config.consts import (
    HPA_TO_MMHG_COEFF,
    PRESSURE_ROUND_PRECISION,
    WIND_SECTOR_COUNT,
    WIND_SECTOR_DEG,
    SOLAR_FLARE_NO_EFFECT,
    SOLAR_FLARE_LOW_RISK,
    G_SCALE_NONE,
    G_SCALE_WEAK,
    G_SCALE_MODERATE,
    G_SCALE_STRONG,
    G_SCALE_POWERFUL
)


def hpa_to_mmhg(hpa: float) -> float:
    """Переводит давление из гектопаскалей в миллиметры ртутного столба."""
    return round(hpa * HPA_TO_MMHG_COEFF, PRESSURE_ROUND_PRECISION)


def wind_direction(deg: float) -> str:
    """
    Переводит градусы (0–360) в направление ветра по восьми секторам.
    Args:
        deg (float): направление ветра в градусах
    Returns:
        str: название направления (например, 'Северный')
    """
    directions = [
        "Северный", "Северо-восточный", "Восточный", "Юго-восточный",
        "Южный", "Юго-западный", "Западный", "Северо-западный"
    ]
    index = round(deg / WIND_SECTOR_DEG) % WIND_SECTOR_COUNT
    return directions[index]


def interpret_solar_flare_data(flux_value: str) -> str:
    """
    Интерпретирует прогноз солнечных вспышек по значению потока.
    Args:
        flux_value (str): значение потока в SFU
    Returns:
        str: текстовая интерпретация уровня риска
    """
    flux = int(flux_value)
    if flux < SOLAR_FLARE_NO_EFFECT:
        return "Влияние на здоровье нет"
    elif flux < SOLAR_FLARE_LOW_RISK:
        return "Риск влияния на самочувствие очень мал"
    else:
        return "Риск плохого самочувствия"


def interpret_geomagnetic_data(data: dict) -> str:
    """
    Интерпретирует уровень геомагнитной активности по шкале G.
    Args:
        data (dict): словарь с ключом 'G' и вложенным ключом 'Scale'
    Returns:
        str: текстовая интерпретация прогноза
    """
    scale = data['G']['Scale']

    if scale == G_SCALE_NONE:
        return "Магнитных бурь нет"
    elif scale == G_SCALE_WEAK:
        return "Ожидается слабая геомагнитная буря"
    elif scale == G_SCALE_MODERATE:
        return "Ожидается умеренная геомагнитная буря"
    elif scale == G_SCALE_STRONG:
        return "Ожидается сильная геомагнитная буря"
    elif scale in G_SCALE_POWERFUL:
        return "Ожидается мощная геомагнитная буря"
    else:
        return "Уровень геомагнитной активности неизвестен"
