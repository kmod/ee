// Simple script that allows fairly complete -- if slow -- control
// of the ATmega over serial.
// I use it to test out new protocols and debug by hand.

void setup() {
    Serial.begin(500000);

    pinMode(2, OUTPUT);
    pinMode(3, OUTPUT);
    pinMode(4, OUTPUT);

    pinMode(6, OUTPUT);
    pinMode(7, OUTPUT);

    Serial.write(0xae);
}

void loop() {
    uint8_t data = Serial.read();

    if (data & (1<<4)) {
        return;
    }

    bitWrite(PORTD, 3, (data>>7)&1);
    bitWrite(PORTD, 2, (data>>6)&1);

    bitSet(PORTD, 4);
    delay(0);
    bitClear(PORTD, 4);
    delay(0);

    if (data & (1<<5)) {
        data = digitalRead(5);
        Serial.write((char)data);
    }
}

