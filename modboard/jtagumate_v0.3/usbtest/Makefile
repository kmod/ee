SRCS := blink.c \
	$(wildcard STM32_USB_Device_Library/*.c) \
	$(wildcard STM32_USB_Device_Library/*/*.c) \
	$(wildcard STM32_USB_Device_Library/*/*/*.c)
	# $(wildcard STM32_USB_OTG_Driver/*.c) \
	# $(wildcard STM32_USB_OTG_Driver/*/*.c) \
	# $(wildcard STM32_USB_OTG_Driver/*/*/*.c)
	# $(wildcard STM32_USB_HOST_Library/*.c) \
	# $(wildcard STM32_USB_HOST_Library/*/*.c) \
	# $(wildcard STM32_USB_HOST_Library/*/*/*.c)
PROGRAM_NAME := blink

FAMILY := stm32f40x

OPENOCD := /home/kmod/arm-cross/bin/openocd

CFLAGS += -I STM32_USB_Device_Library/Core/inc
CFLAGS += -I STM32_USB_HOST_Library/Core/inc
CFLAGS += -I STM32_USB_OTG_Driver/inc
CFLAGS += -I .

include ../../../common/stm32/Makefile.include
