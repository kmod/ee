MEMORY
{
	flash (rx) : ORIGIN = 0x08000000, LENGTH = 256K
	sram (rwx) : ORIGIN = 0x20000000, LENGTH = 40K
}

/* Include the common ld script. */
INCLUDE stm32.ld

