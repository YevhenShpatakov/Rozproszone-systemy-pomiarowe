# Python UI — Rozproszone Systemy Pomiarowe

Ten folder zawiera interfejs użytkownika wykonany w Pythonie/Streamlit.

Dashboard pełni rolę klienta REST dla backendu Flask i funkcjonalnie zastępuje panel LabVIEW:
- sprawdza połączenie z API (`/health`),
- pobiera listę urządzeń (`/devices`),
- pobiera ostatni pomiar (`/measurements/latest`),
- pobiera historię pomiarów (`/measurements/history`),
- umożliwia filtrowanie po `device_id`, `sensor` i `limit`,
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
curl http://localhost:5001/devices
```

## Instalacja UI

Z poziomu głównego folderu projektu:

```bash
cd ui
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

W Git Bash aktywacja środowiska może wyglądać tak:

```bash
source .venv/Scripts/activate
```

## Uruchomienie

Z głównego folderu projektu:

```bash
streamlit run ui/app.py
```

Albo z folderu `ui`:

```bash
streamlit run app.py
```

Domyślny adres API:

```text
http://localhost:5001
```

## Basic Auth

Aktualna wersja API może działać bez logowania. Po wykonaniu laboratorium 10 dashboard obsługuje Basic Auth przez pola:

- `Username`
- `Password`

Jeżeli API zwróci `401 Unauthorized`, wpisz poprawny login i hasło w panelu bocznym.

## Struktura plików

```text
ui/
├── app.py
├── api_client.py
├── config.py
├── requirements.txt
└── README.md
```

## Ograniczenia

- Pole `ts_ms` może być czasem od startu ESP32 (`millis()`), więc wykres pokazuje dane głównie względem numeru próbki.
- UI jest alternatywnym klientem REST w Pythonie; instrukcja laboratoryjna formalnie opisuje wariant LabVIEW.
