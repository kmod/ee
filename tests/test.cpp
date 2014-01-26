#include "Arduino.h"

#define LED 7

void setup() {
    pinMode(LED, OUTPUT);
}

void loop() {
    digitalWrite(LED, 1);
    delay(500);
    digitalWrite(LED, 0);
    delay(500);
}
