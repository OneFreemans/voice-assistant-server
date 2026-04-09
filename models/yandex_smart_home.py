import requests
from typing import Optional, Any


class YandexSmartHome:
    """Клиент для управления Яндекс.Умным домом через API."""

    def __init__(self, token: str) -> None:
        """
        Инициализирует клиент с токеном авторизации.

        Args:
            token: OAuth-токен для доступа к API Яндекса.
        """
        self.token = token
        self.base_url = "https://api.iot.yandex.net/v1.0"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_devices(self) -> dict[str, Any]:
        """
        Получает список всех устройств и сценариев.

        Returns:
            Словарь с данными от API или словарь с ключом 'error'.
        """
        response = requests.get(f"{self.base_url}/user/info", headers=self.headers)
        if response.status_code == 200:
            try:
                return response.json()
            except requests.JSONDecodeError:
                return {"error": "Не JSON", "text": response.text}

        else:
            return {"error": f"HTTP {response.status_code}", "text": response.text}

    def control_device(self, device_id: str, action: str = "on", brightness: Optional[int] = None) -> tuple[int, dict[str, Any]]:
        """
        Управляет устройством (включение/выключение, изменение яркости).

        Args:
            device_id: Идентификатор устройства.
            action: Действие — 'on' или 'off'.
            brightness: Яркость (0–100) для устройств, поддерживающих регулировку.

        Returns:
            Кортеж (HTTP-статус, ответ API в виде словаря).
        """
        payload = {
            "devices": [{"id": device_id, "actions": []}]
        }

        # Команда включения/выключения
        if action in ("on", "off"):
            payload["devices"][0]["actions"].append({
                "type": "devices.capabilities.on_off",
                "state": {"instance": "on", "value": action == "on"}
            })

        # Яркость (если указана)
        if brightness is not None:
            payload["devices"][0]["actions"].append({
                "type": "devices.capabilities.range",
                "state": {"instance": "brightness", "value": brightness}
            })

        response = requests.post(
            f"{self.base_url}/devices/actions",
            headers=self.headers,
            json=payload
        )
        return response.status_code, response.json()

    def run_scenario(self, scenario_id: str) -> tuple[int, dict[str, Any]]:
        """
        Запускает сценарий умного дома.

        Args:
            scenario_id: Идентификатор сценария.

        Returns:
            Кортеж (HTTP-статус, ответ API в виде словаря).
        """
        response = requests.post(
            f"{self.base_url}/scenarios/{scenario_id}/actions",
            headers=self.headers,
            json={}
        )
        return response.status_code, response.json()