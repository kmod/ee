/// A very basic STM32 demo that runs of the internal oscillator,
/// flashes a LED, and writes out some serial data.
///
/// Michael Hope <michaelh@juju.net.nz>, 2010
///
#include "stm32f4xx.h"

/// Spin delay
void delay(int count)
{
    for (int i = 0; i < count; i++)
    {
        __asm__ volatile ("");
    }
}

// helper function for debugging in gdb:
GPIO_TypeDef* gpio(int i) {
    switch (i) {
        case 0:
            return GPIOA;
        case 1:
            return GPIOB;
        case 2:
            return GPIOC;
        case 3:
            return GPIOD;
        case 4:
            return GPIOE;
        default:
            return 0;
    }
}

void ledsOn() {
    GPIOC->BSRRH = (1 << 13) | (1 << 14) | (1 << 15);
    GPIOB->BSRRH = (1 << 9);
}

void ledsOff() {
    GPIOC->BSRRL = (1 << 13) | (1 << 14) | (1 << 15);
    GPIOB->BSRRL = (1 << 9);
}

/// Main function.  Called by the startup code.
int main(void)
{
    RCC->AHB1ENR |= 0
        | RCC_AHB1ENR_GPIOBEN
        | RCC_AHB1ENR_GPIOCEN
        ;

    // I don't know why this is required, but sometimes we need to delay
    // between enabling the GPIO clock and setting the registers.
    delay(5000);

    GPIOB->MODER |= (0b01 << (9 * 2));
    GPIOB->OTYPER = 0x0;
    GPIOB->OSPEEDR = 0x0;
    GPIOB->PUPDR = 0x0;

    GPIOC->MODER |= (0b01 << (13 * 2)) | (0b01 << (14 * 2)) | (0b01 << (15 * 2));
    GPIOC->OTYPER = 0x0;
    GPIOC->OSPEEDR = 0x0;
    GPIOC->PUPDR = 0x0;
    //GPIOC->MODER = (GPIOC->MODER & ~GPIO_MODER_MODER10) | (GPIO_MODER_MODER10_0); // OUTPUT
    //GPIOC->OTYPER = (GPIOC->OTYPER & ~GPIO_OTYPER_OT_10) | (0); // push-pull
    //GPIOC->OSPEEDR = (GPIOC->OSPEEDR & ~GPIO_OSPEEDER_OSPEEDR10) | (0); // low speed
    //GPIOC->PUPDR = (GPIOC->PUPDR & ~GPIO_PUPDR_PUPDR10) | (0); // low speed

    for (int i = 0; i < 3; i++) {
        delay(800000);
        ledsOn();
        delay(800000);
        ledsOff();
    }

    for (;;)
    {
        delay(15000000);

        ledsOn();

        delay(1000000);

        ledsOff();
    }
}
