import serial # pip install pyserial
import threading
import time

print_lock = threading.Lock()

class BinaryStream(object):
    def __init__(self, ser):
        self.ser = ser

        self.ser.timeout = None
        self.cur_timeout = None

    def read(self, nbytes, timeout=None):
        if timeout is not self.cur_timeout and timeout != self.cur_timeout:
            # This looks like a simple attribute set, but it's not:
            self.cur_timeout = self.ser.timeout = timeout
        return self.ser.read(nbytes)

    def write(self, data):
        # print "Writing %d bytes:" % (len(data),), repr(data)
        if self.cur_timeout is not None:
            self.cur_timeout = self.ser.timeout = None
        self.ser.write(data)

    def flush(self):
        self.ser.flush()

    def readUInt(self, nbytes):
        data = self.read(nbytes)
        r = 0
        for i in xrange(nbytes):
            r = (r << 8) + ord(data[i])
        return r

    def writeUInt(self, nbytes, val):
        assert 0 <= val < (256 ** nbytes)
        assert nbytes in (1, 2, 4, 8), nbytes

        if nbytes == 1:
            self.write(chr(val))
        elif nbytes == 2:
            self.write(chr(val >> 8))
            self.write(chr(val & 0xff))
        else:
            raise Exception(nbytes)

class ControllerHub(object):
    def __init__(self, br):
        self.baud_rate = br
        self.ser = serial.Serial("/dev/ttyUSB0", br)

        self.stream = BinaryStream(self.ser)

        self.supported_endpoints = set()
        self._open_endpoint = None

        # Note: signal on board is !RTS
        print "Resetting board..."
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

        print "Waiting for board to start up..."
        start_byte = self.ser.read(1)
        while start_byte != '\xaf':
            assert start_byte == '\xff', repr(start_byte)
            start_byte = self.ser.read(1)

        assert start_byte == '\xaf', repr(start_byte)

        num_endpoints = self.stream.readUInt(1)
        assert 1 <= num_endpoints < 128
        for i in xrange(num_endpoints):
            endpoint_id = self.stream.readUInt(2)
            assert 0x1000 <= endpoint_id < 0x8000

            self.supported_endpoints.add(endpoint_id)

        print "Connected to hub, %d endpoints listed" % num_endpoints

    def openEndpoint(self, endpoint_id):
        assert self._open_endpoint == None
        assert endpoint_id in self.supported_endpoints, self.supported_endpoints

        self.stream.writeUInt(2, endpoint_id)
        self.stream.flush()
        s = self.stream.read(2)
        assert s == '\x00\x00', repr(s)
        self._open_endpoint = endpoint_id

        return self.stream

