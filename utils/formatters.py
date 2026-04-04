from typing import Union

def _format(count: Union[int, str], one: str, few: str, many: str) -> str:
    """
    Базовая функция для склонения слов по правилам русского языка.

    Args:
        count: Число (целое или строка).
        one: Форма для 1 (например, "рубль").
        few: Форма для 2–4 (например, "рубля").
        many: Форма для 0, 5–20 (например, "рублей").

    Returns:
        Правильная форма слова в зависимости от числа.
    """
    count = int(count)

    # Исключение для чисел 11–19
    if 11 <= count <= 19:
        return many

    last_digit = int(str(count)[-1])
    if last_digit == 1:
        return one
    if 2 <= last_digit <= 4:
        return few
    return many


def mesh(count: int | str) -> str:
    """Возвращает правильную форму слова 'мешок' для числа count."""
    return _format(count, 'мешок', 'мешка', 'мешков')


def rub(count: int | str) -> str:
    """Возвращает правильную форму слова 'рубль' для числа count."""
    return _format(count, 'рубль', 'рубля', 'рублей')


def cop(count: int | str) -> str:
    """Возвращает правильную форму слова 'копейка' для числа count."""
    return _format(count, 'копейка', 'копейки', 'копеек')


def min(count: int | str) -> str:
    """Возвращает правильную форму слова 'минута' для числа count."""
    return _format(count, 'минута', 'минуты', 'минут')


def heart(count: int) -> str:
    """Возвращает правильную форму слова 'сердце' для числа count."""
    return _format(count, 'сердце', 'сердца', 'сердец')