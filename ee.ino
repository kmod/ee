void setup() {
    pinMode(10, OUTPUT);
    analogWrite(10, 50);
    pinMode(13, OUTPUT);
}

void loop() {
    delay(1400);
    digitalWrite(13, 1);
    delay(100);
    digitalWrite(13, 0);
}
