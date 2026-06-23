#include "dht22_service.h"
#include <DHT.h>
#include <math.h>

static DHT dht(DHT22_DATA_PIN, DHT22);
static String lastError = "";

void dht22_init() {
    dht.begin();
    lastError = "";
}

bool dht22_read(Dht22Reading &reading) {
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature(); // Celsius

    reading.temperatureC = temperature;
    reading.humidityPercent = humidity;
    reading.temperatureValid = !isnan(temperature);
    reading.humidityValid = !isnan(humidity);

    if (!reading.temperatureValid && !reading.humidityValid) {
        lastError = "DHT22 read failed: temperature and humidity are NaN";
        return false;
    }

    if (!reading.temperatureValid) {
        lastError = "DHT22 read failed: temperature is NaN";
        return false;
    }

    if (!reading.humidityValid) {
        lastError = "DHT22 read failed: humidity is NaN";
        return false;
    }

    lastError = "";
    return true;
}

String dht22_last_error() {
    return lastError;
}
