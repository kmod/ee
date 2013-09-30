import random
import threading
import time

import serial # easy_install pyserial

import sys
sys.path.insert(0, "../../bc")


# Baud rates linux seems to support:
# 0 50 75 110 134 150 200 300 600 1200 1800 2400 4800 9600 19200 38400 57600 115200 230400 460800 576000 921600 1152000 1500000 3000000...

ser = serial.Serial("/dev/ttyUSB0", 1000000, timeout=4)

while True:
    CX = random.randrange(20, 140)
    CY = random.randrange(20, 100)
    CC = random.randrange(0, 256)
    CRO = random.randrange(10, 25)
    CRI = random.randrange(5, CRO)
    CRI = CRO - 5
    for y in xrange(120):
        for x in xrange(160):
            d = (x - CX)**2 + (y - CY)**2 
            if (CRI-0.5)**2 < d < (CRO+0.5)**2:
                ser.write(chr(CC) + chr(x) + chr(y) + chr(0))
            elif (CRO+0.5)**2 < d < (CRO+1.5)**2:
                ser.write(chr(0) + chr(x) + chr(y) + chr(0))
            elif (CRI-1.5)**2 < d < (CRI-0.5)**2:
                ser.write(chr(0) + chr(x) + chr(y) + chr(0))
                # time.sleep(0.0001)
