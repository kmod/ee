/// A very basic STM32 demo that runs of the internal oscillator,
/// flashes a LED, and writes out some serial data.
///
/// Michael Hope <michaelh@juju.net.nz>, 2010
///
#include "stm32f30x.h"

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

/// Main function.  Called by the startup code.
int main(void)
{
    RCC->AHBENR |= 0
        // Turn on IO Port E
        | RCC_AHBENR_GPIOEEN
        ;

    // I don't know why this is required, but sometimes we need to delay
    // between enabling the GPIO clock and setting the registers.
    delay(5000);

    GPIOE->MODER = 0x55555555;
    GPIOE->OTYPER = 0x0;
    GPIOE->OSPEEDR = 0x0;
    GPIOE->PUPDR = 0x0;
    //GPIOE->MODER = (GPIOE->MODER & ~GPIO_MODER_MODER10) | (GPIO_MODER_MODER10_0); // OUTPUT
    //GPIOE->OTYPER = (GPIOE->OTYPER & ~GPIO_OTYPER_OT_10) | (0); // push-pull
    //GPIOE->OSPEEDR = (GPIOE->OSPEEDR & ~GPIO_OSPEEDER_OSPEEDR10) | (0); // low speed
    //GPIOE->PUPDR = (GPIOE->PUPDR & ~GPIO_PUPDR_PUPDR10) | (0); // low speed

    for (int i = 0; i < 3; i++) {
        delay(800000);
        GPIOE->ODR = ~0;
        delay(800000);
        GPIOE->ODR = 0;
    }

    for (;;)
    {
        delay(15000000);

        GPIOE->ODR = ~0;

        delay(1000000);

        GPIOE->ODR = 0;
    }
}
