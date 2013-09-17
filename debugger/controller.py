import os
import serial # pip install pyserial
import sys
import threading
import time

class Controller(object):
    def __init__(self, br=115200):
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

    def _write(self, s):
        # print repr(s)
        self.ser.write(s)
        self.ser.flush()

    def pinMode(self, port, mode):
        if mode in (0, 1):
            pass
        elif mode.lower().startswith("in"):
            mode = 0
        elif mode.lower().startswith("out"):
            mode = 1
        else:
            mode = int(mode)
            assert mode in (0,1), mode
        self._write("m" + chr(port) + chr(mode))

    def digitalWrite(self, port, value):
        self._write("s" + chr(port) + chr(value))

    def digitalRead(self, port):
        self._write("r" + chr(port))

    def shiftIn(self, port):
        self._write("i" + chr(port))

    def readShiftReg(self):
        self._write("v")
