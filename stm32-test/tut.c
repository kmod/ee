#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>

int leds[] = {GPIO8, GPIO9, GPIO10, GPIO11, GPIO12, GPIO13, GPIO14, GPIO15};
#define NLEDS (sizeof(leds) / sizeof(leds[0]))

static void gpio_setup(void)
{
        /* Enable GPIOE clock. */
        rcc_peripheral_enable_clock(&RCC_AHBENR, RCC_AHBENR_IOPEEN);

        for (unsigned i = 0; i < NLEDS; i++) {
            gpio_mode_setup(GPIOE, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, leds[i]);
        }
}

int main(void)
{
        gpio_setup();

        /* Blink the LED (PC8) on the board. */
        while (1) {
            for (unsigned l = 0; l < NLEDS; l++) {
                gpio_toggle(GPIOE, leds[l]);     /* LED on/off */
                for (int i = 0; i < 100000; i++) /* Wait a bit. */
                        __asm__("nop");
                gpio_toggle(GPIOE, leds[l]);     /* LED on/off */
            }
        }

        return 0;
}
