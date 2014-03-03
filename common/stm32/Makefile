BINDIR:=$(HOME)/arm-cross/bin

CC=$(BINDIR)/arm-none-eabi-gcc
LD=$(CC)
OBJCOPY=$(BINDIR)/arm-none-eabi-objcopy
OPENOCD=$(BINDIR)/openocd
CFLAGS=-Wall -Wextra -Wimplicit-function-declaration -Wredundant-decls -Wstrict-prototypes -Wundef -Wshadow -g -fno-common -mcpu=cortex-m3 -mthumb -mfloat-abi=hard -MD -DSTM32F3
LDFLAGS=--static -lc -lnosys -T tut.ld -nostartfiles -Wl,--gc-sections -mcpu=cortex-m3 -mthumb -mfloat-abi=hard -lm -Wl,-Map=tut.map
OBJS=tut.o

all: tut.bin

tut.bin: tut.elf
	$(OBJCOPY) -Obinary tut.elf tut.bin

tut.elf: $(OBJS)
	$(CC) -o tut.elf $(OBJS) ~/arm-cross/arm-none-eabi/lib/libopencm3_stm32f3.a --static -lc -lnosys -T tut.ld -nostartfiles -Wl,--gc-sections -mcpu=cortex-m3 -mthumb -mfloat-abi=hard -lm -Wl,-Map=tut.map

flash: tut.bin
	sudo $(OPENOCD) -f stm32-openocd.cfg -c "init" -c "reset init" -c "flash write_image erase tut.bin 0x08000000" -c "reset run" -c "shutdown"

clean:
	rm -f *.elf *.bin *.list *.map *.o *.d *~
