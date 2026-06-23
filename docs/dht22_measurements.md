# DHT22 — rzeczywisty pomiar temperatury i wilgotności

## Cel zmiany

Wcześniejsza wersja firmware ESP32 publikowała stałą, symulowaną wartość temperatury `24.5`. W projekcie dodano obsługę czujnika DHT22, dzięki czemu ESP32 publikuje rzeczywiste pomiary:

- `temperature` — temperatura w stopniach Celsjusza,
- `humidity` — wilgotność względna w procentach.

## Pliki zmienione lub dodane

```text
esp32/include/dht22_service.h
esp32/src/dht22_service.cpp
esp32/src/main.cpp
esp32/platformio.ini
ingestor/ingestor.py
ui/config.py
ui/app.py
ui/README.md
docs/dht22_measurements.md
```

## Podłączenie DHT22

Przyjęty pin danych:

```text
DHT22 DATA -> GPIO4
```

Jeżeli czujnik jest podłączony do innego pinu, należy zmienić wartość w pliku:

```text
esp32/include/dht22_service.h
```

```cpp
#define DHT22_DATA_PIN 4
```

Typowe połączenie:

```text
DHT22 VCC  -> 3V3
DHT22 GND  -> GND
DHT22 DATA -> GPIO4
```

Jeżeli używany jest sam czujnik bez modułu, należy dodać rezystor podciągający 4.7k–10k między DATA i 3V3.

## Topic MQTT

Temperatura:

```text
lab/<group_id>/<device_id>/temperature
```

Wilgotność:

```text
lab/<group_id>/<device_id>/humidity
```

Przykład temperatury:

```json
{
  "schema_version": 1,
  "group_id": "g02",
  "device_id": "esp32-E8247EB865E4",
  "sensor": "temperature",
  "value": 23.8,
  "unit": "C",
  "ts_ms": 125000,
  "seq": 10
}
```

Przykład wilgotności:

```json
{
  "schema_version": 1,
  "group_id": "g02",
  "device_id": "esp32-E8247EB865E4",
  "sensor": "humidity",
  "value": 48.6,
  "unit": "%",
  "ts_ms": 125010,
  "seq": 11
}
```

## Baza danych i API

Nie trzeba zmieniać struktury tabeli `measurements`, ponieważ tabela ma uniwersalne pola `sensor`, `value` i `unit`. Dzięki temu temperatura i wilgotność są zapisywane w tej samej tabeli jako dwa typy pomiarów.

Endpoint historii działa dla obu sensorów:

```bash
curl -u student:student "http://localhost:5001/measurements/history?device_id=esp32-E8247EB865E4&sensor=temperature&limit=10"
curl -u student:student "http://localhost:5001/measurements/history?device_id=esp32-E8247EB865E4&sensor=humidity&limit=10"
```

## UI

W Python UI dodano wybór sensora z listy:

```text
temperature
humidity
```

Dzięki temu dashboard może pokazywać osobno historię temperatury i wilgotności.
