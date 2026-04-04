import time, requests, random, config
from utils.anecdote import an
from utils.formatters import rub, cop,heart, min as format_min
import datetime as dt




# ------------------------------------таймер-------------------------------------
def my_timer(time_timer: str, format_timer: str) -> str:
    """
    Возвращает сообщение о запуске таймера (без ожидания).
    """
    from utils.formatters import min as format_min

    formatted_min = format_min(time_timer)

    if format_timer in config.MINUTE_FORMATS:
        seconds = int(time_timer) * 60
        return f"⏳ Таймер запущен на {time_timer} {formatted_min}. Я напомню через {seconds} секунд."

    elif format_timer in config.HOUR_FORMATS:
        seconds = int(time_timer) * 60 * 60
        return f"⏳ Таймер запущен на {time_timer} {format_timer}. Я напомню через {seconds} секунд."

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