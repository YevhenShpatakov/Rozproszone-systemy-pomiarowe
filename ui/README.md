# Python UI — Rozproszone Systemy Pomiarowe

Ten folder zawiera interfejs użytkownika wykonany w Pythonie/Streamlit.

Dashboard pełni rolę klienta REST dla backendu Flask i funkcjonalnie zastępuje panel LabVIEW:
- sprawdza połączenie z API (`/health`),
- pobiera listę urządzeń (`/devices`),
- pobiera ostatni pomiar (`/measurements/latest`),
- pobiera historię pomiarów (`/measurements/history`),
- umożliwia filtrowanie po `device_id`, `sensor` i `limit`,
- obsługuje sensory `temperature` oraz `humidity` publikowane przez DHT22,
- pokazuje dane liczbowo, tabelarycznie i na wykresie,
- obsługuje błędy połączenia, brak danych i odpowiedzi HTTP 401/404/500.

## Wymagania

Najpierw uruchom backend projektu:

```bash
docker compose up -d --build
docker compose ps
```

Sprawdź API:

```bash
curl http://localhost:5001/health
curl -u student:student http://localhost:5001/devices
```

## Uruchomienie UI

Z poziomu folderu `ui`:

```bash
source .venv/Scripts/activate
streamlit run app.py
```

Jeżeli środowisko nie istnieje:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
streamlit run app.py
```

## Basic Auth

Po wykonaniu laboratorium 10 dashboard obsługuje Basic Auth przez pola:

- `Username`
- `Password`

Domyślne dane testowe API:

```text
student / student
```

## Sensory

Po dodaniu czujnika DHT22 dashboard pozwala filtrować dane po:

- `temperature` — temperatura w °C,
- `humidity` — wilgotność względna w %.
