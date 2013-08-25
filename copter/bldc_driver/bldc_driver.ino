#define UL 3
#define UH 6

#define REVERSE
#ifdef REVERSE
#define VL 10
#define VH 7
#define WL 9
#define WH 8
#else
#define VL 9
#define VH 8
#define WL 10
#define WH 7
#endif

#define LED 13

void setup() {
    pinMode(UL, INPUT);
    digitalWrite(UL, 0);
    pinMode(UH, INPUT);
    digitalWrite(UH, 0);
    pinMode(VL, INPUT);
    digitalWrite(VL, 0);
    pinMode(VH, INPUT);
    digitalWrite(VH, 0);
    pinMode(WL, INPUT);
    digitalWrite(WL, 0);
    pinMode(WH, INPUT);
    digitalWrite(WH, 0);

    pinMode(LED, OUTPUT);
    digitalWrite(LED, 1);

    TCCR1B = TCCR1B & 0b11111000 | 0x01;
    TCCR2B = TCCR2B & 0b11111000 | 0x01;

    delay(1000);
}

#define IN(pin) pinMode((pin), INPUT); digitalWrite((pin), 0)
#define HIGH(pin) pinMode((pin), OUTPUT); digitalWrite((pin), 1)
#define LOW(pin) pinMode((pin), OUTPUT); digitalWrite((pin), 0)

#define DELAY() delay(100)

int led_on = 0;
int cur_delay = 15000;
int last_speedup = 0;

void pulse(int l, int h) {
    int pwr = (int)(10 + 150  / (cur_delay / 1000 + 1));
    if (cur_delay > 5000)
        pwr = 20;
    else
        pwr = 30;
    analogWrite(l, pwr);
    HIGH(h);

    led_on ^= 1;
    digitalWrite(LED, led_on);

    delayMicroseconds(cur_delay);
    int now = millis();
    if (now - last_speedup > pwr / 10) {
        cur_delay = max(3000, cur_delay - 100);
        last_speedup = now;
    }

    IN(h);
    IN(l);
}

void loop() {
    pulse(UL, WH);
    pulse(VL, WH);
    pulse(VL, UH);
    pulse(WL, UH);
    pulse(WL, VH);
    pulse(UL, VH);
}
