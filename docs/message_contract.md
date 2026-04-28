# Message Contract v1

## 1. Cel dokumentu
Dokument opisuje uzgodniony kontrakt danych dla komunikacji MQTT w projekcie rozproszonych systemów pomiarowych. Kontrakt definiuje strukturę topiców, format wiadomości JSON, pola wymagane i opcjonalne oraz podstawowe reguły walidacji.

## 2. Struktura topiców MQTT

Przyjęty schemat topiców:

`lab/<group_id>/<device_id>/<sensor>`

### Aktualnie używany przykład
`lab/g02/esp32-205EAB004F8C/temperature`

### Znaczenie segmentów
- `lab` - główny obszar projektu
- `group_id` - identyfikator grupy laboratoryjnej
- `device_id` - identyfikator urządzenia ESP32
- `sensor` - typ danych pomiarowych

### Zasady nazewnictwa
- używane są małe litery
- nie używa się spacji ani polskich znaków
- zachowana jest stała kolejność segmentów
- topic opisuje klasę komunikatu, a nie pojedynczą próbkę

## 3. Format wiadomości JSON v1

### Przykład wiadomości poprawnej
```json
{
  "schema_version": 1,
  "group_id": "g02",
  "device_id": "esp32-205EAB004F8C",
  "sensor": "temperature",
  "value": 24.5,
  "unit": "C",
  "ts_ms": 105975,
  "seq": 18
}
```

### Znaczenie pól
- `schema_version` - wersja kontraktu danych
- `group_id` - identyfikator grupy laboratoryjnej
- `device_id` - identyfikator urządzenia
- `sensor` - rodzaj sensora lub typu danych
- `value` - wartość pomiaru
- `unit` - jednostka fizyczna
- `ts_ms` - znacznik czasu pomiaru
- `seq` - numer sekwencyjny wiadomości

## 4. Pola wymagane

W wersji minimalnej wymagane są:
- `device_id`
- `sensor`
- `value`
- `ts_ms`

## 5. Pola opcjonalne / zalecane

Pola zalecane:
- `schema_version`
- `group_id`
- `unit`
- `seq`

## 6. Reguły walidacji

Przyjęto następujące podstawowe reguły walidacji:
- `device_id` musi być niepustym napisem
- `sensor` musi być napisem
- `value` musi być liczbą
- `ts_ms` musi być dodatnią liczbą całkowitą
- `unit`, jeśli występuje, musi odpowiadać typowi sensora
- `seq`, jeśli występuje, musi być liczbą całkowitą nieujemną

## 7. Informacja o znaczniku czasu

W aktualnej wersji testowej pole `ts_ms` jest generowane z wykorzystaniem `millis()`, czyli jako czas od startu urządzenia. Jest to wariant uproszczony używany na etapie testów.

Docelowo `ts_ms` powinno reprezentować czas Unix epoch w milisekundach po synchronizacji z NTP.

## 8. Przykłady wiadomości błędnych

### Błędny przykład 1 - brak `device_id`
```json
{
  "sensor": "temperature",
  "value": 24.5,
  "unit": "C",
  "ts_ms": 12345
}
```

### Błędny przykład 2 - `value` zapisane jako tekst
```json
{
  "device_id": "esp32-205EAB004F8C",
  "sensor": "temperature",
  "value": "24.5",
  "unit": "C",
  "ts_ms": 12345
}
```

### Błędny przykład 3 - brak `ts_ms`
```json
{
  "device_id": "esp32-205EAB004F8C",
  "sensor": "temperature",
  "value": 24.5,
  "unit": "C"
}
```

### Błędny przykład 4 - niepoprawny topic
`lab/g02/temperature`

## 9. Weryfikacja praktyczna

Weryfikację wykonano z użyciem MQTT Explorer. Sprawdzono:
- poprawność połączenia z brokerem MQTT
- poprawność nazwy topicu
- poprawność struktury JSON
- obecność publikowanych wiadomości w odpowiednim miejscu drzewa topiców

## 10. Podsumowanie

Przyjęty kontrakt danych zapewnia spójny sposób publikacji wiadomości pomiarowych z ESP32 do brokera MQTT. Uzgodniona struktura topicu i format JSON umożliwiają późniejszą walidację danych oraz integrację z ingestorem i bazą danych.