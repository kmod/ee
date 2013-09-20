bldc_driver.o: driver.cpp Makefile
	/opt/arduino-1.0.5/hardware/tools/avr/bin/avr-g++ -c -g -Os -w -fno-exceptions -ffunction-sections -fdata-sections -mmcu=atmega328p -DF_CPU=16000000L -MMD -DUSB_VID=null -DUSB_PID=null -DARDUINO=105 -I/opt/arduino-1.0.5/hardware/arduino/cores/arduino -I/opt/arduino-1.0.5/hardware/arduino/variants/standard $< -o $@

bldc_driver.elf: bldc_driver.o core.a Makefile
	/opt/arduino-1.0.5/hardware/tools/avr/bin/avr-gcc -Os -Wl,--gc-sections  -mmcu=atmega328p  -o  bldc_driver.elf  bldc_driver.o  core.a -lm

bldc_driver.hex: bldc_driver.elf Makefile
	/opt/arduino-1.0.5/hardware/tools/avr/bin/avr-objcopy -O ihex -R .eeprom $< $@

.PHONY: prog
prog: bldc_driver.hex
	/opt/arduino-1.0.5/hardware/tools/avrdude -b57600 -C/opt/arduino-1.0.5/hardware/tools/avrdude.conf -patmega328 -cstk500v1 -P/dev/ttyUSB0 -Uefuse:w:0x05:m -Uhfuse:w:0xde:m -Ulfuse:w:0xff:m -Uflash:w:bldc_driver.hex:i -v -v
