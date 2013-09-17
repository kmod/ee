void setup() {
    pinMode(10, OUTPUT);
    pinMode(11, OUTPUT);
    pinMode(12, INPUT);
    pinMode(13, OUTPUT);

    Serial.begin(115200);

    digitalWrite(13, 1);
    delay(100);
    digitalWrite(13, 0);
}

int blocking_read() {
    while (Serial.available() == 0)
        delayMicroseconds(1);
    return Serial.read();
}

int shiftreg = 0;
void loop() {
    int cmd = blocking_read();

    int val, port;
    switch (cmd) {
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
