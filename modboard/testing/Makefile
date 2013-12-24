# Simplified from http://www.xess.com/appnotes/makefile.php

ISE_BIN=/opt/Xilinx/14.7/ISE_DS/ISE/bin/lin64

CPLDFIT_FLAGS=
HPREP6_FLAGS=
NGDBUILD_FLAGS=

SOURCES=$(wildcard *.v)
UCFS=$(wildcard *.ucf)

SIZE=64a
SPEED=7
PACKAGE=vq100
PART=xc2c$(SIZE)-$(SPEED)-$(PACKAGE)

.PHONY: all
all: cpld.svf

xst/projnav.tmp:
	mkdir -p $@

cpld.ngc: $(SOURCES) xst/projnav.tmp
		$(ISE_BIN)/xst -intstyle ise -ifn cpld.xst
%.ngd: %.ngc $(UCFS)
		$(ISE_BIN)/ngdbuild $(NGDBUILD_FLAGS) $(patsubst %,-uc %,$(UCFS)) -p $(PART) $*.ngc $*.ngd
%.vm6: %.ngd
		$(ISE_BIN)/cpldfit $(CPLDFIT_FLAGS) -p $(PART) $*.ngd
%.jed: %.vm6
		$(ISE_BIN)/hprep6 $(HPREP6_FLAGS) -i $*.vm6

cpld.svf: cpld.jed impact.batch
	$(ISE_BIN)/impact -batch impact.batch

.PHONY: prog
prog: cpld.svf
	python /home/kmod/Dropbox/ee/jtag/svf_reader/svf_reader.py cpld.svf

