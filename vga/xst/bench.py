import threading
import time

import serial # easy_install pyserial

import sys
sys.path.insert(0, "../../bc")


# Baud rates linux seems to support:
# 0 50 75 110 134 150 200 300 600 1200 1800 2400 4800 9600 19200 38400 57600 115200 230400 460800 576000 921600 1152000 1500000 3000000...

ser = serial.Serial("/dev/ttyUSB0", 3000000, timeout=4)

# ser.write('\0'*3)

def read_thread():
    while True:
        c = ser.read(1)
        if c:
            print repr(c)

t = threading.Thread(target=read_thread)
t.setDaemon(True)
t.start()

_buf = []
def write(s):
    global _buf
    _buf.append(s)
    if len(_buf) >= 100:
        # start = time.time()
        ser.write(''.join(_buf))
        # print time.time() - start
        _buf = []

start = time.time()

i = 0
# screen is 160 x 120
while True:
    # print i
    x = i % 160
    y = (i/160) % 120
    c = (x + y + (i / 160 / 120)) % 256
    s = chr(c) + chr(x) + chr(y) + chr(88)
    # print map(hex, map(ord, s))
    write(s)
    # for c in s:
        # ser.write(c)
        # time.sleep(.001)
    # ser.write(chr(i))
    i += 1
    if i % 100000 == 0:
        print "%.1f px/s" % (i / (time.time() - start))
