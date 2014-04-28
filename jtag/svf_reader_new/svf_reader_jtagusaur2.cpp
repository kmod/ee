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

typedef unsigned char byte;

#define F_CPU 16000000
#define BAUD_RATE 1000000
#define MYUBRR (F_CPU / 16 / BAUD_RATE ) - 1

#define SWRITE(b) do {\
    while ((UCSR0A & _BV(UDRE0)) == 0) {};\
	UDR0 = b;\
} while (0)

inline byte SREAD() {
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

void jtag_pulse(byte nibble) {
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
        byte gotten = (PINC >> 2) & 1;
        byte diff = gotten ^ (nibble & 1);
        if (diff) {
            SWRITE(0x03);
            fail();
        }
    }
}

void jtag_auto() {
    while (true) {
        byte num_nibbles = SREAD();

        if (num_nibbles == 0)
            break;

        byte full_bytes = num_nibbles / 2;
        for (byte i = 0; i < full_bytes; i++) {
            byte recv = SREAD();

            jtag_pulse(recv & 0x0f);
            jtag_pulse(recv >> 4);
        }

        if (num_nibbles & 1) {
            byte recv = SREAD();

            jtag_pulse(recv & 0x0f);
        }

        SWRITE(0x00);
    }
}

volatile byte* ports[] = {
    &DDRB,
    &DDRC,
    &DDRD,
    &PINB,
    &PINC,
    &PIND,
    &PORTB,
    &PORTC,
    &PORTD,
};

void bitbang() {
    while (true) {
        byte cmd = SREAD();
        if (cmd == 0x00)
            break;

        if (cmd == 'w') {
            byte data = SREAD();
            byte portnum = (data >> 4);
            byte bitnum = (data >> 1) & 0x07;
            byte val = data & 1;

            volatile byte* port = ports[portnum];

            if (data & 1)
                *port |= _BV(bitnum);
            else
                *port &= ~_BV(bitnum);
            SWRITE(0x00);
            continue;
        }

        if (cmd == 'r') {
            byte data = SREAD();
            volatile byte* port = ports[data];
            byte val = *port;
            SWRITE(0x00);
            SWRITE(val);
            continue;
        }

        if (cmd == '1') {
            (*ports[8]) |= _BV(6);
            continue;
        }

        if (cmd == '2') {
            (*ports[8]) &= ~_BV(6);
            continue;
        }

        SWRITE(0x03);
        fail();
    }
}

int main() {
    DDRC = _BV(0) | _BV(1) | _BV(3);
    DDRD = _BV(1) | _BV(6) | _BV(7);

    /*Set baud rate */ 
	UBRR0H = (byte)(MYUBRR>>8);
	UBRR0L = (byte) MYUBRR;
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

    SWRITE(0x02); // num endpoints

    SWRITE(0x10); SWRITE(0x00); // bitbang
    SWRITE(0x30); SWRITE(0x01); // JTAG_AUTO

    while (true) {
        byte c1 = SREAD();
        byte c2 = SREAD();

        if (c1 == 0x30) {
            if (c2 != 0x01) {
                SWRITE(0x02);
                SWRITE(c2);
                fail();
            }

            SWRITE(0x00);
            SWRITE(0x00);

            jtag_auto();
            continue;
        }

        if (c1 = 0x10) {
            if (c2 != 0x00) {
                SWRITE(0x02);
                SWRITE(c2);
                fail();
            }

            SWRITE(0x00);
            SWRITE(0x00);
            bitbang();
            continue;
        }

        SWRITE(0x01);
        SWRITE(c1);
        fail();
    }
}

