import config
from secrets import YANDEX_TOKEN
from models.yandex_smart_home import YandexSmartHome


# Создаём клиент один раз
yh = YandexSmartHome(YANDEX_TOKEN)


def control_yandex_device(device_id: str, action: str) -> str:
    """
    Отправляет команду в Яндекс.Умный дом.

    Args:
        device_id: Идентификатор устройства (из config.YANDEX_DEVICE_IDS).
        action: Действие — 'on' или 'off'.

    Returns:
        Сообщение об успехе или ошибке.
    """
    status, response = yh.control_device(device_id, action)
    if status == 200:
        result = "включено" if action == "on" else "выключено"
        return f"Устройство {result}"
    else:
        return f"Ошибка: {response}"


def control_device(device_name: str, action: str) -> str:
    """
    Управляет устройством умного дома по его имени.

    Args:
        device_name: Название устройства (ключ из config.YANDEX_DEVICE_IDS).
        action: Действие — "включи" или "выключи".

    Returns:
        Сообщение об успехе или ошибке.
    """
    device_id = config.YANDEX_DEVICE_IDS.get(device_name)
    if not device_id:
        return f"Устройство '{device_name}' не найдено в конфиге"

    cmd = "on" if action == "включи" else "off"
    return control_yandex_device(device_id, cmd)