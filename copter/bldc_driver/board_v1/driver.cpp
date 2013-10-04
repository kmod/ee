#include "Arduino.h"
#define PWM 3

#define UL A3
#define UH A0

#define SM 2
#define SL 6
#define SH 7
#define S SM
#define M0 4
#define M1 5
#define U_MUX 0
#define V_MUX 1
#define W_MUX 2

#define REVERSE
#ifdef REVERSE
#define VL A4
#define VH A1
#define WL A5
#define WH A2
#else
#define VL A5
#define VH A2
#define WL A4
#define WH A1
#endif

#define LED 13

// Only use Serial in DEBUG mode, mostly because it bloats the binary size
//#define DEBUG
#ifndef DEBUG
#define Serial #error
#endif

void setup() {
#ifdef DEBUG
    Serial.begin(115200);
#endif

    digitalWrite(UL, 0);
    pinMode(UL, OUTPUT);
    digitalWrite(UH, 0);
    pinMode(UH, OUTPUT);
    digitalWrite(VL, 0);
    pinMode(VL, OUTPUT);
    digitalWrite(VH, 0);
    pinMode(VH, OUTPUT);
    digitalWrite(WL, 0);
    pinMode(WL, OUTPUT);
    digitalWrite(WH, 0);
    pinMode(WH, OUTPUT);

    pinMode(LED, OUTPUT);
    digitalWrite(LED, 0);

    pinMode(M0, OUTPUT);
    pinMode(M1, OUTPUT);

    TCCR2B = TCCR2B & 0b11111000 | 0x01;

    analogWrite(PWM, 0);
    pinMode(PWM, OUTPUT);

    // the comparator output is open-collector, so activate the internal pull-ups:
    pinMode(SM, INPUT);
    digitalWrite(SM, 1);
    pinMode(SL, INPUT);
    digitalWrite(SL, 1);
    pinMode(SH, INPUT);
    digitalWrite(SH, 1);
}

#define HIGH(pin) digitalWrite((pin), 1)
#define LOW(pin) digitalWrite((pin), 0)

int led_on = 0;
#define START_DELAY 15000
unsigned long cur_delay = START_DELAY;
long speed_change_count = 0;
int last_speedup = 0;

#define SWITCHOVER_DELAY 10000
#define START_NWAITS (SWITCHOVER_DELAY / 1000 * 280)
unsigned long last_nwaits = START_NWAITS;
#define BAILOUT_NWAITS (START_NWAITS + 50)

void microDelay() __attribute__ ((noinline));
void microDelay() {
    asm volatile("nop");
}

#define DELAY() microDelay()
//#define DELAY() delayMicroseconds(1)

void pulse1(int l, int h, int m, bool rising) {
    int pwr;
    if (cur_delay > SWITCHOVER_DELAY) {
        pwr = 100 + 40 * (cur_delay - SWITCHOVER_DELAY) / (START_DELAY - SWITCHOVER_DELAY);
    } else {
        if (last_nwaits > 300)
            pwr = 140;
        else
            pwr = 160;
    }

    analogWrite(PWM, pwr);

    HIGH(l);
    HIGH(h);

    if (cur_delay > SWITCHOVER_DELAY) {
        unsigned long start = micros();
        while ((micros() - start) < cur_delay) {
        }

        int now = millis();
        if (now - last_speedup > 5) {
            cur_delay = max(SWITCHOVER_DELAY, cur_delay - 5 - (cur_delay - 1000) / 256);
            last_speedup = now;
        }
    } else if (m != U_MUX) {
        // The board design is messed up, and the amuxsel bits
        // are essentially hard-wired to be 0.
        // If we had tried to set them to something else, don't do the back-emf
        // sensing since it will return bogus values.
        for (unsigned long i = 0; i < last_nwaits; i++) {
            DELAY();
        }
        for (unsigned long i = 0; i < last_nwaits; i++) {
            DELAY();
        }
        for (unsigned long i = 0; i < 10; i++) {
            DELAY();
        }
    } else {
        unsigned long nwaits = max(50, last_nwaits - 10);

        for (unsigned long i = 0; i < nwaits; i++) {
            DELAY();
        }

        int r = 0;
        int row = 0;
        int mr = 4;
        while (true) {
            DELAY();
            r = (PIND >> S) & 1;
            nwaits++;
            if (rising == r) {
                row++;
                if (row == mr)
                    break;
            }
            if (nwaits > last_nwaits + 10) {
                break;
            }
        }

        //for (unsigned long i = nwaits; i < last_nwaits; i++) {
            //DELAY();
        //}

        int dw = 1 + 16 * (last_nwaits / 400);

        if (nwaits < last_nwaits - 1) {
            digitalWrite(LED, 1);
            speed_change_count--;
            if (speed_change_count <= -2) {
                last_nwaits -= dw;
                speed_change_count = 0;
            }
        } else if (nwaits > last_nwaits + 1) {
            digitalWrite(LED, 0);
            speed_change_count = max(0, speed_change_count + 1);
            if (speed_change_count >= 2) {
                last_nwaits += 2 * dw + 1;
                speed_change_count = 0;
            }
        } else {
            speed_change_count = 0;
            digitalWrite(LED, 0);
        }

        //if (((PIND >> S) & 1) != rising) {
            //last_nwaits++;
            ////speed_change_count = 4;
            //digitalWrite(LED, 1);
        //}

        //analogWrite(PWM, pwr/2);
        for (unsigned long i = 0; i < last_nwaits - row; i++) {
            DELAY();
        }

        //if (((PIND >> S) & 1) != rising && speed_change_count < 0)
            //speed_change_count = 0;
        //if (last_nwaits < 400 && ((PIND >> S) & 1) != rising && speed_change_count < 0)
            //speed_change_count += 1;
        //if (last_nwaits < 400 && ((PIND >> S) & 1) != rising)
            //speed_change_count += 4;

        if (last_nwaits > BAILOUT_NWAITS || last_nwaits <= 102) {
            digitalWrite(LED, 0);
            cur_delay = START_DELAY;
            last_nwaits = START_NWAITS;
            last_speedup = millis();
        }
    }

    LOW(h);
    LOW(l);
}

#ifdef DEBUG
void pulse2(int l, int h, int s) {
    HIGH(l);
    HIGH(h);

    led_on ^= 1;
    //digitalWrite(LED, led_on);

    analogWrite(PWM, 50);
    Serial.print(s);
    for (int i = 0; i < 10; i++) {
        Serial.print(' ');
        Serial.print(analogRead(s));
        delay(100);
    }
    Serial.println();

    LOW(l);
    LOW(h);
}
#endif

#define pulse pulse1

void loop() {
    unsigned long start = micros();
    for (int i = 0; i < 7; i++) {
        pulse(UL, WH, V_MUX, 0);
        pulse(VL, WH, U_MUX, 1);
        pulse(VL, UH, W_MUX, 0);
        pulse(WL, UH, V_MUX, 1);
        pulse(WL, VH, U_MUX, 0);
        pulse(UL, VH, W_MUX, 1);
    }
#ifdef DEBUG
    unsigned long rps = (int)(1000000.0 / (micros() - start));
    if (rps >= 256)
        Serial.write((char)(rps>>8));
    Serial.write((char)rps);
    if (last_nwaits >= 256)
        Serial.write((char)(last_nwaits>>8));
    Serial.write((char)last_nwaits);
    Serial.write((char)0);
#endif
    led_on ^= 1;
    //digitalWrite(LED, led_on);
}
