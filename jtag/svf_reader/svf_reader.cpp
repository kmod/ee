// Simple sketch that is optimized to work with the JTAG svf_reader.py script,
// though really it just does SPI.

// To hookup:
// pin 2 is TDI (output)
// pin 3 is TMS (output)
// pin 4 is TCK (output)
// pin 5 is TDO (input)
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
    delay(100);
    bitClear(PORTD, 4);

    if (nibble & (1<<1)) {
        delay(0);
        uint8_t data = (PIND >> 5) & 1;
        Serial.write((char)data);
    }
    delay(100);
}

void loop() {
    uint8_t data = Serial.read();

    pulse(data >> 4);
    pulse(data & 0x0f);
}

