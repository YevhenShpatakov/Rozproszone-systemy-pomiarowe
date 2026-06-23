# Dokumentacja Python UI

## 1. Cel interfejsu

Interfejs użytkownika został przygotowany jako klient REST dla systemu rozproszonych pomiarów. Aplikacja działa poza Dockerem i komunikuje się z backendem Flask przez HTTP.

UI realizuje tę samą funkcjonalność, która w instrukcji laboratoryjnej została przewidziana dla panelu LabVIEW:

- weryfikacja połączenia z REST API,
- pobranie listy urządzeń,
- pobranie ostatniego pomiaru,
- pobranie historii pomiarów,
- filtrowanie po `device_id`, `sensor` i `limit`,
- prezentacja danych liczbowo, tabelarycznie i graficznie,
- obsługa błędów połączenia, braku danych i niepoprawnej odpowiedzi API.


## 2. Lokalizacja plików

```text
ui/
├── app.py
├── api_client.py
├── config.py
├── requirements.txt
└── README.md
```

## 3. Użyte endpointy REST

Adres bazowy API:

```text
http://localhost:5001
```

Dashboard korzysta z endpointów:

```text
GET /health
GET /devices
GET /measurements/latest
GET /measurements
GET /measurements/history?device_id=...&sensor=...&limit=...
```

## 4. Opis plików

### `ui/app.py`

Główny plik aplikacji Streamlit. Odpowiada za:

- budowę panelu użytkownika,
- obsługę przycisków,
- wybór urządzenia, sensora i limitu,
- prezentację ostatniego pomiaru,
- prezentację historii w tabeli,
- prezentację historii na wykresie,
- obsługę komunikatów diagnostycznych.

### `ui/api_client.py`

Moduł komunikacji REST. Zawiera klasę `ApiClient`, która odpowiada za zapytania HTTP do Flask API.

Najważniejsze funkcje:

```text
get_health()
get_devices()
get_latest()
get_measurements()
get_history(device_id, sensor, limit)
```

Ten plik oddziela logikę komunikacji REST od logiki interfejsu użytkownika.

### `ui/config.py`

Plik z domyślną konfiguracją:

```text
DEFAULT_API_URL = http://localhost:5001
DEFAULT_SENSOR = temperature
DEFAULT_LIMIT = 20
DEFAULT_TIMEOUT = 5
```

Konfigurację można nadpisać zmiennymi środowiskowymi.

### `ui/requirements.txt`

Lista bibliotek wymaganych do uruchomienia UI:

```text
streamlit
requests
pandas
```

### `ui/README.md`

Krótka instrukcja uruchomienia interfejsu.

## 5. Instrukcja uruchomienia

Najpierw należy uruchomić backend:

```bash
docker compose up -d --build
docker compose ps
```

Sprawdzenie API:

```bash
curl http://localhost:5001/health
curl http://localhost:5001/devices
```

Instalacja zależności UI:

```bash
cd ui
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Uruchomienie dashboardu:

```bash
streamlit run app.py
```

Po uruchomieniu Streamlit otworzy aplikację w przeglądarce.

## 6. Funkcjonalność UI

Panel boczny zawiera:

- adres API,
- timeout HTTP,
- pola loginu i hasła dla Basic Auth,
- przycisk testu `/health`,
- przycisk odświeżenia listy urządzeń `/devices`,
- opcję automatycznego odświeżania historii.

Panel główny zawiera:

- wybór `device_id`,
- wybór `sensor`,
- wybór `limit`,
- przycisk pobrania ostatniego pomiaru globalnego,
- przycisk pobrania ostatniego pomiaru dla wybranego urządzenia,
- przycisk pobrania historii,
- zakładkę z ostatnim pomiarem,
- zakładkę z historią i wykresem,
- zakładkę diagnostyczną.

## 7. Obsługa błędów

Aplikacja obsługuje między innymi:

- brak połączenia z API,
- timeout zapytania,
- odpowiedź `401 Unauthorized`,
- odpowiedź `404 Not Found`,
- błędy serwera HTTP,
- brak danych dla wybranego filtra,
- niepoprawny JSON.

## 8. Basic Auth

Po wykonaniu laboratorium 10 endpointy z danymi mogą wymagać Basic Auth. Dashboard ma przygotowane pola:

- `Username`,
- `Password`.

Dane te są przekazywane do zapytań HTTP przez `requests` jako Basic Auth. Endpoint `/health` może pozostać publiczny.

## 9. Ograniczenia

- Aktualny backend zwraca `/measurements/latest` jako ostatni pomiar globalny. Dlatego UI ma dodatkowy przycisk „Pobierz latest dla urządzenia”, który wykorzystuje `/measurements/history` z `limit=1`.
- Jeżeli `ts_ms` pochodzi z `millis()` ESP32, nie jest to rzeczywisty czas zegarowy, tylko czas od startu urządzenia.
- UI jest wykonany w Pythonie/Streamlit jako alternatywna implementacja panelu operatorskiego. Formalna instrukcja laboratoryjna odnosi się do LabVIEW, dlatego ewentualną zamianę narzędzia warto uzgodnić z prowadzącym.

## 10. Test praktyczny

Przed uruchomieniem UI warto wykonać:

```bash
curl http://localhost:5001/health
curl http://localhost:5001/devices
curl http://localhost:5001/measurements/latest
curl "http://localhost:5001/measurements/history?device_id=esp32-E8247EB865E4&sensor=temperature&limit=5"
```

Jeżeli powyższe komendy zwracają JSON, dashboard powinien działać poprawnie.
