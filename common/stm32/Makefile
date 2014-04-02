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

FAMILY_LOWER := $(shell echo $(FAMILY) | tr A-Z a-z)


BINDIR:=$(HOME)/arm-cross/bin

CC=$(BINDIR)/arm-none-eabi-gcc
LD=$(CC)
OBJCOPY=$(BINDIR)/arm-none-eabi-objcopy
OPENOCD=$(BINDIR)/openocd
CFLAGS := -Wall -Wextra -Wimplicit-function-declaration -Wredundant-decls -Wstrict-prototypes -Wundef -Wshadow -g -fno-common -mcpu=$(CPU) -mthumb -mfloat-abi=hard -MD -D$(FAMILY) -Wfatal-errors -std=c99 -I. -Os
LDFLAGS=--static -lc -lnosys -T $(STM32DIR)/$(FAMILY).ld -nostartfiles -Wl,--gc-sections -mcpu=$(CPU) -mthumb -mfloat-abi=hard -lm -Wl,-Map=$(PROGRAM_NAME).map -lopencm3_stm32f4
OBJS=$(SRCS:.c=.o)

all: $(PROGRAM_NAME).bin

$(SRCS:.c=.o): %.o: %.c $(MAKEFILE_LIST)
	$(CC) -c -o $@ $< $(CFLAGS)

$(PROGRAM_NAME).elf: $(OBJS) $(STM32DIR)/$(FAMILY).ld $(MAKEFILE_LIST)
	$(CC) -o $(PROGRAM_NAME).elf $(OBJS) $(LDFLAGS)

$(PROGRAM_NAME).bin: $(PROGRAM_NAME).elf $(MAKEFILE_LIST)
	$(OBJCOPY) -Obinary $(PROGRAM_NAME).elf $(PROGRAM_NAME).bin

.PHONY: flash
flash: $(PROGRAM_NAME).bin
	$(OPENOCD) -f $(STM32DIR)/$(FAMILY)-openocd.cfg -c "init" -c "reset init" -c "flash write_image erase $(PROGRAM_NAME).bin 0x08000000" -c "reset run" -c "shutdown"

clean:
	rm -f *.elf *.bin *.list *.map *.o *.d *~
