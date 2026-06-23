"""
Konfiguracja dashboardu UI.

UI działa poza Dockerem jako klient REST. Domyślnie łączy się z Flask API
uruchomionym lokalnie na porcie 5001.
"""

import os

DEFAULT_API_URL = os.getenv("RSP_API_URL", "http://localhost:5001")
DEFAULT_SENSOR = os.getenv("RSP_DEFAULT_SENSOR", "temperature")
DEFAULT_LIMIT = int(os.getenv("RSP_DEFAULT_LIMIT", "20"))

# Po dodaniu DHT22 system publikuje dwa typy pomiarów.
AVAILABLE_SENSORS = ["temperature", "humidity"]

# Timeout pojedynczego zapytania HTTP w sekundach.
DEFAULT_TIMEOUT = float(os.getenv("RSP_API_TIMEOUT", "5"))

# Basic Auth jest opcjonalne na wcześniejszych etapach, a po laboratorium 10
# dashboard przekazuje login i hasło do API.
DEFAULT_USERNAME = os.getenv("RSP_API_USERNAME", "")
DEFAULT_PASSWORD = os.getenv("RSP_API_PASSWORD", "")
