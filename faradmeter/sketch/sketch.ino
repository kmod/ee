int LED = 9;
double R1 = 21500.0; // measured resistance of resistor R1 (see schematic.png)
double R2 = 982.0; // measured resistance of resistor R2 (see schematic.png)

void setup() {
    pinMode(LED, OUTPUT);

    Serial.begin(9600);
}

void loop() {
    digitalWrite(LED, LOW);
    delay(1000);
    digitalWrite(LED, HIGH);

    pinMode(A5, INPUT);
    pinMode(A4, OUTPUT);
    pinMode(A3, OUTPUT);

    digitalWrite(A4, 0);
    digitalWrite(A3, 0);

    int input = 1023;
    while (input > 3) {
        input = analogRead(A5);
        Serial.print("Driving low, ");
        Serial.println(input);
        delay(1);
    }

    int waited = 0;
    double driven = 0;
    pinMode(A4, INPUT);
    pinMode(A3, INPUT);

    double res = R1;
    long start = micros();
    long prev = start;
    long now = prev;
    pinMode(A4, OUTPUT);
    digitalWrite(A4, 1);
    while (true) {
        if (prev - start > 5000) {
            pinMode(A4, INPUT);
            pinMode(A3, OUTPUT);
            digitalWrite(A3, 1);
            res = R2;
        }
        delayMicroseconds(100);
        waited += 1;

        input = analogRead(A5);

        now = micros();
        driven += .000001 * (now - prev) / res;
        prev = now;

        if (input > 511) break;
    }
    Serial.print("After ");
    Serial.print(now - start);
    Serial.print("us (");
    Serial.print(waited);
    Serial.print(" waits): ");
    Serial.println(input);

    double elapsed = 0.000001 * (prev - start);
    driven /= elapsed;

    double rc = elapsed / log(1023.0 / (1023 - input));
    Serial.print("RC constant: ");
    Serial.print(rc * 1000000.0);
    Serial.println("us");

    Serial.print("Avg resistance: ");
    Serial.print(1.0/driven);
    Serial.println();

    double cap = rc * driven;

    Serial.print("Capacitance: ");
    double cap_uF = cap * 1000.0 * 1000.0;
    if (cap_uF > 1) {
        Serial.print(cap_uF);
        Serial.println("uF");
    } else {
        Serial.print(cap_uF * 1000.0);
        Serial.println("nF");
    }
}
