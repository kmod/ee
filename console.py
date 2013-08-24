import serial
import sys
import time

br = 9600
ser = serial.Serial("/dev/ttyUSB0", br, timeout=1)
while True:
    try:
        sys.stdout.write(ser.read(1))
    except OSError:
        print
        print "OSError, assuming it's being programmed, waiting"
        time.sleep(6)
        print "starting"
