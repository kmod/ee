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
        __asm__ volatile ("nop");
    }
}

/// Main function.  Called by the startup code.
int main(void)
{
    RCC->AHBENR |= 0
        // Turn on IO Port E
        | RCC_AHBENR_GPIOEEN
        ;


    GPIOE->MODER = 0x55555555;
    //GPIOE->OTYPER = 0x0;
    //GPIOE->OSPEEDR = 0x0;
    //GPIOE->PUPDR = 0x0;
    //GPIOE->MODER = (GPIOE->MODER & ~GPIO_MODER_MODER10) | (GPIO_MODER_MODER10_0); // OUTPUT
    //GPIOE->OTYPER = (GPIOE->OTYPER & ~GPIO_OTYPER_OT_10) | (0); // push-pull
    //GPIOE->OSPEEDR = (GPIOE->OSPEEDR & ~GPIO_OSPEEDER_OSPEEDR10) | (0); // low speed
    //GPIOE->PUPDR = (GPIOE->PUPDR & ~GPIO_PUPDR_PUPDR10) | (0); // low speed

    for (;;)
    {
        // Around 1/4 of a second
        delay(1000000);

        // Turn all pins on
        GPIOE->ODR = ~0;

        delay(1000000);

        // Turn all pins off
        GPIOE->ODR = 0;
    }
}
