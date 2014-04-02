#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>

int main(void) {
    /* Enable GPIOE clock. */
    //rcc_peripheral_enable_clock(&RCC_AHB1ENR, RCC_AHB1ENR_IOPEEN);
    rcc_periph_clock_enable(RCC_GPIOC);


    gpio_mode_setup(GPIOC, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, GPIO13);

	/* Blink the LED (PC8) on the board. */
    int i;
	while (1) {
		/* Manually: */
		// GPIOD_BSRR = GPIO12;		/* LED off */
		// for (i = 0; i < 1000000; i++)	/* Wait a bit. */
		//	__asm__("nop");
		// GPIOD_BRR = GPIO12;		/* LED on */
		// for (i = 0; i < 1000000; i++)	/* Wait a bit. */
		//	__asm__("nop");

		/* Using API functions gpio_set()/gpio_clear(): */
		// gpio_set(GPIOD, GPIO12);	/* LED off */
		// for (i = 0; i < 1000000; i++)	/* Wait a bit. */
		//	__asm__("nop");
		// gpio_clear(GPIOD, GPIO12);	/* LED on */
		// for (i = 0; i < 1000000; i++)	/* Wait a bit. */
		//	__asm__("nop");

		/* Using API function gpio_toggle(): */
		gpio_toggle(GPIOC, GPIO13);	/* LED on/off */
		for (i = 0; i < 1000000; i++) {	/* Wait a bit. */
			__asm__("nop");
		}
	}


    return 0;
}
