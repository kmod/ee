#define ENABLE1 6
#define F1 8
#define BB1 7
#define ENABLE2 9
#define BB2 10
#define F2 11

#define VERT A0
#define HORZ A1

#define LED 13

int vmid = 512;
int hmid = 512;
void setup() {
    digitalWrite(ENABLE1, 0);

    pinMode(LED, OUTPUT);
    pinMode(ENABLE1, OUTPUT);
    pinMode(F1, OUTPUT);
    pinMode(BB1, OUTPUT);
    pinMode(VERT, INPUT);

    digitalWrite(LED, 1);
    delay(100);
    vmid = analogRead(VERT);
    hmid = analogRead(HORZ);
    digitalWrite(LED, 0);
}

void loop() {
    int vert = analogRead(VERT);
    int horz = analogRead(HORZ);
    double p1 = 0;
    double p2 = 0;

    if (vert < vmid) {
        p1 -= (vert - vmid) / vmid;
        p2 -= (vert - vmid) / vmid;
    } else if (vert > vmid) {
        p1 -= (vert - vmid) / (1023 - vmid);
        p2 -= (vert - vmid) / (1023 - vmid);
    }

    if (horz < hmid) {
        p1 -= (horz - hmid) / hmid;
        p2 += (horz - hmid) / hmid;
    } else if (horz > hmid) {
        p1 -= (horz - hmid) / (1023 - hmid);
        p2 += (horz - hmid) / (1023 - hmid);
    }

    if (p1 > 1) p1 = 1;
    if (p2 > 1) p2 = 1;
    if (p1 < -1) p1 = -1;
    if (p2 < -1) p2 = -1;

    const double thresh = 0.25;
    if (p1 > thresh) {
        digitalWrite(F1, 1);
        digitalWrite(BB1, 0);
        analogWrite(ENABLE1, 255 * p1);
    } else if (p1 < -thresh) {
        digitalWrite(F1, 0);
        digitalWrite(BB1, 1);
        analogWrite(ENABLE1, 255 * -p1);
    } else {
        digitalWrite(ENABLE1, 0);
    }

    if (p2 > thresh) {
        digitalWrite(F2, 1);
        digitalWrite(BB2, 0);
        analogWrite(ENABLE2, 255 * p2);
    } else if (p2 < -thresh) {
        digitalWrite(F2, 0);
        digitalWrite(BB2, 1);
        analogWrite(ENABLE2, 255 * -p2);
    } else {
        digitalWrite(ENABLE2, 0);
    }
}
