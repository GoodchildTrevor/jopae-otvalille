from python_scripts.config.types import JopaeReport
from python_scripts.config.consts import PRESSURE_THRESHOLD
from python_scripts.etl import (
    get_weather_info,
    get_pollen_info,
    get_solar_flare_info,
    get_geomagnetic_info
)


def get_tg_jopae_message() -> str:
    """
    Формирует итоговое сообщение для Telegram с анализом погодных условий, пыльцы,
    солнечной и геомагнитной активности.
    Returns:
        str: текст сообщения
    """
    weather_data = get_weather_info()
    pollen_data = get_pollen_info()
    solar_flare_data = get_solar_flare_info()
    geomagnetic_data = get_geomagnetic_info()

    weather = weather_message(weather_data)
    pollen = pollen_message(pollen_data)
    solar = solar_flare_message(solar_flare_data)
    geomagnetic = geomagnetic_message(geomagnetic_data)

    jopae_list = [weather.jopae, pollen.jopae, solar.jopae, geomagnetic.jopae]
    reasons = []

    if weather.jopae:
        reasons.append("погоды")
    if pollen.jopae:
        reasons.append("пыльцы")
    if solar.jopae:
        reasons.append("солнечных вспышек")
    if geomagnetic.jopae:
        reasons.append("магнитных бурь")

    if all(jopae_list):
        message = "Сегодня будет тотальный отвал жопы. Можешь даже не вставать\n\n"
    elif any(jopae_list):
        message = f"Сегодня жопа отпадёт из-за {', '.join(reasons)}\n\n"
    else:
        message = "Сегодня жопа будет на месте\n\n"

    message += weather.report
    # message += pollen.report
    message += solar.report
    message += geomagnetic.report

    return message


def weather_message(data: dict | str) -> JopaeReport:
    """
    Анализирует погодные данные.
    Args: data (dict | str): данные от API или строка с ошибкой
    Returns: JopaeReport: структура с флагом отвала жопы и сообщением
    """
    if isinstance(data, dict):
        weather_main = data['main']
        feels_like = data['feels_like']
        pressure = data['pressure']
        wind = data['wind']
        jopae = pressure < PRESSURE_THRESHOLD
        report = f"За окном {weather_main}\nПо ощущениям {feels_like} градусов\n{wind}\nДавление {pressure} мм.рт.ст.\n"
    else:
        jopae = False
        report = data + "\n"
    return JopaeReport(jopae, report)


def pollen_message(data: dict | str) -> JopaeReport:
    """
    Анализирует уровень пыльцы и аллергенов.
    Args: data (dict | str): данные от API или строка с ошибкой
    Returns: JopaeReport: структура с флагом отвала жопы и сообщением
    """
    if isinstance(data, dict):
        risk_grass = data['risk_grass'] not in ["Low", "Moderate"]
        risk_tree = data['risk_tree'] not in ["Low", "Moderate"]
        risk_weed = data['risk_weed'] not in ["Low", "Moderate"]

        if any([risk_grass, risk_tree, risk_weed]):
            jopae = True
            report = ["Риск аллергии на "]
            if risk_grass:
                report.append(f"траву ({data['count_grass']}), ")
            if risk_tree:
                report.append(
                    f"деревья ({data['count_tree']}), в т.ч. берёза ({data['birch_count']}) и дуб ({data['oak_count']}), "
                )
            if risk_weed:
                report.append(f"сорняки ({data['count_weed']}), ")
        else:
            jopae = False
            report = ["Риска аллергии нет"]

        report = "".join(report).rstrip(", ") + "\n"
    else:
        jopae = False
        report = data + "\n"
    return JopaeReport(jopae, report)


def solar_flare_message(data: dict | str) -> JopaeReport:
    """
    Анализирует данные о солнечной активности.
    Args: data (dict | str): данные от API или строка с ошибкой
    Returns: JopaeReport: структура с флагом отвала жопы и сообщением
    """
    if isinstance(data, dict):
        flux_value = data['value']
        interpretation = data['interpretation']
        jopae = interpretation != "Влияние на здоровье нет"
        report = f"Вспышки на Солнце: {flux_value} SFU\n{interpretation} \n"
    else:
        jopae = False
        report = data + "\n"
    return JopaeReport(jopae, report)


def geomagnetic_message(data: dict | str) -> JopaeReport:
    """
    Анализирует данные о геомагнитной обстановке.
    Args: data (dict | str): данные от API или строка с ошибкой
    Returns:JopaeReport: структура с флагом отвала жопы и сообщением
    """
    if isinstance(data, dict):
        prediction = data['prediction']
        jopae = prediction != "Магнитных бурь нет"
        report = prediction + "\n"
    else:
        jopae = False
        report = data + "\n"
    return JopaeReport(jopae, report)
