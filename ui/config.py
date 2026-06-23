"""
Konfiguracja dashboardu UI.

UI działa poza Dockerem jako klient REST. Domyślnie łączy się z Flask API
uruchomionym lokalnie na porcie 5001.
"""

import os

DEFAULT_API_URL = os.getenv("RSP_API_URL", "http://localhost:5001")
DEFAULT_SENSOR = os.getenv("RSP_DEFAULT_SENSOR", "temperature")
DEFAULT_LIMIT = int(os.getenv("RSP_DEFAULT_LIMIT", "20"))

# Timeout pojedynczego zapytania HTTP w sekundach.
DEFAULT_TIMEOUT = float(os.getenv("RSP_API_TIMEOUT", "5"))

# Basic Auth jest opcjonalne. Aktualnie API może działać bez autoryzacji,
# ale po laboratorium 10 można włączyć pola login/hasło w panelu.
DEFAULT_USERNAME = os.getenv("RSP_API_USERNAME", "")
DEFAULT_PASSWORD = os.getenv("RSP_API_PASSWORD", "")
