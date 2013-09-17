import os
import serial # pip install pyserial
import sys
import threading
import time

class Controller(object):
    def __init__(self):
        br = 115200
        self.ser = serial.Serial("/dev/ttyUSB0", br, timeout=1)
        self.on_read = []

        t = threading.Thread(target=self.read_thread)
        t.setDaemon(True)
        t.start()

    def read_thread(self):
        try:
            while True:
                try:
                    c = self.ser.read(1)
                    if c:
                        for callback in self.on_read:
                            callback(c)
                except OSError:
                    print
                    print "OSError, assuming it's being programmed, waiting"
                    time.sleep(6)
                    print "starting"
        except:
            os._exit(1)
            raise

    def pinMode(self, port, mode):
        if mode.lower().startswith("in"):
            mode = 0
        elif mode.lower().startswith("out"):
            mode = 1
        else:
            mode = int(mode)
            assert mode in (0,1), mode
        self.ser.write("m" + chr(port) + chr(mode))
        self.ser.flush()

    def digitalWrite(self, port, value):
        self.ser.write("s" + chr(port) + chr(value))
        self.ser.flush()

    def digitalRead(self, port):
        self.ser.write("r" + chr(port))
        self.ser.flush()

    def shiftIn(self, port):
        self.ser.write("i" + chr(port))
        self.ser.flush()

    def readShiftReg(self):
        self.ser.write("v")
        self.ser.flush()
