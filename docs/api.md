# Dokumentacja REST API

## 1. Cel API

REST API umożliwia odczyt danych pomiarowych zapisanych w bazie PostgreSQL. Dane trafiają do bazy przez łańcuch:

ESP32 → MQTT broker → ingestor → PostgreSQL → REST API

API działa jako warstwa pośrednia między bazą danych a klientem, np. przeglądarką, `curl`, Postmanem albo LabVIEW.

Adres bazowy API:

```text
http://localhost:5001
```

---

## 2. Endpoint: health check

### Adres

```text
GET /health
```

### Pełny URL

```text
http://localhost:5001/health
```

### Przykładowe zapytanie

```bash
curl http://localhost:5001/health
```

### Przykładowa odpowiedź

```json
{
  "status": "ok"
}
```

### Opis

Endpoint służy do sprawdzenia, czy serwis Flask działa poprawnie.

---

## 3. Endpoint: lista pomiarów

### Adres

```text
GET /measurements
```

### Pełny URL

```text
http://localhost:5001/measurements
```

### Przykładowe zapytanie

```bash
curl http://localhost:5001/measurements
```

### Opis

Endpoint zwraca listę ostatnich pomiarów zapisanych w tabeli `measurements`.

Wyniki są sortowane malejąco po polu `id`, czyli najnowsze rekordy znajdują się na początku listy.

### Przykładowa odpowiedź

```json
[
  {
    "id": 393,
    "group_id": "g02",
    "device_id": "esp32-146FAB004F8C",
    "sensor": "temperature",
    "value": 24.5,
    "unit": "C",
    "ts_ms": 1148120,
    "seq": 209,
    "topic": "lab/g02/esp32-146FAB004F8C/temperature"
  }
]
```

---

## 4. Endpoint: ostatni pomiar

### Adres

```text
GET /measurements/latest
```

### Pełny URL

```text
http://localhost:5001/measurements/latest
```

### Przykładowe zapytanie

```bash
curl http://localhost:5001/measurements/latest
```

### Opis

Endpoint zwraca jeden najnowszy rekord z tabeli `measurements`.

### Przykładowa odpowiedź

```json
{
  "id": 396,
  "group_id": "g02",
  "device_id": "esp32-146FAB004F8C",
  "sensor": "temperature",
  "value": 24.5,
  "unit": "C",
  "ts_ms": 1163168,
  "seq": 212,
  "topic": "lab/g02/esp32-146FAB004F8C/temperature"
}
```

### Odpowiedź w przypadku braku danych

```json
{
  "message": "Brak danych"
}
```

---

## 5. Endpoint: historia pomiarów

### Adres

```text
GET /measurements/history
```

### Pełny URL z parametrami

```text
http://localhost:5001/measurements/history?device_id=esp32-146FAB004F8C&sensor=temperature&limit=5
```

### Przykładowe zapytanie

```bash
curl "http://localhost:5001/measurements/history?device_id=esp32-146FAB004F8C&sensor=temperature&limit=5"
```

### Obsługiwane parametry

| Parametr | Opis | Przykład |
|---|---|---|
| `device_id` | filtruje pomiary dla wybranego urządzenia | `esp32-146FAB004F8C` |
| `sensor` | filtruje pomiary według typu sensora | `temperature` |
| `limit` | ogranicza liczbę zwracanych rekordów | `5` |

### Opis

Endpoint zwraca historię pomiarów z możliwością filtrowania po `device_id`, `sensor` oraz `limit`.

Jeżeli parametr nie zostanie podany, zapytanie zwróci dane bez tego filtra. Domyślna wartość `limit` wynosi `20`.

### Przykładowa odpowiedź

```json
[
  {
    "id": 393,
    "group_id": "g02",
    "device_id": "esp32-146FAB004F8C",
    "sensor": "temperature",
    "value": 24.5,
    "unit": "C",
    "ts_ms": 1148120,
    "seq": 209,
    "topic": "lab/g02/esp32-146FAB004F8C/temperature"
  },
  {
    "id": 392,
    "group_id": "g02",
    "device_id": "esp32-146FAB004F8C",
    "sensor": "temperature",
    "value": 24.5,
    "unit": "C",
    "ts_ms": 1143106,
    "seq": 208,
    "topic": "lab/g02/esp32-146FAB004F8C/temperature"
  }
]
```

---

## 6. Struktura rekordu pomiarowego

Każdy rekord pomiarowy zwracany przez API zawiera następujące pola:

| Pole | Opis |
|---|---|
| `id` | identyfikator rekordu w bazie danych |
| `group_id` | identyfikator grupy laboratoryjnej |
| `device_id` | identyfikator urządzenia ESP32 |
| `sensor` | typ sensora lub rodzaju pomiaru |
| `value` | wartość pomiaru |
| `unit` | jednostka pomiarowa |
| `ts_ms` | znacznik czasu z urządzenia |
| `seq` | numer sekwencyjny wiadomości |
| `topic` | topic MQTT, z którego pochodzi wiadomość |

---

## 7. Testowanie API

Do testów użyto narzędzia `curl`.

### Sprawdzenie działania API

```bash
curl http://localhost:5001/health
```

### Pobranie listy pomiarów

```bash
curl http://localhost:5001/measurements
```

### Pobranie ostatniego pomiaru

```bash
curl http://localhost:5001/measurements/latest
```

### Pobranie historii z filtrowaniem

```bash
curl "http://localhost:5001/measurements/history?device_id=esp32-146FAB004F8C&sensor=temperature&limit=5"
```

---

## 8. Uwagi

W aktualnej wersji projektu pole `ts_ms` jest generowane po stronie ESP32 jako czas od startu urządzenia z użyciem funkcji `millis()`. Jest to wariant testowy. Docelowo pole `ts_ms` może zostać zastąpione czasem Unix epoch w milisekundach po synchronizacji czasu przez NTP.

API udostępnia wyłącznie endpointy typu `GET`, ponieważ zapis danych do bazy realizowany jest przez serwis `ingestor`, który odbiera wiadomości z brokera MQTT.

---

## 9. Podsumowanie

Przygotowane REST API umożliwia odczyt danych pomiarowych zapisanych w PostgreSQL. Zaimplementowano endpoint kontrolny `/health`, pobieranie listy pomiarów `/measurements`, pobieranie ostatniego pomiaru `/measurements/latest` oraz pobieranie historii z filtrowaniem `/measurements/history`.