#include "Arduino.h"

void setup() {
    pinMode(13, OUTPUT);
    pinMode(3, OUTPUT);
    pinMode(A0, OUTPUT);

    digitalWrite(3, 1);
    digitalWrite(A0, 1);
    digitalWrite(13, 1);
}
void loop() {
}
