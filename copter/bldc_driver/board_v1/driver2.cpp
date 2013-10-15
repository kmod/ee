#include "Arduino.h"

#define PWM 3

#define UL A3
#define UH A0

#define SM 2
#define SL 6
#define SH 7
#define S SM

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

#define MOSI 11
#define MISO 12
#define SCK 13
#define SS 10

void setup() {
    pinMode(SL, INPUT);
    pinMode(SM, INPUT);
    pinMode(SH, INPUT);
    digitalWrite(SL, 1);
    digitalWrite(SM, 1);
    digitalWrite(SH, 1);

    pinMode(UL, OUTPUT);
    pinMode(UH, OUTPUT);
    pinMode(VL, OUTPUT);
    pinMode(VH, OUTPUT);
    pinMode(WL, OUTPUT);
    pinMode(WH, OUTPUT);

    pinMode(PWM, OUTPUT);

    // Set PWM timer prescaler
    TCCR2B = TCCR2B & 0b11111000 | 0x01;

    SPCR = (1<<SPE) | (1<<CPHA);

    pinMode(MOSI, INPUT);
    pinMode(MISO, OUTPUT);
    pinMode(SCK, INPUT);
    pinMode(SS, INPUT);
}

#define INITIAL_SPEED 10000
#define MAX_POWER 180
#define MIN_POWER 10
#define MIN_SENSORLESS_SPEED 1000

unsigned int target_speed = 300;
unsigned int current_speed = INITIAL_SPEED;
unsigned int current_power = 120;

void microDelay() __attribute__ ((noinline));
void microDelay() {
    asm volatile("nop");
}

#define DELAY() microDelay()

void pulse(int l, int h, int r) {
    analogWrite(PWM, current_power);

    digitalWrite(l, 1);
    digitalWrite(h, 1);

    //if (h == UH)
        //while(1);

    int ds = 1 + 0*(current_speed / 250) + (current_speed / 1000);
    if (current_speed > MIN_SENSORLESS_SPEED || r == 2) {
        for (int i = 0; i < current_speed + 4; i++) {
            DELAY();
        }
        if (current_speed > MIN_SENSORLESS_SPEED)
            current_speed -= ds;
        delay(2000);
    } else {
        bool fe1 = bitRead(PIND, SM) == r;
        for (int i = 0; i < current_speed/2-50; i++) {
            DELAY();
        }
        for (int i = 0; i < 50; i++) {
            DELAY();
        }
        bool fe2 = bitRead(PIND, SM) == r;
        for (int i = 0; i < 4; i++) {
            DELAY();
        }
        bool fe3 = bitRead(PIND, SM) == r;
        for (int i = 0; i < current_speed/2-4; i++) {
            DELAY();
        }

        static int power_changes = 0;
        power_changes = power_changes * 7 / 8;
        if (fe2) {
            if (current_speed > target_speed) {
                current_speed = max(current_speed - ds, target_speed);
            } else if (current_speed <= target_speed) {
                if (power_changes > -64) {
                    power_changes -= 256;
                    current_power = max(MIN_POWER, current_power - 1);
                }
            }
        } else {
            if (current_speed < target_speed) {
                current_speed = min(current_speed + 2 * ds, target_speed);
            } else if (current_speed >= target_speed) {
                if (power_changes < 256) {
                    power_changes += 256;
                    current_power = min(MAX_POWER, current_power + 1);
                }
            }
        }
    }

    digitalWrite(l, 0);
    digitalWrite(h, 0);
}

void check_spi() {
    //SPDR = (current_speed / 4);
    if (bitRead(SPSR, SPIF)) {
        uint8_t b = SPDR;
        target_speed = b * 4;
    }
}

void loop() {
    for (int i = 0; i < 7; i++) {
        check_spi();
        pulse(UL, WH, 2);
        check_spi();
        pulse(VL, WH, 1);
        check_spi();
        pulse(VL, UH, 2);
        check_spi();
        pulse(WL, UH, 2);
        check_spi();
        pulse(WL, VH, 0);
        check_spi();
        pulse(UL, VH, 2);
    }
}
