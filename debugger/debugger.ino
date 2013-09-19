// Simple script that allows fairly complete -- if slow -- control
// of the ATmega over serial.
// I use it to test out new protocols and debug by hand.

void setup() {
    Serial.begin(500000);
}

char blocking_read() {
    while (Serial.available() == 0) {
        //delayMicroseconds(1);
    }
    return Serial.read();
}

int shiftreg = 0;
void loop() {
    char cmd = blocking_read();

    int val, port;
    if (cmd & 0x80) {
        port = cmd & 0x3f;
        val = (cmd >> 6) & 1;
        digitalWrite(port, val);
        return;
    }
    switch (cmd) {
        case 'm':
            port = blocking_read();
            val = blocking_read();
            pinMode(port, val);
            break;
        case 's':
            port = blocking_read();
            val = blocking_read();
            digitalWrite(port, val);
            break;
        case 'r':
            port = blocking_read();
            val = digitalRead(port);
            Serial.print((char)val);
            break;
        case 'i':
            port = blocking_read();
            shiftreg = ((shiftreg << 1) + digitalRead(port)) & 0xff;
            break;
        case 'v':
            Serial.print((char)shiftreg);
            break;
        default:
            Serial.print((char)cmd);
            break;
    }
}
