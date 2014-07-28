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
        # self.q = Queue.Queue()

        # Note: signal on board is !RTS
        self.ser.setRTS(0)
        time.sleep(0.100)

        self.ser.timeout = 0
        while True:
            s = self.ser.read(1024)
            if not s:
                break
            print "Got %d junk bytes from the serial buffer" % len(s)
        self.ser.timeout = None
        self.ser.setRTS(1)

        self.bytes_incoming = 0
        self.lock = threading.Lock()

        # t = threading.Thread(target=self.read_thread)
        # t.setDaemon(True)
        # t.start()

        print "Waiting for board to start..."
        self.ser.timeout = None
        def test(check):
            c = self.ser.read(1)
            assert c == check, (c, check)
        test('\xaf')
        test('\x03')

        test('\x10')
        test('\x00')
        test('\x30')
        test('\x01')
        test('\x30')
        test('\x81')

        self.ser.write('\x30\x81')
        self.ser.flush()

        test('\x00')
        test('\x00')
        print "Connected"


    def add_incoming(self, nbytes):
        while self.bytes_incoming > 4000:
            time.sleep(0.0001)
        with self.lock:
            self.bytes_incoming += nbytes

    def get(self):
        with self.lock:
            self.bytes_incoming -= 1
        return self.ser.read(1)

    def assertDone(self):
        self.ser.timeout = 0
        assert not self.ser.read(1)
        self.ser.timeout = None


    def flush(self):
        self.ser.flush()

    def _write(self, s):
        self.bytes_written += len(s)
        self.ser.write(s)
        if self.autoflush:
            self.ser.flush()
        # time.sleep(5)
