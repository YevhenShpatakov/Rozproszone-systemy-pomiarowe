# Uzupełnienie kontraktu MQTT — DHT22

Po dodaniu czujnika DHT22 urządzenie ESP32 publikuje dwa rodzaje pomiarów:

```text
lab/<group_id>/<device_id>/temperature
lab/<group_id>/<device_id>/humidity
```

Dla temperatury pole `sensor` ma wartość `temperature`, a pole `unit` ma wartość `C`.

Dla wilgotności pole `sensor` ma wartość `humidity`, a pole `unit` ma wartość `%`.

Struktura JSON pozostaje zgodna z kontraktem v1:

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
