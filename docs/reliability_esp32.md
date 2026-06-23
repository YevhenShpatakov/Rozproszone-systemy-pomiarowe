# Laboratorium 9 – niezawodność ESP32

## 1. Cel zmian

W ramach laboratorium 9 rozbudowano firmware ESP32 o mechanizmy zwiększające niezawodność pracy urządzenia pomiarowego. Dodano monitorowanie połączenia Wi-Fi, reconnect Wi-Fi, monitorowanie połączenia MQTT, reconnect MQTT, osobny topic statusowy oraz mechanizm Last Will and Testament.

## 2. Zmodyfikowane pliki

Zmodyfikowano następujące pliki:

- `esp32/src/main.cpp` – główna logika reconnect Wi-Fi, reconnect MQTT, status topic i Last Will,
- `ingestor/ingestor.py` – ignorowanie komunikatów technicznych z topicu `/status`,
- `docs/reliability_esp32.md` – dokumentacja zmian i testów.

Plik `esp32/include/secrets.h` zawiera dane sieciowe i nie powinien być commitowany do repozytorium, jeżeli znajdują się w nim prawdziwe hasła.

## 3. Topic danych pomiarowych

Dane pomiarowe są publikowane na topicu:

```text
lab/<group_id>/<device_id>/temperature
```

Przykład:

```text
lab/g02/esp32-E8247EB865E4/temperature
```

Przykładowy payload:

```json
{
  "schema_version": 1,
  "group_id": "g02",
  "device_id": "esp32-E8247EB865E4",
  "sensor": "temperature",
  "value": 24.5,
  "unit": "C",
  "ts_ms": 123456,
  "seq": 10
}
```

## 4. Topic statusowy

Dodano osobny topic techniczny statusu urządzenia:

```text
lab/<group_id>/<device_id>/status
```

Przykład:

```text
lab/g02/esp32-E8247EB865E4/status
```

Przykładowy payload `online`:

```json
{
  "schema_version": 1,
  "group_id": "g02",
  "device_id": "esp32-E8247EB865E4",
  "status": "online",
  "ts_ms": 123456
}
```

Komunikat statusowy jest publikowany z flagą `retained`, dzięki czemu MQTT Explorer pokazuje ostatni znany stan urządzenia od razu po subskrypcji topicu.

## 5. Reconnect Wi-Fi

Firmware cyklicznie sprawdza stan Wi-Fi przez `WiFi.status()`. Jeżeli urządzenie nie jest połączone z siecią, wykonywana jest próba ponownego połączenia. Próby reconnect są ograniczone czasowo i wykonywane co `WIFI_RETRY_MS = 5000 ms`, aby nie blokować programu i nie wywoływać `WiFi.begin(...)` w każdej iteracji pętli.

Najważniejsza funkcja:

```cpp
void connectWiFiIfNeeded();
```

## 6. Reconnect MQTT

Firmware sprawdza stan klienta MQTT przez `mqttClient.connected()`. Próby reconnect MQTT wykonywane są tylko wtedy, gdy Wi-Fi jest aktywne. Próby są ograniczone czasowo i wykonywane co `MQTT_RETRY_MS = 3000 ms`.

Po poprawnym połączeniu z brokerem urządzenie publikuje status:

```text
online
```

Najważniejsza funkcja:

```cpp
bool connectMqttIfNeeded();
```

## 7. Last Will and Testament

Podczas łączenia z brokerem MQTT urządzenie deklaruje komunikat Last Will na topicu statusowym. Jeżeli ESP32 rozłączy się niepoprawnie, broker opublikuje komunikat:

```json
{
  "schema_version": 1,
  "group_id": "g02",
  "device_id": "esp32-E8247EB865E4",
  "status": "offline",
  "ts_ms": 123456
}
```

Dzięki temu można wykryć nagłe zniknięcie urządzenia, na przykład po odłączeniu zasilania lub zerwaniu połączenia.

## 8. Zmiana w ingestorze

Ingestor subskrybuje topic:

```text
lab/+/+/+
```

Oznacza to, że odbiera zarówno dane pomiarowe, jak i komunikaty statusowe. Ponieważ status nie zawiera pól `sensor` i `value`, dodano ignorowanie topiców kończących się na `/status`:

```python
if topic.endswith("/status"):
    print("Status message ignored:", topic, data)
    return
```

Dzięki temu status można obserwować w MQTT Explorer, ale nie jest zapisywany do tabeli `measurements`.

## 9. Testy awarii

### Test 1 – poprawny start systemu

1. Uruchomiono Docker Compose.
2. Uruchomiono ESP32.
3. W MQTT Explorer zasubskrybowano:

```text
lab/g02/+/+
```

Oczekiwany rezultat:

- pojawia się topic `/temperature` z danymi pomiarowymi,
- pojawia się topic `/status` ze statusem `online`,
- ingestor zapisuje dane pomiarowe do PostgreSQL,
- ingestor ignoruje komunikaty statusowe.

### Test 2 – zatrzymanie brokera MQTT

1. Zatrzymano brokera:

```bash
docker compose stop broker
```

2. ESP32 zgłasza w Serial Monitor błąd połączenia MQTT.
3. Urządzenie podejmuje cykliczne próby reconnect.

Po ponownym uruchomieniu brokera:

```bash
docker compose start broker
```

Oczekiwany rezultat:

- ESP32 ponownie łączy się z MQTT,
- publikuje status `online`,
- wraca do publikacji pomiarów.

### Test 3 – utrata zasilania ESP32

1. ESP32 jest połączone z brokerem.
2. Odłączono ESP32 od zasilania lub portu USB.
3. Broker publikuje Last Will na topicu `/status`.

Oczekiwany rezultat:

- w MQTT Explorer pojawia się status `offline`,
- po ponownym uruchomieniu ESP32 pojawia się status `online`.

## 10. Podsumowanie

Po zmianach ESP32 nie zatrzymuje działania programu przy chwilowej utracie Wi-Fi lub MQTT. Urządzenie cyklicznie próbuje odzyskać połączenie, publikuje status `online` po poprawnym reconnect oraz wykorzystuje Last Will and Testament do sygnalizacji stanu `offline` przy niepoprawnym rozłączeniu.
