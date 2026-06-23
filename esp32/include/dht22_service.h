#pragma once

#include <Arduino.h>

// Zmień ten pin, jeśli DATA z DHT22 masz podłączone do innego GPIO.
// Uwaga: DHT22 wymaga rezystora podciągającego 4.7k–10k między DATA i 3V3,
// jeśli moduł czujnika nie ma go już na płytce.
#ifndef DHT22_DATA_PIN
#define DHT22_DATA_PIN 4
#endif

struct Dht22Reading {
    float temperatureC;
    float humidityPercent;
    bool temperatureValid;
    bool humidityValid;
};

void dht22_init();
bool dht22_read(Dht22Reading &reading);
String dht22_last_error();
