# Simplified from http://www.xess.com/appnotes/makefile.php

ISE_BIN=/opt/Xilinx/14.6/ISE_DS/ISE/bin/lin64

CPLDFIT_FLAGS=
HPREP6_FLAGS=
NGDBUILD_FLAGS=

SOURCES=$(wildcard *.v)
UCFS=$(wildcard *.ucf)

PART=xc2c32a-4-vq44

cpld.ngc: $(SOURCES)
		$(ISE_BIN)/xst -ifn cpld.xst
%.ngd: %.ngc $(UCFS)
		$(ISE_BIN)/ngdbuild $(NGDBUILD_FLAGS) -p $(PART) $*.ngc $*.ngd
%.vm6: %.ngd
		$(ISE_BIN)/cpldfit $(CPLDFIT_FLAGS) -p $(PART) $*.ngd
%.jed: %.vm6
		$(ISE_BIN)/hprep6 $(HPREP6_FLAGS) -i $*.vm6

cpld.svf: cpld.jed impact.batch
	$(ISE_BIN)/impact -batch impact.batch

.PHONY: prog
prog: cpld.svf
	time python /home/kmod/Dropbox/ee/jtag/svf_reader.py cpld.svf
