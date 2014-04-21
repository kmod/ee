// Simple sketch that is optimized to work with the JTAG svf_reader.py script,
// though really it just does SPI.

// To hookup:
// pin A0 is TDI (output)
// pin A1 is TMS (output)
// pin A2 is TDO (input)
// pin A3 is TCK (output)
// pins 6 and 7 can be used for debug output [currently not enabled]
// make sure to do level shifting appropriately

// protocol:
// each message is a 4-bit packet, and there can be 0, 1, or 2 packets per byte.
// packet structure, MSB first:
// - TMS
// - TDI
// - get_tdo (whether or not to read the TDO line and send it back)
// - #enable (set to 1 to set to a noop packet, ex if you want to send just 1 packet in a byte)

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

int main() {
    //pinMode(A0, OUTPUT);
    //pinMode(A1, OUTPUT);
    //pinMode(A2, INPUT);
    //pinMode(A3, OUTPUT);
//
    //pinMode(6, OUTPUT); // LED
    //pinMode(7, OUTPUT); // LED

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

    SWRITE(0xae);

    while (true) {
        unsigned char recv = SREAD();

        PORTD |= _BV(6);
        PORTD &= ~_BV(7);

        PORTC = (PORTC & ~0x03) | ((recv >> 2) & 0x03);
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

        PORTD &= ~_BV(6);
        PORTD |= _BV(7);

        if (recv & 0x02) {
            unsigned char to_send = (PINC >> 2) & 1;
            SWRITE(to_send);
        }
    }
}

