// Simple sketch that is optimized to work with the JTAG svf_reader.py script,
// though really it just does SPI.

// To hookup:
// pin A0 is TDI (output)
// pin A1 is TMS (output)
// pin A2 is TDO (input)
// pin A3 is TCK (output)
// pins 6 and 7 can be used for debug output [currently not enabled]
// make sure to do level shifting appropriately

// JTAG:
// - all signals get sampled on the rising edge of TCK
// - TDO gets updated on the falling edge of TCK
// - TMS/TDI are recommended to be updated on the falling edge of TCK
// - on entering a new state, the first new data appears on TDO at the next falling clock edge

#include <avr/io.h>

#define F_CPU 16000000
#define BAUD_RATE 1000000
#define MYUBRR (F_CPU / 16 / BAUD_RATE ) - 1

#define SWRITE(b) do {\
    while ((UCSR0A & _BV(UDRE0)) == 0) {};\
	UDR0 = b;\
} while (0)

inline unsigned char SREAD() {
    while ((UCSR0A & _BV(RXC0)) == 0) {
    }
    return UDR0;
}

void fail() {
    while (true) {
        PORTD |= _BV(6) | _BV(7);
        for (long i = 0; i < 100000; i++) {
            asm("nop");
        }
        PORTD &= ~(_BV(6) | _BV(7));
        for (long i = 0; i < 100000; i++) {
            asm("nop");
        }
    }
}

void jtag_pulse(unsigned char nibble) {
    PORTC = (PORTC & ~0x03) | ((nibble >> 2) & 0x03);
    asm("nop"); asm("nop"); asm("nop"); asm("nop");
    asm("nop"); asm("nop"); asm("nop"); asm("nop");
    asm("nop"); asm("nop"); asm("nop"); asm("nop");
    asm("nop"); asm("nop"); asm("nop"); asm("nop");
    PORTC &= ~_BV(3);
    asm("nop"); asm("nop"); asm("nop"); asm("nop");
    asm("nop"); asm("nop"); asm("nop"); asm("nop");
    asm("nop"); asm("nop"); asm("nop"); asm("nop");
    asm("nop"); asm("nop"); asm("nop"); asm("nop");
    PORTC |= _BV(3);

    if (nibble & 0x02) {
        unsigned char gotten = (PINC >> 2) & 1;
        unsigned char diff = gotten ^ (nibble & 1);
        if (diff) {
            fail();
        }
    }
}

void jtag_auto() {
    while (true) {
        unsigned char num_nibbles = SREAD();

        if (num_nibbles == 0)
            break;

        unsigned char full_bytes = num_nibbles / 2;
        for (unsigned char i = 0; i < full_bytes; i++) {
            unsigned char recv = SREAD();

            jtag_pulse(recv & 0x0f);
            jtag_pulse(recv >> 4);
        }

        if (num_nibbles & 1) {
            unsigned char recv = SREAD();

            jtag_pulse(recv & 0x0f);
        }

        SWRITE(0x00);
    }
}

int main() {
    DDRC = _BV(0) | _BV(1) | _BV(3);
    DDRD = _BV(1) | _BV(6) | _BV(7);

    /*Set baud rate */ 
	UBRR0H = (unsigned char)(MYUBRR>>8); 
	UBRR0L = (unsigned char) MYUBRR; 
	/* Enable receiver and transmitter   */
	UCSR0B = (1<<RXEN0)|(1<<TXEN0); 
	/* Frame format: 8data, No parity, 1stop bit */ 
	UCSR0C = (3<<UCSZ00);

    // Reset:
    PORTC |= 0x03;
    for (char c = 0; c < 5; c++) {
        PORTC &= ~_BV(3);
        asm("nop"); asm("nop"); asm("nop"); asm("nop");
        asm("nop"); asm("nop"); asm("nop"); asm("nop");
        asm("nop"); asm("nop"); asm("nop"); asm("nop");
        asm("nop"); asm("nop"); asm("nop"); asm("nop");
        PORTC |= _BV(3);
        asm("nop"); asm("nop"); asm("nop"); asm("nop");
        asm("nop"); asm("nop"); asm("nop"); asm("nop");
        asm("nop"); asm("nop"); asm("nop"); asm("nop");
        asm("nop"); asm("nop"); asm("nop"); asm("nop");
    }
    SWRITE(0xaf);

    SWRITE(0x01); // num endpoints

    SWRITE(0x30); SWRITE(0x01); // JTAG_AUTO

    while (true) {
        unsigned char c1 = SREAD();
        unsigned char c2 = SREAD();
        if (c1 != 0x30) {
            SWRITE(0x01);
            SWRITE(c1);
            fail();
        }
        if (c2 != 0x01) {
            SWRITE(0x02);
            SWRITE(c2);
            fail();
        }

        SWRITE(0x00);
        SWRITE(0x00);

        jtag_auto();
    }
}

