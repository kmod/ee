#include "Arduino.h"
#define PWM 3

#define UL A3
#define UH A0

#define S 6
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

void setup() {
    Serial.begin(115200);

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
    digitalWrite(LED, 1);

    pinMode(M0, OUTPUT);
    pinMode(M1, OUTPUT);

    TCCR2B = TCCR2B & 0b11111000 | 0x01;

    analogWrite(PWM, 0);
    pinMode(PWM, OUTPUT);

    digitalWrite(LED, 1);
    delay(500);
    digitalWrite(LED, 0);
    delay(100);
    digitalWrite(LED, 1);
    delay(100);
    digitalWrite(LED, 0);
    delay(100);
    //delay(1000);
    //digitalWrite(LED, 0);

    // the comparator output is open-collector, so activate the internal pull-up:
    pinMode(S, INPUT);
    digitalWrite(S, 1);
}

#define HIGH(pin) digitalWrite((pin), 1)
#define LOW(pin) digitalWrite((pin), 0)

int led_on = 0;
unsigned long cur_delay = 15000;
int last_speedup = 0;
unsigned long vhalf = 200;

int _ = 0;
unsigned long last_nwaits = 200;

void microDelay() __attribute__ ((noinline));
void microDelay() {
    asm volatile("nop");
}

#define DELAY() microDelay()
//#define DELAY() delayMicroseconds(1)

void pulse1(int l, int h, int m, bool rising) {
    int pwr;
    if (cur_delay > 5000)
        pwr = 70;
    else if (cur_delay > 1000)
        pwr = 120;
    else {
        if (last_nwaits < 150)
            pwr = 180;
        else
            pwr = 140;
    }

    analogWrite(PWM, pwr);

    //led_on ^= 1;
    //digitalWrite(LED, led_on);

    //int vhalf_meas = analogRead(VREF)/2;
    //vhalf = (vhalf * 7 + vhalf_meas) / 8;

    //const int N = 5;
    //int reads[N];
    //reads[0] = analogRead(s);

    HIGH(l);
    HIGH(h);
    digitalWrite(M0, (m&1));
    digitalWrite(M1, ((m>>1)&1));

    /*if (true) {
        Serial.write((char)(vhalf>>2));
        Serial.write((char)s);
        Serial.write((char)(1 + rising));
        for (int i = 1; i < N; i++) {
            reads[i] = analogRead(s);
        }
        bool done = false;
        for (int i = 0; i < N; i++) {
            Serial.write((char)(reads[i] >> 2));
            if ((!done) && (rising == 1) && (reads[i] > vhalf * 1.1)) {
                Serial.write((char)255);
                done = true;
            } else if ((!done) && (rising == 0) && (reads[i] < vhalf * 0.9)) {
                Serial.write((char)255);
                done = true;
            }
        }

        Serial.write((char)0);
    }*/

    if (cur_delay > 1000) {
        unsigned long start = micros();
        while ((micros() - start) < cur_delay) {
        }
    } else if (m != 0) {
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
    } else {
        unsigned long nwaits = max(20, last_nwaits - 4);

        for (unsigned long i = 0; i < nwaits; i++) {
            DELAY();
        }

        int r = 0;
        while (true) {
            DELAY();
            r = (PIND >> S) & 1;
            nwaits++;
            if (rising == 1 && r == 1) {
                //digitalWrite(LED, 0);
                break;
            }
            if (rising == 0 && r == 0) {
                //digitalWrite(LED, 0);
                break;
            }
            if (nwaits > last_nwaits * 2 + 4) {
                //digitalWrite(LED, 1);
                break;
            }
        }

        if (nwaits > last_nwaits) {
            last_nwaits += 2;
        } else if (nwaits < last_nwaits) {
            last_nwaits--;
        }
        //Serial.write((char)s);
        //Serial.write((char)(rising + 1));
        //Serial.write((char)(r>>2));
        //Serial.write((char)nwaits);
        //Serial.write((char)0);
        for (unsigned long i = 0; i < last_nwaits; i++) {
            DELAY();
        }
        if (((PIND >> S) & 1) != rising)
            last_nwaits++;
        //while ((micros() - start) < cur_delay) {
        //}
        //
        if (last_nwaits > 300) {
            cur_delay = 20000;
            last_nwaits = 200;
            last_speedup = millis();
        }
    }

    int now = millis();
    if (now - last_speedup > pwr / 8) {
        cur_delay = max(1000, cur_delay - 50);
        last_speedup = now;
    }

    LOW(h);
    LOW(l);
}

void pulse2(int l, int h, int s) {
    HIGH(l);
    HIGH(h);

    led_on ^= 1;
    digitalWrite(LED, led_on);

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
    unsigned long rps = (int)(1000000.0 / (micros() - start));
    if (rps >= 256)
        Serial.write((char)(rps>>8));
    Serial.write((char)rps);
    if (last_nwaits >= 256)
        Serial.write((char)(last_nwaits>>8));
    Serial.write((char)last_nwaits);
    Serial.write((char)0);
    led_on ^= 1;
    digitalWrite(LED, led_on);
}
