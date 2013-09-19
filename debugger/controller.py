import os
import serial # pip install pyserial
import sys
import threading
import time
import traceback

class Controller(object):
    def __init__(self, br=500000, autoflush=True):
        self.autoflush = autoflush
        self.bytes_read = 0
        self.bytes_written = 0

        self.ser = serial.Serial("/dev/ttyUSB0", br, timeout=1)
        self.on_read = []

        self._started = threading.Event()

        t = threading.Thread(target=self.read_thread)
        t.setDaemon(True)
        t.start()

        while not self._started.isSet():
            # Give the atmega some time to exit the bootloader,
            # and wait until it responds to a command
            self.readShiftReg()
            time.sleep(.1)

    def read_thread(self):
        try:
            while True:
                try:
                    c = self.ser.read(1)
                    if c:
                        self.bytes_read += 1
                        if not self._started.isSet():
                            self._started.set()
                        else:
                            for callback in self.on_read:
                                callback(c)
                except OSError:
                    print
                    print "OSError, assuming it's being programmed, waiting"
                    time.sleep(6)
                    print "starting"
        except:
            traceback.print_exc()
            os._exit(1)
            raise

    def flush(self):
        self.ser.flush()

    def _write(self, s):
        self.bytes_written += len(s)
        # print repr(s)
        self.ser.write(s)
        if self.autoflush:
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
        assert value in (0,1)
        self._write(chr(0x80 | (value << 6) | port))
        # self._write("s" + chr(port) + chr(value))

    def digitalRead(self, port):
        self._write("r" + chr(port))

    def shiftIn(self, port):
        self._write("i" + chr(port))

    def readShiftReg(self):
        self._write("v")
