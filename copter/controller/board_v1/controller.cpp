#include "Arduino.h"

// PB1
#define LED0 9
// PB0
#define LED1 8
// PD7
#define LED2 7
// PD6
#define LED3 6

// PD2
#define SS0 2
// PD5
#define SS1 5
// PD4
#define SS2 4
// PD3
#define SS3 3

// PB3
#define MOSI 11
// PB4
#define MISO 12
// PB5
#define SCK 13
#define SS 10
void setup() {
    pinMode(LED0, OUTPUT);
    pinMode(LED1, OUTPUT);
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);

    pinMode(SS0, OUTPUT);
    pinMode(SS1, OUTPUT);
    pinMode(SS2, OUTPUT);
    pinMode(SS2, OUTPUT);

    pinMode(MOSI, OUTPUT);
    pinMode(MISO, INPUT);
    pinMode(SCK, OUTPUT);

    // Activate the pullup on SS to make sure the SPI circuitry stays in master mode.
    // Alternatively, could set the pinMode to output
    pinMode(SS, INPUT);
    digitalWrite(SS, 1);

    SPCR = (1<<SPE) | (1<<MSTR) | (1<<SPR0) | (1<<CPHA);

    digitalWrite(SS1, 0);
    digitalWrite(LED3, 1);
    /*
    for (int i = 0; i < 64; i++) {
        SPDR = i;
        //while (!(SPSR & (1<<SPIF))) {
        while (!bitRead(SPSR, SPIF)) {
            digitalWrite(LED2, 1);
        }
        delay(100);
    }*/
    /*uint8_t c = SPDR;
    digitalWrite(LED0, (SPDR>>0)&1);
    digitalWrite(LED1, (SPDR>>1)&1);
    digitalWrite(LED2, (SPDR>>2)&1);
    digitalWrite(LED3, (SPDR>>3)&1);
    delay(2000);*/
    for (byte b = 180; b >= 80; b--) {
        SPDR = b;
        while (!bitRead(SPSR, SPIF));
        delay(200);
    }
    digitalWrite(SS1, 1);
    digitalWrite(LED3, 0);
    SPCR = 0;

    pinMode(MOSI, INPUT);
    pinMode(SCK, INPUT);
}

void loop() {
    digitalWrite(LED3, 0);
    digitalWrite(LED0, 1);
    delay(300);
    digitalWrite(LED0, 0);
    digitalWrite(LED1, 1);
    delay(300);
    digitalWrite(LED1, 0);
    digitalWrite(LED2, 1);
    delay(300);
    digitalWrite(LED2, 0);
    digitalWrite(LED3, 1);
    delay(300);
}
