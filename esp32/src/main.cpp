#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "secrets.h"
#include "dht22_service.h"

WiFiClient espClient;
PubSubClient mqttClient(espClient);

String deviceId;
String statusTopicName;
uint32_t seqCounter = 0;

unsigned long lastWifiAttemptMs = 0;
unsigned long lastMqttAttemptMs = 0;
unsigned long lastMeasurementMs = 0;

const unsigned long WIFI_RETRY_MS = 5000;
const unsigned long MQTT_RETRY_MS = 3000;
const unsigned long MEASUREMENT_PERIOD_MS = 5000;

bool wifiWasConnected = false;
bool mqttWasConnected = false;

String generateDeviceIdFromEfuse() {
    uint64_t chipId = ESP.getEfuseMac();
    char id[32];

    snprintf(id, sizeof(id), "esp32-%04X%08X",
             (uint16_t)(chipId >> 32),
             (uint32_t)chipId);

    return String(id);
}

long long getTimestampMs() {
    // Wariant uproszczony zgodny z dotychczasowym projektem.
    // Jeżeli później zostanie dodane NTP, można tutaj zwrócić Unix epoch w ms.
    return (long long)millis();
}

String buildMeasurementTopic(const char* sensor) {
    return "lab/" + String(MQTT_GROUP) + "/" + deviceId + "/" + String(sensor);
}

String buildStatusTopic() {
    return "lab/" + String(MQTT_GROUP) + "/" + deviceId + "/status";
}

void publishStatus(const char* status) {
    if (!mqttClient.connected()) {
        return;
    }

    StaticJsonDocument<192> doc;
    doc["schema_version"] = 1;
    doc["group_id"] = MQTT_GROUP;
    doc["device_id"] = deviceId;
    doc["status"] = status;
    doc["ts_ms"] = getTimestampMs();

    char payload[192];
    serializeJson(doc, payload, sizeof(payload));

    // retained = true, żeby MQTT Explorer od razu widział ostatni znany status urządzenia
    mqttClient.publish(statusTopicName.c_str(), payload, true);

    Serial.print("Status publish: ");
    Serial.print(statusTopicName);
    Serial.print(" -> ");
    Serial.println(payload);
}

void startWiFi() {
    Serial.print("Laczenie z Wi-Fi: ");
    Serial.println(WIFI_SSID);

    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void connectWiFiIfNeeded() {
    if (WiFi.status() == WL_CONNECTED) {
        if (!wifiWasConnected) {
            wifiWasConnected = true;
            Serial.println("Wi-Fi connected");
            Serial.print("ESP32 IP: ");
            Serial.println(WiFi.localIP());
        }
        return;
    }

    if (wifiWasConnected) {
        wifiWasConnected = false;
        mqttWasConnected = false;
        Serial.println("Wi-Fi disconnected");
    }

    if (millis() - lastWifiAttemptMs < WIFI_RETRY_MS) {
        return;
    }

    lastWifiAttemptMs = millis();
    Serial.println("Wi-Fi disconnected. Trying reconnect...");

    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

bool connectMqttIfNeeded() {
    if (WiFi.status() != WL_CONNECTED) {
        return false;
    }

    if (mqttClient.connected()) {
        if (!mqttWasConnected) {
            mqttWasConnected = true;
            Serial.println("MQTT connected");
            publishStatus("online");
        }
        return true;
    }

    if (mqttWasConnected) {
        mqttWasConnected = false;
        Serial.println("MQTT disconnected");
    }

    if (millis() - lastMqttAttemptMs < MQTT_RETRY_MS) {
        return false;
    }

    lastMqttAttemptMs = millis();

    StaticJsonDocument<192> willDoc;
    willDoc["schema_version"] = 1;
    willDoc["group_id"] = MQTT_GROUP;
    willDoc["device_id"] = deviceId;
    willDoc["status"] = "offline";
    willDoc["ts_ms"] = getTimestampMs();

    char willPayload[192];
    serializeJson(willDoc, willPayload, sizeof(willPayload));

    Serial.print("Laczenie z MQTT: ");
    Serial.print(MQTT_HOST);
    Serial.print(":");
    Serial.println(MQTT_PORT);

    bool ok = mqttClient.connect(
        deviceId.c_str(),
        statusTopicName.c_str(),
        0,
        true,
        willPayload
    );

    if (ok) {
        mqttWasConnected = true;
        Serial.println("MQTT connected");
        publishStatus("online");
    } else {
        Serial.print("MQTT connect failed, rc=");
        Serial.println(mqttClient.state());
    }

    return ok;
}

void publishSensorMeasurement(const char* sensor, float value, const char* unit) {
    if (!mqttClient.connected()) {
        return;
    }

    StaticJsonDocument<256> doc;

    doc["schema_version"] = 1;
    doc["group_id"] = MQTT_GROUP;
    doc["device_id"] = deviceId;
    doc["sensor"] = sensor;
    doc["value"] = value;
    doc["unit"] = unit;
    doc["ts_ms"] = getTimestampMs();
    doc["seq"] = seqCounter++;

    char payload[256];
    serializeJson(doc, payload, sizeof(payload));

    String topicName = buildMeasurementTopic(sensor);
    bool ok = mqttClient.publish(topicName.c_str(), payload);

    if (ok) {
        Serial.print("Measurement publish: ");
        Serial.print(topicName);
        Serial.print(" -> ");
        Serial.println(payload);
    } else {
        Serial.print("Measurement publish failed for sensor: ");
        Serial.println(sensor);
    }
}

void publishMeasurements() {
    if (!mqttClient.connected()) {
        return;
    }

    Dht22Reading reading;
    bool ok = dht22_read(reading);

    if (!ok) {
        Serial.print("DHT22 error: ");
        Serial.println(dht22_last_error());
        publishStatus("sensor_error");
        return;
    }

    publishSensorMeasurement("temperature", reading.temperatureC, "C");
    publishSensorMeasurement("humidity", reading.humidityPercent, "%");
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    deviceId = generateDeviceIdFromEfuse();
    statusTopicName = buildStatusTopic();

    Serial.print("Device ID: ");
    Serial.println(deviceId);
    Serial.print("Temperature topic: ");
    Serial.println(buildMeasurementTopic("temperature"));
    Serial.print("Humidity topic: ");
    Serial.println(buildMeasurementTopic("humidity"));
    Serial.print("Status topic: ");
    Serial.println(statusTopicName);
    Serial.print("DHT22 DATA pin: GPIO");
    Serial.println(DHT22_DATA_PIN);

    dht22_init();
    mqttClient.setServer(MQTT_HOST, MQTT_PORT);
    startWiFi();
}

void loop() {
    connectWiFiIfNeeded();
    connectMqttIfNeeded();

    if (mqttClient.connected()) {
        mqttClient.loop();
    }

    if (millis() - lastMeasurementMs >= MEASUREMENT_PERIOD_MS) {
        lastMeasurementMs = millis();
        publishMeasurements();
    }
}
