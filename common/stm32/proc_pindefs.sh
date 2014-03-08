#!/bin/bash

tail STM32F407_pin_defs.txt -n +2 | awk '
    BEGIN { y = 0 }
    { if ($1 != "-") { print "<pin name=\""$7"\" x=\"0\" y=\"-"y"\" length=\"middle\"/>" ; y += 2.54 } }
'
tail STM32F407_pin_defs.txt -n +2 | awk '
    BEGIN { y = 0 }
    { if ($1 != "-") print "<connect gate=\"G$1\" pin=\""$7"\" pad=\""$1"\"/>"}
'
