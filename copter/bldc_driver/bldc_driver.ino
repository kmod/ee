#define PWM 3
#define VREF A5

#define UL 6
#define UH 11
#define US A4


#define REVERSE
#ifdef REVERSE
#define VL 8
#define VH 9
#define VS A2
#define WL 7
#define WH 10
#define WS A3
#else
#define VL 7
#define VH 10
#define VS A3
#define WL 8
#define WH 9
#define WS A2
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

    // Set ADC prescaler
    // http://www.extremeelectronics.co.in/avrtutorials/images/ADPS.gif
    // 0b100 is 16, giving 1MHz
    ADCSRA = ADCSRA & 0b11111000 | 0b010;
}

#define IN(pin) pinMode((pin), INPUT); digitalWrite((pin), 0)
#define SOFTHIGH(pin) pinMode((pin), INPUT); digitalWrite((pin), 1)
#define HIGH(pin) pinMode((pin), OUTPUT); digitalWrite((pin), 1)
#define LOW(pin) pinMode((pin), OUTPUT); digitalWrite((pin), 0)

#define DELAY() delay(100)

int led_on = 0;
unsigned long cur_delay = 15000;
int last_speedup = 0;
unsigned long vhalf = 200;

int _ = 0;
int last_nwaits = 40;

void pulse1(int l, int h, int s, bool rising) {
    int pwr;
    if (cur_delay > 5000)
        pwr = 60;
    else if (cur_delay > 1000)
        pwr = 100;
    else {
        if (last_nwaits < 10)
            pwr = 255;
        else
            pwr = 150;
    }

    analogWrite(PWM, pwr);
    unsigned long start = micros();

    led_on ^= 1;
    digitalWrite(LED, led_on);

    //int vhalf_meas = analogRead(VREF)/2;
    //vhalf = (vhalf * 7 + vhalf_meas) / 8;

    //const int N = 5;
    //int reads[N];
    //reads[0] = analogRead(s);

    HIGH(l);
    HIGH(h);

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
        while ((micros() - start) < cur_delay) {
        }
    } else {
        int nwaits = max(3, last_nwaits - 3);

        for (int i = 0; i < nwaits; i++) {
            _ = digitalRead(s);
        }

        int r = 0;
        while (true) {
            r = digitalRead(s);
            //Serial.write((char)r);
            if (rising == 1 && r == 1)
                break;
            if (rising == 0 && r == 0)
                break;
            nwaits++;
            if (nwaits > cur_delay / 10)
                break;
        }

        if (nwaits > last_nwaits) {
            last_nwaits++;
        } else if (nwaits < last_nwaits) {
            last_nwaits--;
        }
        //Serial.write((char)s);
        //Serial.write((char)(rising + 1));
        //Serial.write((char)(r>>2));
        //Serial.write((char)nwaits);
        //Serial.write((char)0);
        for (int i = 0; i < last_nwaits; i++) {
            _ = digitalRead(s);
        }
        //while ((micros() - start) < cur_delay) {
        //}
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
        pulse(UL, WH, VS, 0);
        pulse(VL, WH, US, 1);
        pulse(VL, UH, WS, 0);
        pulse(WL, UH, VS, 1);
        pulse(WL, VH, US, 0);
        pulse(UL, VH, WS, 1);
    }
    int rps = (int)(1000000.0 / (micros() - start));
    Serial.write((char)rps);
    Serial.write((char)last_nwaits);
    Serial.write((char)0);
}
