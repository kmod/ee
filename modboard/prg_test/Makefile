include Makefile.gen

ISE_BIN := /opt/Xilinx/14.7/ISE_DS/ISE/bin/lin64

Makefile.gen: prg_test.mb $(wildcard ../programming/*.py)
	../programming/gen.py prg_test.mb $@
