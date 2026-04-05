import time, requests, random, config
from utils.anecdote import an
from utils.formatters import rub, cop, heart, mesh, min as format_min
import datetime as dt


def calculation_materials(mat: str, text_input: str) -> str:
    """
    Рассчитывает материалы для стяжки или наливного пола на основе текстового ввода.

    Args:
        mat: Тип материала ("стяжку" или "наливной").
        text_input: Текст от пользователя, например "площадь 25 слой 5".

    Returns:
        Строка с результатом расчёта или сообщение об ошибке.
    """
    parts = text_input.lower().split(" ")

    # Ищем числа в тексте (поддержка разных форматов)
    numbers = []
    for part in parts:
        try:
            numbers.append(float(part))
        except ValueError:
            pass

    if len(numbers) < 2:
        return "❌ Не удалось распознать числа. Пример: площадь 25 слой 5"

    area = numbers[0]
    thickness = numbers[1]

    if area <= 0 or thickness <= 0:
        return "❌ Площадь и слой должны быть положительными числами."

    if mat not in config.MATERIALS:
        return f"❌ Материал '{mat}' не найден в базе данных"

    kf, kgm, price_m, price_r = map(int, config.MATERIALS[mat].split(", "))
    total_kg = thickness * kf * area / kgm
    total_cost_material = total_kg * price_m
    total_cost_work = area * price_r

    bags = mesh(int(total_kg))
    cost_material = rub(int(total_cost_material))
    cost_work = rub(int(total_cost_work))

    return (f"📊 **Результат расчёта:**\n\n"
            f"📦 Понадобится: {int(total_kg)} {bags}\n"
            f"💰 Материал: {int(total_cost_material)} {cost_material}\n"
            f"🔨 Работа: {int(total_cost_work)} {cost_work}")


# ------------------------------------таймер-------------------------------------
def my_timer(time_timer: str, format_timer: str) -> str:
    """
    Возвращает сообщение о запуске таймера (без ожидания).
    """
    formatted_min = format_min(time_timer)

    if format_timer in config.SECOND_FORMATS:
        return f"⏳ Таймер запущен на {time_timer} {format_timer}."

    elif format_timer in config.MINUTE_FORMATS:
        return f"⏳ Таймер запущен на {time_timer} {formatted_min}."

    elif format_timer in config.HOUR_FORMATS:
        return f"⏳ Таймер запущен на {time_timer} {format_timer}."

    return f"❌ Неизвестный формат времени: {format_timer}"


# ----------------------------------текущий день---------------------------------
def what_dey(city: int = config.UTC_OFFSET) -> str:
    """
    Возвращает текущую дату с учётом часового пояса.

    Args:
        city: Часовой сдвиг в часах относительно UTC (по умолчанию из config.UTC_OFFSET).

    Returns:
        Строка с датой в формате "сегодня ДД.ММ.ГГГГ".
    """
    city_day = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=city)
    return city_day.strftime("сегодня %d.%m.%Y")


# -------------------------------курс волют к рублю------------------------------
def currency(currency_name: str) -> str:
    """
    Возвращает текущий курс доллара или евро в рублях.

    Args:
        currency_name: "доллар" или "евро".

    Returns:
        Строка с курсом валюты или сообщение об ошибке.
    """
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        response.raise_for_status()
        data = response.json()
        usd_rate = data["Valute"]["USD"]["Value"]
        eur_rate = data["Valute"]["EUR"]["Value"]
    except requests.RequestException:
        return "Не удалось получить курс с сайта ЦБ"

    if currency_name in ("доллара", "доллар"):
        course = usd_rate
        rubles = int(course)
        cents = round((course - rubles) * 100)
        return f"курс доллара {rubles} {rub(rubles)} {cents} {cop(cents)}"

    if currency_name == "евро":
        course = eur_rate
        rubles = int(course)
        cents = round((course - rubles) * 100)
        return f"курс евро {rubles} {rub(rubles)} {cents} {cop(cents)}"

    return "Не удалось обработать запрос на курс валют"


# -----------------------------------анекдоты------------------------------------
def prank() -> str:
    """
    Возвращает случайный анекдот из anecdote.an.

    Returns:
        Строка с анекдотом или сообщение, что список пуст.
    """
    return random.choice(an) if an else "Список анекдотов пуст."


# ---------------------------------текущие время---------------------------------
def time_kem() -> str:
    """
    Возвращает текущее время в формате ЧЧ:ММ:СС.
    """
    return time.strftime("%H:%M:%S", time.localtime())


# ---------------------------------погода сегодня--------------------------------
def what_weather(city: str = config.DEFAULT_CITY) -> str:
    """
    Получает погоду для указанного города с сервиса wttr.in.

    Args:
        city: Название города (по умолчанию из config.DEFAULT_CITY).

    Returns:
        Строка с погодой или сообщение об ошибке.
    """
    url = f'http://wttr.in/{city}'

    weather_parameters = {
        'format': '%l: %t %C',  # город: температура + описание
        'M': '',                # скорость ветра в м/с
        'lang': 'ru',           # язык — русский
        'A': ''                 # отключить цвета (ANSI escape codes)
    }

    try:
        response = requests.get(url, params=weather_parameters, timeout=5)
        response.raise_for_status()
        response.encoding = 'utf-8'
        text = response.text.strip()
        return text
    except requests.ConnectionError:
        return "Сетевая ошибка"
    except requests.Timeout:
        return "Таймаут при запросе погоды"
    except requests.RequestException as e:
        return f"Ошибка при получении погоды: {str(e)}"


# ---------------------------Рисует сердце--------------------
def print_heart(amount: str) -> str:
    try:
        count = int(amount)
    except ValueError:
        return f"❌ Ошибка: '{amount}' не является числом"

    if count > 3:
        return f"⚠️ Слишком много сердечек ({count}). Максимум 3."

    heart_art = """
............* ...*
........*..lovel...*
.....*..lovelovelo...*
...*..lovelovelove....*
..*.lovelovelovelove...*................*....*
.*..lovelovelovelovelo...*.........*..lovel....*
*..lovelovelovelovelove...*......*..lovelovelo.*
*.. lovelovelovelovelove...*....*...lovelovelo.*
.*..lovelovelovelovelove...*..*...lovelovelo...*
..*...lovelovelovelovelove..*...lovelovelo...*
...*....lovelovelolovelovelovelovelovelo...*
.....*....lovelovelovelovelovelovelov...*
........*....lovelovelovelovelovelo...*
...........*....lovelovelovelove...*
...............*...lovelovelo....*
..................*..lovelo...*
.....................*.....*
......................*..*
.......................*
......................*
......................*
.......................*
.........................*.
...........................*
"""

    result = ""
    for _ in range(count):
        result += heart_art
        if _ != count - 1:
            result += "\n\n"

    return f"{result}\n✨ Нарисовано {count} {heart(count)}"