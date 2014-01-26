import os
import Queue
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

        self.ser = serial.Serial("/dev/ttyUSB0", br)
        self.on_read = []
        self.q = Queue.Queue()

        # Note: signal on board is !RTS
        self.ser.setRTS(0)
        time.sleep(0.100)
        self.ser.setRTS(1)

        self._started = threading.Event()

        t = threading.Thread(target=self.read_thread)
        t.setDaemon(True)
        t.start()

        print "Waiting for board to start..."
        while not self._started.isSet():
            # Give the atmega some time to exit the bootloader,
            # and gives the magic word
            time.sleep(.1)
        print "Connected"

    def read_thread(self):
        try:
            while True:
                try:
                    self.ser.timeout = 0
                    s = self.ser.read(1024)
                    while not s:
                        self.ser.timeout = 1
                        s = self.ser.read(1)
                    for c in s:
                        self.bytes_read += 1
                        if not self._started.isSet():
                            assert c == chr(0xae), repr(c)
                            self._started.set()
                        else:
                            for callback in self.on_read:
                                callback(c)
                            self.q.put(c)
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

if __name__ == "__main__":
    C = Controller()
    C.ser.close()
