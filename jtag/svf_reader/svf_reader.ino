// Simple script that allows fairly complete -- if slow -- control
// of the ATmega over serial.
// I use it to test out new protocols and debug by hand.

void setup() {
    Serial.begin(500000);

    pinMode(2, OUTPUT);
    pinMode(3, OUTPUT);
    pinMode(4, OUTPUT);
    pinMode(5, INPUT);

    pinMode(6, OUTPUT);
    pinMode(7, OUTPUT);

    Serial.write(0xae);
}

void pulse(int nibble) {
    if (nibble & 1)
        return;
    PORTD = (PORTD & ~0x0c) | (nibble & 0x0c);
    //bitWrite(PORTD, 3, (nibble>>3)&1);
    //bitWrite(PORTD, 2, (nibble>>2)&1);

    bitSet(PORTD, 4);
    bitClear(PORTD, 4);

    if (nibble & (1<<1)) {
        delay(0);
        uint8_t data = (PIND >> 5) & 1;
        Serial.write((char)data);
    }
}

void loop() {
    uint8_t data = Serial.read();

    pulse(data >> 4);
    pulse(data & 0x0f);
}

