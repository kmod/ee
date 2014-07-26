void setup() {
    pinMode(5, OUTPUT);
    pinMode(13, OUTPUT);
}

int led = 0;
void loop() {
    for (long i = 0; i < 2500; i++) {
        delayMicroseconds(10);
        digitalWrite(5, 0);
        delayMicroseconds(10);
        digitalWrite(5, 1);
    }
    led ^= 1;
    digitalWrite(13, led);
}
