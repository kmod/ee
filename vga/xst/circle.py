import random
import threading
import time

import serial # easy_install pyserial

import sys
sys.path.insert(0, "../../bc")


# Baud rates linux seems to support:
# 0 50 75 110 134 150 200 300 600 1200 1800 2400 4800 9600 19200 38400 57600 115200 230400 460800 576000 921600 1152000 1500000 3000000...

ser = serial.Serial("/dev/ttyUSB0", 3000000, timeout=4)

_buf = []
def write(s):
    global _buf
    _buf.append(s)
    if len(_buf) > 100:
        ser.write(''.join(_buf))
        _buf = []

while True:
    CX = random.randrange(20, 140)
    CY = random.randrange(20, 100)
    CC = random.randrange(0, 256)
    CRO = random.randrange(10, 25)
    CRI = random.randrange(-2, CRO-2)
    CRI = CRO - 5
    # CRI = 1
    l = []
    miny = max(0, CY - CRO - 2)
    maxy = max(0, CY + CRO + 2)
    minx = max(0, CX - CRO - 2)
    maxx = max(0, CX + CRO + 2)
    for y in xrange(miny, maxy):
        for x in xrange(minx, maxx):
            d = (x - CX)**2 + (y - CY)**2 
            if (CRI-0.5)**2 < d < (CRO+0.5)**2:
                write(chr(CC) + chr(x) + chr(y) + chr(0))
            elif (CRO+0.5)**2 < d < (CRO+1.5)**2:
                write(chr(0) + chr(x) + chr(y) + chr(0))
            elif (CRI-1.5)**2 < d < (CRI-0.5)**2:
                write(chr(0) + chr(x) + chr(y) + chr(0))
                # time.sleep(0.0001)
