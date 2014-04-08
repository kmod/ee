CWD := $(dir $(lastword $(MAKEFILE_LIST)))

$(CWD)main.syr: $(CWD)main.v
	cd $(CWD); $(ISE_BIN)/xst -intstyle ise -ifn "main.xst" -ofn "main.syr"
	touch $(CWD)did_xst

$(CWD)main.ngd: $(CWD)main.syr $(CWD)pins.ucf
	cd $(CWD); $(ISE_BIN)/ngdbuild -intstyle ise -dd _ngo -nt timestamp -uc pins.ucf -p xc6slx9-tqg144-3 "main.ngc" main.ngd
	touch $(CWD)did_ngdbuild

$(CWD)main_map.ncd: $(CWD)main.ngd
	cd $(CWD); $(ISE_BIN)/map -intstyle ise -p xc6slx9-tqg144-3 -w -logic_opt off -ol high -t 1 -xt 0 -register_duplication off -r 4 -global_opt off -mt off -ir off -pr off -lc off -power off -o main_map.ncd main.ngd main.pcf
	touch $(CWD)did_map

$(CWD)main.ncd: $(CWD)main_map.ncd
	cd $(CWD); $(ISE_BIN)/par -w -intstyle ise -ol high -mt off main_map.ncd main.ncd main.pcf
	touch $(CWD)did_par

$(CWD)main.bit: $(CWD)main.ncd
	cd $(CWD); $(ISE_BIN)/bitgen -intstyle ise -f main.ut main.ncd -m
	touch $(CWD)did_bitgen
