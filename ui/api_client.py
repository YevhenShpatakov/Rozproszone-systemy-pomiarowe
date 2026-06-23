"""
Klient REST dla dashboardu Python/Streamlit.

Ten plik jest odpowiednikiem zestawu subVI REST z LabVIEW:
- rest_get_health.vi
- rest_get_devices.vi
- rest_get_latest.vi
- rest_get_history.vi

Funkcje nie zawierają logiki UI. Odpowiadają tylko za komunikację HTTP,
walidację statusów odpowiedzi i zwrócenie danych JSON.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import requests
from requests.auth import HTTPBasicAuth


class ApiClientError(Exception):
    """Błąd komunikacji z REST API."""


@dataclass
class ApiClient:
    base_url: str = "http://localhost:5001"
    username: str = ""
    password: str = ""
    timeout: float = 5.0

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

    @property
    def auth(self) -> Optional[HTTPBasicAuth]:
        if self.username and self.password:
            return HTTPBasicAuth(self.username, self.password)
        return None

    def _get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"

        try:
            response = requests.get(
                url,
                params=params,
                auth=self.auth,
                timeout=self.timeout,
            )
        except requests.exceptions.ConnectionError as exc:
            raise ApiClientError(
                f"Brak połączenia z API pod adresem {self.base_url}. "
                "Sprawdź, czy Docker Compose i kontener api są uruchomione."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise ApiClientError(
                f"Timeout połączenia z API po {self.timeout} s."
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise ApiClientError(f"Błąd zapytania HTTP: {exc}") from exc

        if response.status_code == 401:
            raise ApiClientError(
                "401 Unauthorized: brak poprawnych danych logowania. "
                "Po laboratorium 10 wpisz login i hasło Basic Auth."
            )

        if response.status_code == 404:
            raise ApiClientError(
                f"404 Not Found dla endpointu {path}. "
                "Sprawdź, czy endpoint istnieje w api/app.py."
            )

        if response.status_code >= 400:
            body_preview = response.text[:300]
            raise ApiClientError(
                f"HTTP {response.status_code}: {body_preview}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise ApiClientError(
                f"API zwróciło odpowiedź, która nie jest poprawnym JSON: "
                f"{response.text[:300]}"
            ) from exc

    def get_health(self) -> dict[str, Any]:
        return self._get("/health")

    def get_devices(self) -> list[str]:
        data = self._get("/devices")

        # Aktualny endpoint zwraca {"devices": ["esp32-..."]}.
        if isinstance(data, dict) and isinstance(data.get("devices"), list):
            return [str(device) for device in data["devices"]]

        # Wariant awaryjny, gdyby endpoint kiedyś zwracał listę obiektów:
        # [{"device_id": "esp32-..."}]
        if isinstance(data, list):
            devices: list[str] = []
            for item in data:
                if isinstance(item, dict) and "device_id" in item:
                    devices.append(str(item["device_id"]))
                else:
                    devices.append(str(item))
            return devices

        raise ApiClientError(f"Niepoprawny format odpowiedzi /devices: {data}")

    def get_latest(self) -> dict[str, Any]:
        return self._get("/measurements/latest")

    def get_measurements(self) -> list[dict[str, Any]]:
        data = self._get("/measurements")
        if isinstance(data, list):
            return data
        raise ApiClientError(f"Niepoprawny format odpowiedzi /measurements: {data}")

    def get_history(
        self,
        device_id: str | None = None,
        sensor: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": int(limit)}

        if device_id:
            params["device_id"] = device_id

        if sensor:
            params["sensor"] = sensor

        data = self._get("/measurements/history", params=params)

        if isinstance(data, list):
            return data

        raise ApiClientError(f"Niepoprawny format odpowiedzi /measurements/history: {data}")
