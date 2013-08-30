import serial
import sys
import time

br = 115200
ser = serial.Serial("/dev/ttyUSB1", br, timeout=1)
while True:
    try:
        c = ser.read(1)
        if c:
            if c == '\0':
                print
            else:
                print str(ord(c)),
    except OSError:
        print
        print "OSError, assuming it's being programmed, waiting"
        time.sleep(5)
        print "starting"
