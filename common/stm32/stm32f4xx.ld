MEMORY
{
	flash (rx) : ORIGIN = 0x08000000, LENGTH = 1024K
	sram (rwx) : ORIGIN = 0x20000000, LENGTH = 128K
}

/* Include the common ld script. */
INCLUDE stm32.ld

