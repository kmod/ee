# Simplified from http://www.xess.com/appnotes/makefile.php

ISE_BIN=/mnt/hgfs/M/Xilinx_linux/14.6/ISE_DS/ISE/bin/lin64

CPLDFIT_FLAGS=
HPREP6_FLAGS=
NGDBUILD_FLAGS=

SOURCES=$(wildcard *.v) $(wildcard ipcoredir/*.v) $(wildcard src/*.v)
UCFS=$(wildcard *.ucf)

OPTLEVEL=std # options are "high" and "std"

fpga.ngc: $(SOURCES)
	mkdir -p xst/projnav.tmp
	$(ISE_BIN)/xst -intstyle ise -ifn fpga.xst -ofn fpga_syn.log
%.ngd: %.ngc $(UCFS)
	$(ISE_BIN)/ngdbuild -intstyle ise -dd _ngo -sd ipcore_dir -nt timestamp $(patsubst %,-uc %,$(UCFS)) -p xc6slx16-csg324-3 fpga.ngc fpga.ngd
%_map.ncd: %.ngd
	$(ISE_BIN)/map -intstyle ise -p xc6slx16-csg324-3 -w -logic_opt off -ol $(OPTLEVEL) -t 1 -xt 0 -register_duplication off -r 4 -global_opt off -mt off -ir off -pr off -lc off -power off -o fpga_map.ncd fpga.ngd fpga.pcf
%.ncd: %_map.ncd
	$(ISE_BIN)/par -w -intstyle ise -ol $(OPTLEVEL) -mt off fpga_map.ncd fpga.ncd fpga.pcf
%.bit: %.ncd
	$(ISE_BIN)/bitgen -intstyle ise -f fpga.ut fpga.ncd

.PHONY: prog
prog: fpga.bit
	djtgcfg prog -d Nexys3 -i 0 -f fpga.bit

