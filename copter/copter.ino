#define UL 6
#define UH 12
#define VL 7
#define VH 10
#define WL 8
#define WH 9

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

    pinMode(WH, OUTPUT);
}

#define IN(pin) pinMode((pin), INPUT); digitalWrite((pin), 0)
#define HIGH(pin) pinMode((pin), OUTPUT); digitalWrite((pin), 1)
#define LOW(pin) pinMode((pin), OUTPUT); digitalWrite((pin), 0)

#define DELAY() delay(100)
void loop() {
    IN(UL);
    HIGH(VL);
    DELAY();

    IN(WH);
    LOW(UH);
    DELAY();

    IN(VL);
    HIGH(WL);
    DELAY();

    IN(UH);
    LOW(VH);
    DELAY();

    IN(WL);
    HIGH(UL);
    DELAY();

    IN(VH);
    LOW(WH);
    DELAY();
}
