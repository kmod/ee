include Makefile.gen

include fpga_vga/Makefile

ISE_BIN := /opt/Xilinx/14.7/ISE_DS/ISE/bin/lin64
ifeq ($(wildcard $(ISE_BIN)),)
ISE_BIN := /opt/Xilinx/14.6/ISE_DS/ISE/bin/lin64
endif


PROGRAMMING_DIR := ../../../modboard/programming

Makefile.gen: main.mb $(wildcard $(PROGRAMMING_DIR)/*.py)
	$(PROGRAMMING_DIR)/gen.py main.mb $@

.PHONY: clean
clean:
	- rm Makefile.gen
	- rm -rfv *.mbbuild

.PHONY: prog_fpga
prog_fpga: prog_main_vga.fpga_noverify
# prog_fpga: prog_main_vga.fpga
