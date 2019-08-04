#include "Arduino.h"

//int main() {
    //pinMode(LED_BUILTIN, OUTPUT);
//}

#define LED PIN_SPI_SCK
#define IN PIN_A5

void setup() {
    pinMode(LED, OUTPUT);
    pinMode(IN, INPUT);
    Serial.begin(115200);
}

void loop() {
    int val = analogRead(IN);
    for (int i = 0; i < val; i += 10)
        Serial.print('.');
    Serial.println("");
    //Serial.println(val);
    //for (int i = 0; i < 256; i++) {
        //analogWrite(LED, i);
        //delay(10);
    //}

    //analogWrite(LED, 128);
    //digitalWrite(LED, 1);
    //delay(50);
    //digitalWrite(LED, 0);
    //delay(500);
}


