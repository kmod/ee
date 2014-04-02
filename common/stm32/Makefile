STM32DIR := $(dir $(lastword $(MAKEFILE_LIST)))

define assert_defined
ifeq ($($1),)
$$(error "Please set $1 before including this makefile")
endif
endef

$(eval $(call assert_defined,SRCS))
$(eval $(call assert_defined,PROGRAM_NAME))
$(eval $(call assert_defined,CPU))
$(eval $(call assert_defined,FAMILY))



BINDIR:=$(HOME)/arm-cross/bin

CC=$(BINDIR)/arm-none-eabi-gcc
LD=$(CC)
OBJCOPY=$(BINDIR)/arm-none-eabi-objcopy
OPENOCD=$(BINDIR)/openocd
CFLAGS := -Wall -Wextra -Wimplicit-function-declaration -Wredundant-decls -Wstrict-prototypes -Wundef -Wshadow -g -fno-common -mcpu=$(CPU) -mthumb -mfloat-abi=hard -MD -D$(FAMILY) -Wfatal-errors -std=c99 -I.
LDFLAGS=--static -lc -lnosys -T $(STM32DIR)/tut.ld -nostartfiles -Wl,--gc-sections -mcpu=$(CPU) -mthumb -mfloat-abi=hard -lm -Wl,-Map=$(PROGRAM_NAME).map
OBJS=$(SRCS:.c=.o)

all: $(PROGRAM_NAME).bin

$(PROGRAM_NAME).elf: $(OBJS) $(STM32DIR)/tut.ld
	$(CC) -o $(PROGRAM_NAME).elf $(OBJS) ~/arm-cross/arm-none-eabi/lib/libopencm3_stm32f3.a $(LDFLAGS)

$(PROGRAM_NAME).bin: $(PROGRAM_NAME).elf
	$(OBJCOPY) -Obinary $(PROGRAM_NAME).elf $(PROGRAM_NAME).bin

flash: $(PROGRAM_NAME).bin
	sudo $(OPENOCD) -f $(STM32DIR)/stm32-openocd.cfg -c "init" -c "reset init" -c "flash write_image erase $(PROGRAM_NAME).bin 0x08000000" -c "reset run" -c "shutdown"

clean:
	rm -f *.elf *.bin *.list *.map *.o *.d *~
