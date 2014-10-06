MEMORY
{
	rom (rx) : ORIGIN = 0x08000000, LENGTH = 256K
	ram (rwx) : ORIGIN = 0x20000000, LENGTH = 40K
}

/* Include the common ld script. */
INCLUDE libopencm3_stm32f3.ld

