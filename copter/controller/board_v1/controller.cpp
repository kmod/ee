#include "Arduino.h"

// PB1
#define LED0 9
// PB0
#define LED1 8
// PD7
#define LED2 7
// PD6
#define LED3 6
void setup() {
    pinMode(LED0, OUTPUT);
    pinMode(LED1, OUTPUT);
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
}

void loop() {
    digitalWrite(LED3, 0);
    digitalWrite(LED0, 1);
    delay(300);
    digitalWrite(LED0, 0);
    digitalWrite(LED1, 1);
    delay(300);
    digitalWrite(LED1, 0);
    digitalWrite(LED2, 1);
    delay(300);
    digitalWrite(LED2, 0);
    digitalWrite(LED3, 1);
    delay(300);
}
