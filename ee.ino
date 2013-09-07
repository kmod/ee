void setup() {
    Serial.begin(115200);
}

void microDelay(unsigned long) __attribute__ ((noinline));
void microDelay(unsigned long loops) {
    while (loops > 0) {
        loops--;
        asm ("nop");
    }
}

#define delay_cycles_CONST(cycles) { \
   if(cycles&1) asm volatile("nop"); \
   if(cycles&2) asm volatile("nop \n\t nop"); \
   if(cycles&4) asm volatile("push r26 \n\t pop r26"); \
   if(cycles > 7) { \
      asm volatile( \
          "1:    sbiw %0, 1"      "\n\t" \
          "      brne 1b"         "\n\t" \      
          "      nop"             "\n\t" \
          "      nop"             "\n\t" \
          "      nop"             "\n\t" \
          : : "w" (((cycles&0xfff8)-4)>>2) \
     ); \
   } \
}

void delay_cycles_VAR(unsigned int cycles) __attribute__ ((noinline));
void delay_cycles_VAR(unsigned int cycles) {
  if(cycles < 15) return;
  asm volatile(
    "1:  sbiw %0, 1"    "\n\t"      // 2 cycles
    "            brne 1b"            // 2 cycles if branch taken
    : : "r" ((cycles>>2))
  );
}

void loop() {
    unsigned long start = micros();
    delay_cycles_CONST(16);
    unsigned long elapsed = micros() - start;
    if (elapsed >= 256)
        Serial.write((char)(elapsed >> 8));
    Serial.write((char)elapsed);
    Serial.write((char)0);
}
