// Simple sketch that is optimized to work with the JTAG svf_reader.py script,
// though really it just does SPI.

// To hookup:
// pin A0 is TDI (output)
// pin A1 is TMS (output)
// pin A2 is TDO (input)
// pin A3 is TCK (output)
// pins 6 and 7 can be used for debug output [currently not enabled]
// make sure to do level shifting appropriately

// protocol:
// each message is a 4-bit packet, and there can be 0, 1, or 2 packets per byte.
// packet structure, MSB first:
// - TMS
// - TDI
// - get_tdo (whether or not to read the TDO line and send it back)
// - #enable (set to 1 to set to a noop packet, ex if you want to send just 1 packet in a byte)

#include "Arduino.h"

void setup() {
    Serial.begin(500000);

    pinMode(A0, OUTPUT);
    pinMode(A1, OUTPUT);
    pinMode(A2, INPUT);
    pinMode(A3, OUTPUT);

    pinMode(6, OUTPUT); // LED
    pinMode(7, OUTPUT); // LED

    //pinMode(2, OUTPUT); // to modboard
    //pinMode(3, OUTPUT); // to modboard
    //pinMode(4, OUTPUT); // to modboard
    //pinMode(5, OUTPUT); // to modboard
    //pinMode(8, OUTPUT); // to modboard

    Serial.write(0xae);
}

void pulse(int nibble) {
    if (nibble & 1)
        return;
    delayMicroseconds(100);
    PORTC = (PORTC & ~0x03) | ((nibble >> 2) & 0x03);

    delayMicroseconds(100);
    bitSet(PORTC, 3);
    delayMicroseconds(100);
    bitClear(PORTC, 3);

    delayMicroseconds(100);
    if (nibble & (1<<1)) {
        delay(0);
        uint8_t data = (PINC >> 2) & 1;
        Serial.write((char)data);
    }
    //delay(10);
}

void loop() {
    bitClear(PORTD, 7);
    while (Serial.available() == 0) {}
    uint8_t data = Serial.read();
    bitSet(PORTD, 7);

    pulse(data >> 4);
    pulse(data & 0x0f);

}


