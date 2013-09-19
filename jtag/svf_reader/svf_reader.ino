// Simple script that allows fairly complete -- if slow -- control
// of the ATmega over serial.
// I use it to test out new protocols and debug by hand.

void setup() {
    Serial.begin(500000);

    pinMode(2, OUTPUT);
    pinMode(3, OUTPUT);
    pinMode(4, OUTPUT);

    Serial.write(0xae);
}

char blocking_read() {
    while (Serial.available() == 0) {
    }
    return Serial.read();
}

int shiftreg = 0;
void loop() {
    while (Serial.available() == 0) {
    }
    uint8_t data = Serial.read();

    bitWrite(PORTD, 3, (data>>7)&1);
    bitWrite(PORTD, 2, (data>>6)&1);
    delay(0);

    bitWrite(PORTD, 4, 1);
    delay(0);
    bitWrite(PORTD, 4, 0);
    delay(0);

    if (data & (1<<5)) {
        data = digitalRead(5);
        Serial.write((char)data);
    }
}

